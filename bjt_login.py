import base64
import json
import time
from hashlib import md5

import ddddocr
import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

# BJT_PHONE和BJT_PWD现在通过UserConfig传递，不再从config导入
from utils import get_url_params, logger, AppriseNotifier

ocr = ddddocr.DdddOcr(show_ad=False)
ocr.set_ranges("0123456789")


class BeijingTong(object):
    def __init__(self, phone_num="", pwd="", notify_urls=None):
        self.session = requests.Session()
        self.phone_num = phone_num
        self.pwd = pwd
        self.redirect_url = None
        # 使用Apprise推送通知
        self.bot = AppriseNotifier(notify_urls)

    def get_pubkey(self):
        response = self.session.get(
            url="https://bjt.beijing.gov.cn/renzheng/open/m/login/goUserLogin?client_id=100100000343&redirect_uri=https://bjjj.jtgl.beijing.gov.cn/uc/ucfront/userauth&response_type=code&scope=user_info&state=100100004153",
            allow_redirects=False,
        )

        if response.status_code != 302:
            raise ValueError("无法获取pubKey")
        pubKey = get_url_params(response.headers.get("Location", ""), "pubKey")

        # 如果仍然没有获取到，抛出错误
        if not pubKey:
            raise ValueError("无法获取pubKey")
        return pubKey

    def get_captcha(self):
        timestamp = int(time.time() * 1000)  # 生成动态时间戳
        resp = self.session.get(
            url=f"https://bjt.beijing.gov.cn/renzheng/common/generateCaptcha?{timestamp}",
            stream=True,  # 添加流式传输模式
        )
        if resp.status_code == 200:
            result = ocr.classification(resp.content)
            return result
        else:
            raise ValueError("无法获取验证码")

    def login(self):

        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            self.session = requests.Session()
            # 修改验证码请求部分
            try:
                pubKey = self.get_pubkey()
                encrypted_data = self.encrypt_data(self.phone_num, self.pwd, pubKey)
                captcha = self.get_captcha()
                resp = self.session.post(
                    "https://bjt.beijing.gov.cn/renzheng/inner/m/login/doUserLoginByPwd",
                    data={"encryptData": encrypted_data, "captcha": captcha},
                )
                auth_url = None
                if resp.status_code == 200:
                    json_data = resp.json()
                    code = json_data.get("meta", {}).get("code") 
                    if code == "5019":
                        logger.error(f"登陆失败, 重试次数: {retry_count}，错误信息: {json_data.get('meta', {}).get('message')}")
                        self.bot.send("进京证", f"登陆失败, 重试次数: {retry_count}，错误信息: {json_data.get('meta', {}).get('message')}")
                        return None
                    elif code == "5016":
                        self.bot.send("进京证", f"登陆失败, 重试次数: {retry_count}，错误信息: {json_data.get('meta', {}).get('message')}")
                        raise Exception(f"{json_data.get('meta', {}).get('message')}")
                    auth_url = json_data.get("data", {}).get("redirectUrl", "")
                else:
                    logger.error(f"登陆失败, 重试次数: {retry_count}，错误信息: {resp.text}")
                return auth_url
            except Exception as e:
                logger.error(f"登陆失败, 重试次数: {retry_count}，错误信息: {e}")
                retry_count += 1
                continue
        
        return None

    def encrypt_data(self, phone_num, pwd, public_key):
        data = {
            "userIdentity": phone_num,
            "resetFlag": False,
            "encryptedPwd": md5(pwd.encode("utf-8")).hexdigest().lower(),
        }

        pem_public_key = (
            f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
        )

        # 保持后续加密逻辑不变
        json_str = json.dumps(data, separators=(",", ":"))
        rsa_key = RSA.import_key(pem_public_key)
        cipher = PKCS1_v1_5.new(rsa_key)

        encrypted_chunks = []
        chunk_size = 214
        data_bytes = json_str.encode("utf-8")

        for i in range(0, len(data_bytes), chunk_size):
            chunk = data_bytes[i : i + chunk_size]
            encrypted_chunk = cipher.encrypt(chunk)
            encrypted_chunks.append(base64.b64encode(encrypted_chunk).decode("utf-8"))

        return ",".join(encrypted_chunks)


def get_token(auth_url):
    resp = requests.get(auth_url, allow_redirects=False)
    if resp.status_code == 302:
        return get_url_params(resp.headers.get("Location", ""), "token")
    else:
        raise ValueError("无法获取token")





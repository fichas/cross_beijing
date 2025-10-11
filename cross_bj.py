import sys
import json
import requests
from datetime import datetime, timedelta
from loguru import logger
from utils import days_between_dates, get_future_date, bot, logger
from config import URL, AUTH

STATE_LIST_URL = f"https://{URL}/pro/applyRecordController/stateList"
INSERT_APPLY_RECORD_URL = (
    f"https://{URL}/pro/applyRecordController/insertApplyRecord"
)

def request(url, data) -> dict:
    payload = json.dumps(data)
    headers = {"Authorization": AUTH, "Content-Type": "application/json"}
    try:
        res = requests.post(url, headers=headers, data=payload)
        result = res.json()
        if result["code"] != 200:
            logger.error(
                f"请求失败，状态码: {result['code']}，错误信息: {result['msg']}"
            )
            sys.exit(1)
    except Exception as e:
        logger.error(f"请求失败，错误信息: {e}")
        bot.send("进京证续签失败", f"请求失败，错误信息: {e}")
        sys.exit(1)
    return result

class CrossBJ:
    def __init__(self):
        self.state_data = None

    def get_state_data(self):
        self.state_data = request(STATE_LIST_URL, data={})
        return self.state_data

    def parse_state_data(self):
        if self.state_data == None:
            self.get_state_data()
        data = (
            self.state_data["data"]["bzclxx"][0]["ecbzxx"][0]
            if self.state_data["data"]["bzclxx"][0]["ecbzxx"]
            else self.state_data["data"]["bzclxx"][0]["bzxx"][0]
        )
        return data

    def need_renew(self):
        data = self.parse_state_data()
        today = datetime.now().strftime("%Y-%m-%d")

        days_difference = days_between_dates(
            today, data["yxqz"]
        )  # 当前日期与有效期之间的天数
        if data["blztmc"] in ["审核通过(生效中)", "审核中", "审核通过(待生效)"]:
            if data["blztmc"] == "审核通过(生效中)" and days_difference <= 1:
                return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                return None
        return today

    def exec_renew(self, jjzzl="六环内"):
        jjrq = self.need_renew()
    
        if jjrq is None:
            return None
        data = self.parse_state_data()
        
        payload = {
            "sqdzgdjd": "116.4",  # 进京经度
            "sqdzgdwd": "39.9",  # 进京纬度
            "sqdzbdjd": "116.273348",  # 进京目的地经度
            "sqdzbdwd": "40.040219",  # 进京目的地纬度
            "txrxx": [],
            "hpzl": data["hpzl"],  # 车牌类型
            "jjdq": "010",  # 进京目的地地区
            "jjmd": "06",  # 进京目的地
            "jjzzl": "01" if jjzzl == "六环内" else "02",  # 进京证类型
            "jjlk": "00606",  # 进京路况
            "jjmdmc": "其它",  # 进京目的地名称
            "jjlkmc": "其他道路",  # 进京路况名称
            "applyIdOld": data["applyId"],  # 续办申请id
            "jjrq": jjrq,  # 进京日期(申请生效日期)
            "vId": data["vId"],  # 车辆识别代号
            "jsrxm": data["jsrxm"],  # 车主姓名
            "jszh": data["jszh"],  # 车主身份证号
            "hphm": data["hphm"],  # 车牌号
            "sfzj": 1,
            "xxdz": "北京动物园",
        }
        return request(INSERT_APPLY_RECORD_URL, payload)
    

def main():
    cross_bj = CrossBJ()
    resp = cross_bj.exec_renew()
    if resp is None:
        msg = "无需续签"
    else:
        msg = "续签成功" if resp["code"] == 200 else "续签失败"
    cross_bj.get_state_data()
    data = cross_bj.parse_state_data()
    

    yxqs = data["yxqs"] # 有效期开始时间    
    yxqz = data["yxqz"] if data["yxqz"] else get_future_date(yxqs, 6) # 有效期结束时间
    blztmc = data["blztmc"] # 状态
    jjzzlmc = data["jjzzlmc"] # 进京证类型
    sqsj = data["sqsj"] # 申请时间
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 执行时间
    title = f"进京证{msg}: {yxqs[5:]}~{yxqz[5:]}" # 标题    
    msg = f"{msg}\n状态: {blztmc}\n有效期: {yxqs}至{yxqz}\n类型: {jjzzlmc}\n申请时间: {sqsj}\n执行时间: {formatted_time}" # 消息
    logger.info(msg)
    bot.send(title, msg)


if __name__ == "__main__":
    main()

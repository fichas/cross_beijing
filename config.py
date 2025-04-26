import os
import dotenv


dotenv.load_dotenv()


# 从环境变量读取配置
URL = os.environ.get("URL")
AUTH = os.environ.get("AUTH")

BARK_KEY = os.environ.get("BARK_KEY")

BJT_PHONE = os.environ.get("BJT_PHONE")
BJT_PWD = os.environ.get("BJT_PWD")

print(URL, AUTH, BARK_KEY, BJT_PHONE, BJT_PWD)
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from urllib.parse import urlparse

import requests
from loguru import logger


class SendMessage(ABC):
    @abstractmethod
    def send(self, title, msg):
        pass


class Bark(SendMessage):
    def __init__(self, key=""):
        self.key = key

    def send(self, title, msg):
        if self.key:
            requests.post(
                f"https://api.day.app/{self.key}/{title}/{msg}?isArchive=1&group=进京证"
            )
        else:
            print("未配置推送密钥，不发送推送")


def get_url_params(url, key):
    """原始参数值获取"""
    parsed = urlparse(url)

    for param in parsed.query.split("&"):
        if "=" in param:
            k, v = param.split("=", 1)  # 只分割第一个等号
            if k == key:
                return v  # 直接返回原始值

    # 处理片段部分
    if parsed.fragment:
        for param in parsed.fragment.split("&"):
            if "=" in param:
                k, v = param.split("=", 1)
                if k == key:
                    return v

    return None


def days_between_dates(date1_str, date2_str):
    try:
        date1 = datetime.strptime(date1_str, "%Y-%m-%d")
        date2 = datetime.strptime(date2_str, "%Y-%m-%d")
        time_difference = date2 - date1
        days_difference = time_difference.days + 1
        return days_difference
    except Exception as error:
        print("计算两个日期差失败:", error)
        return 0


def get_future_date(date_str, days):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    future_date = date_obj + timedelta(days=days)
    return future_date.strftime("%Y-%m-%d")


from datetime import datetime, timedelta
from loguru import logger
from utils import  get_future_date, Bark, logger
from config import get_user_configs
from jtgl_manager import ApplyRecordManager, VehicleManager, UserManager
from model import NewApplyForm, RecordInfo, StateData
from config import UserConfig


class CrossBJ:
    def __init__(self, user: UserConfig):
        self.apply_manager = ApplyRecordManager(user.auth)
        self.vehicle_manager = VehicleManager(user.auth)
        self.user_manager = UserManager(user.auth)
        self.state_data: StateData | None = None
        self.user = user
        self.bot = Bark(user.bark_token)

    def get_state_data(self) -> StateData:
        """获取状态数据"""
        if self.state_data is not None:
            return self.state_data
        self.state_data = self.apply_manager.get_state_data()
        return self.state_data

    def get_latest_record(self) -> RecordInfo:
        """解析状态数据，获取最新的申请记录"""
        if self.state_data is None:
            self.get_state_data()
        # 使用新的数据模型快速获取记录
        if self.state_data is None:
            raise Exception(f"[{self.user.name}]没有找到状态数据")
        record = self.state_data.get_latest_record()
        if record is None:
            logger.info(f"[{self.user.name}]没有找到有效的申请记录")

        return record

    def need_apply(self):
        """检查是否需要申请进京证，返回需要申请的日期，如果不需要申请则返回None"""
        try:
            record = self.get_latest_record()
            today = datetime.now().strftime("%Y-%m-%d")
            if record is None:
                # 新车 没有任何申请记录 直接返回今天
                return today

            # 计算剩余天数
            remaining_days = record.calc_remaining_days()
            status = record.get_status_description()
            # 检查状态和剩余天数
            if status in ["审核通过(生效中)", "审核中", "审核通过(待生效)"]:
                if status == "审核通过(生效中)" and remaining_days <= 1:
                    # 审核通过(生效中) 且剩余天数小于等于1天 提前申请明天的进京证
                    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    return None
            # 其他情况 直接返回今天，审核失败这种就需要重新触发重新申请
            return today
        except Exception as e:
            logger.error(f"[{self.user.name}]检查续签需求失败: {e}")
            return None

    def exec_apply(self, form_type="六环内"):
        """执行续签操作"""
        apply_date = self.need_apply()

        if apply_date is None:
            return None

        try:
            # 获取车辆和用户信息
            vehicles = self.vehicle_manager.list_vehicles()
            user_info = self.user_manager.get_user_info()

            if not vehicles:
                raise Exception(f"[{self.user.name}]没有找到车辆信息")

            # 创建申请表单
            apply_form = NewApplyForm(
                vehicle_info=vehicles[0],
                user_info=user_info,
                apply_date=apply_date,
                destination="北京动物园",
                form_type=form_type,
            )

            # 提交申请
            return self.apply_manager.do_apply_record(apply_form)

        except Exception as e:
            logger.error(f"[{self.user.name}]续签执行失败: {e}")
            self.bot.send("进京证续签失败", f"续签执行失败: {e}")
            return None

    def get_current_status(self):
        """获取当前状态信息"""
        try:
            # 使用新的数据模型快速获取信息
            record = self.get_latest_record()
            if record is None:
                raise Exception("没有找到有效的申请记录")

            return {
                "start_date": record.yxqs,
                "end_date": (
                    record.yxqz if record.yxqz else get_future_date(record.yxqs, 6)
                ),
                "status": record.blztmc,
                "apply_type": record.jjzzlmc,
                "apply_date": record.sqsj,
                "remaining_days": record.calc_remaining_days(),
                "quota_info": self.state_data.get_quota_info(),
                "can_apply": self.state_data.can_apply(),
            }
        except Exception as e:
            logger.error(f"获取状态信息失败: {e}")
            return None

    def exec(self):
        resp = self.exec_apply()
        if resp is None:
            msg = "无需续签"
        else:
            msg = "续签成功" if resp["code"] == 200 else "续签失败"
        status = self.get_current_status()
        if status is None:
            logger.error(f"[{self.user.name}]无法获取状态信息")
            return

        # 格式化信息
        start_date = status["start_date"]
        end_date = status["end_date"]
        status_text = status["status"]
        apply_type = status["apply_type"]
        apply_date = status["apply_date"]
        remaining_days = status["remaining_days"]
        quota_info = status["quota_info"]

        formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 构建消息
        title = f"进京证{msg}: {start_date[5:]}~{end_date[5:]}"
        msg_content = f"{msg}\n"
        msg_content += f"状态: {status_text}\n"
        msg_content += f"有效期: {start_date}至{end_date}\n"
        msg_content += f"剩余天数: {remaining_days}\n"
        msg_content += f"类型: {apply_type}\n"
        msg_content += f"申请时间: {apply_date}\n"
        msg_content += f"执行时间: {formatted_time}\n"
        if quota_info:
            msg_content += f"剩余申请次数: {quota_info.get('remaining_times', 0)}\n"

        logger.info(f"[{self.user.name}] {msg_content}")
        self.bot.send(title, msg_content)


def main():
    user_configs = get_user_configs()
    for user in user_configs:
        logger.info(f"[{user.name}]开始续签")
        try:
            cross_bj = CrossBJ(user)
            cross_bj.exec()
        except Exception as e:
            logger.error(f"[{user.name}]续签失败: {e}")
    logger.info("所有用户续签完成")

if __name__ == "__main__":
    main()

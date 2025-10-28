from tarfile import data_filter
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from constant import LICENSE_PLATE_TYPE_MAP, VEHICLE_TYPE_MAP
from datetime import datetime

from utils import days_between_dates

# 通用配置，允许 None 值
class AllowNoneConfig:
    model_config = ConfigDict(extra='ignore', validate_assignment=True)

class VehicleInfo(BaseModel, AllowNoneConfig):
    """车辆信息模型"""
    license_plate_type: str = Field(default="02", description="号牌种类代码(默认小型新能源汽车)")
    license_number: str = Field(default="", description="号牌号码")
    vehicle_type: str = Field(default="01", description="车辆类型代码（默认客车）")
    engine_number: str = Field(default="", description="发动机号/电机号")
    brand_model: str = Field(default="", description="品牌型号")
    registration_date: str = Field(default="", description="注册时间")
    # ================================
    collection_date: Optional[str] = Field(default=None, description="采集时间")
    enable_status: int = Field(default=1, description="启用状态")
    registration_channel_key: Optional[str] = Field(default=None, description="注册渠道标识")
    identity_number: Optional[str] = Field(default=None, description="身份证明号码")
    kz3: str = Field(default="", description="扩展字段3")
    kz5: Optional[str] = Field(default=None, description="扩展字段5")
    vehicle_id: Optional[str] = Field(default=None, description="车辆唯一标识ID")

    def to_dict(self) -> dict:
        """转换为API所需的字典格式"""
        result = {
            "hphm": self.license_number,
            "hpzl": self.license_plate_type,
            "hpzlmc": LICENSE_PLATE_TYPE_MAP.get(self.license_plate_type, ""),
            "cllx": self.vehicle_type,
            "cllxmc": VEHICLE_TYPE_MAP.get(self.vehicle_type, ""),
            "fdjh": self.engine_number,
            "ppxh": self.brand_model,
            "zcsj": self.registration_date,
            "kz3": self.kz3,
        }
        
        # 添加可选字段
        if self.collection_date:
            result["cjsj"] = self.collection_date
        if self.enable_status is not None:
            result["qyzt"] = self.enable_status
        if self.registration_channel_key:
            result["zcqdKey"] = self.registration_channel_key
        if self.identity_number:
            result["sfzmhm"] = self.identity_number
        if self.kz5:
            result["kz5"] = self.kz5
        if self.vehicle_id:
            result["vId"] = self.vehicle_id
            
        return result

    @classmethod
    def from_api_response(cls, data: dict) -> "VehicleInfo":
        """从API响应数据创建VehicleInfo实例"""
        return cls(
            license_plate_type=data.get("hpzl", ""),
            license_number=data.get("hphm", ""),
            vehicle_type=data.get("cllx", "01"),
            engine_number=data.get("fdjh", ""),
            brand_model=data.get("ppxh", ""),
            registration_date=data.get("zcsj", ""),
            collection_date=data.get("cjsj"),
            enable_status=data.get("qyzt", 1),
            registration_channel_key=data.get("zcqdKey"),
            identity_number=data.get("sfzmhm"),
            kz3=data.get("kz3", ""),
            kz5=data.get("kz5"),
            vehicle_id=data.get("vId")
        )

class UserInfo(BaseModel, AllowNoneConfig):
    id_number: str = Field(default="", description="身份证号")
    name: str = Field(default="", description="姓名")
    @classmethod
    def from_api_response(cls, data: dict) -> "UserInfo":
        return cls(
            id_number=data.get("jszh", ""),
            name=data.get("jsrxm", ""),
        )

class UserDetailInfo(BaseModel, AllowNoneConfig):
    cert_level: str = Field(default="", description="信息级别")
    ip: str = Field(default="", description="IP地址")
    mobile: str = Field(default="", description="手机号")
    source: str = Field(default="", description="请求渠道")
    id_number: str = Field(default="", description="身份证号")
    name: str = Field(default="", description="姓名")
    toon_no: str = Field(default="", description="通行证号")
    access_token: str = Field(default="", description="访问令牌")
    bjt_token: str = Field(default="", description="北京通令牌")
    dlsj: str = Field(default="", description="登录时间")

    @classmethod
    def from_api_response(cls, data: dict) -> "UserInfo":
        return cls(
            cert_level=data.get("certLevel", ""),
            ip=data.get("ip", ""),
            mobile=data.get("mobile", ""),
            source=data.get("source", ""),
            id_number=data.get("certNo", ""),
            name=data.get("certName", ""),
            toon_no=data.get("toonNo", ""),
            access_token=data.get("accessToken", ""),
            bjt_token=data.get("bjtToken", ""),
            dlsj=data.get("dlsj", ""),
        )


class NewApplyForm(BaseModel, AllowNoneConfig):
    sfzj: int = Field(default=1, description="是否在京")
    sqdzgdjd: str = Field(default="116.4", description="进京经度")
    sqdzgdwd: str = Field(default="39.9", description="进京纬度")
    zjxxdzgdjd: str = Field(default="116.4", description="在京经度")
    zjxxdzgdwd: str = Field(default="39.9", description="在京纬度")
    zjxxdz: str = Field(default="北京动物园", description="在京详细地址")
    xxdz: str = Field(default="北京动物园", description="详细地址")
    jjmdmc: str = Field(default="其它", description="进京目的地名称")
    jjmd: str = Field(default="06", description="进京目的地")
    area: str = Field(default="海淀区", description="区域")
    jjdq: str = Field(default="006", description="进京目的地地区")

    applyIdOld: str | None = Field(default=None, description="续办申请id")
    jjrq: str = Field(default="", description="进京日期(申请生效日期)")
    jsrxm: str = Field(default="", description="车主姓名")
    jszh: str = Field(default="", description="车主身份证号")
    jjzzl: str = Field(default="01", description="进京证类型")
    txrxx: list[dict] = Field(default=[], description="同行人信息")

    hphm: str = Field(default="", description="车牌号")
    hpzl: str = Field(default="", description="车牌类型")
    cllx: str = Field(default="", description="车辆类型")
    vId: str = Field(default="", description="车辆识别代号")
    
    def __init__(self,
        vehicle_info: VehicleInfo,
        user_info: UserInfo, 
        apply_date: str = datetime.now().strftime("%Y-%m-%d"),
        destination: str = "北京动物园",
        form_type: str = "六环内",
        **kwargs):
        """
        初始化进京证申请表单
        
        Args:
            vehicle_info: 车辆信息对象
            user_info: 用户信息对象
            apply_date: 申请日期 (格式: YYYY-MM-DD)
            destination: 目的地地址
            form_type: 表单类型（六环内/六环外）
            **kwargs: 其他字段参数
        """
        # 设置默认值
        data = {
            "sfzj": 1,  # 是否在京
            "sqdzgdjd": "116.4",  # 进京经度
            "sqdzgdwd": "39.9",  # 进京纬度
            "zjxxdzgdjd": "116.4",  # 在京经度
            "zjxxdzgdwd": "39.9",  # 在京纬度
            "zjxxdz": destination,  # 在京详细地址
            "xxdz": destination,  # 详细地址
            "jjmdmc": "其它",  # 进京目的地名称
            "jjmd": "06",  # 进京目的地
            "area": "海淀区",  # 区域
            "jjdq": "006",  # 进京目的地地区
            "applyIdOld": "",  # 续办申请id
            "jjrq": apply_date,  # 进京日期
            "jsrxm": "",  # 车主姓名
            "jszh": "",  # 车主身份证号
            "jjzzl": "01" if form_type == "六环内" else "02",  # 进京证类型
            "txrxx": [],  # 同行人信息
            "hphm": "",  # 车牌号
            "hpzl": "52",  # 默认小型新能源汽车
            "cllx": "01",  # 默认客车
            "vId": "",  # 车辆识别代号
        }
        
        # 使用车辆信息填充
        if vehicle_info:
            data.update({
                "hpzl": vehicle_info.license_plate_type,
                "hphm": vehicle_info.license_number,
                "cllx": vehicle_info.vehicle_type,
                "vId": vehicle_info.vehicle_id or "",
            })
        
        # 使用用户信息填充
        if user_info:
            data.update({
                "jsrxm": user_info.name,
                "jszh": user_info.id_number,
            })
        
        # 更新用户提供的参数
        data.update(kwargs)
        
        super().__init__(**data)

   

    def to_api_payload(self) -> dict:
        """转换为API请求的payload格式"""
        return {
            "sfzj": self.sfzj,
            "sqdzgdjd": self.sqdzgdjd,
            "sqdzgdwd": self.sqdzgdwd,
            "zjxxdzgdjd": self.zjxxdzgdjd,
            "zjxxdzgdwd": self.zjxxdzgdwd,
            "zjxxdz": self.zjxxdz,
            "xxdz": self.xxdz,
            "jjmdmc": self.jjmdmc,
            "jjmd": self.jjmd,
            "area": self.area,
            "jjdq": self.jjdq,
            "applyIdOld": self.applyIdOld,
            "jjrq": self.jjrq,
            "jsrxm": self.jsrxm,
            "jszh": self.jszh,
            "jjzzl": self.jjzzl,
            "txrxx": self.txrxx,
            "hphm": self.hphm,
            "hpzl": self.hpzl,
            "cllx": self.cllx,
            "vId": self.vId,
        }
       
    
class ApplyForm(BaseModel, AllowNoneConfig):
    """进京证申请表单模型"""
    sqdzgdjd: str = Field(default="116.4", description="进京经度")
    sqdzgdwd: str = Field(default="39.9", description="进京纬度")
    sqdzbdjd: str = Field(default="116.273348", description="进京目的地经度")
    sqdzbdwd: str = Field(default="40.040219", description="进京目的地纬度")
    txrxx: list[dict] = Field(default=[], description="同行人信息")
    hpzl: str = Field(default="", description="车牌类型")
    jjdq: str = Field(default="010", description="进京目的地地区")
    jjmd: str = Field(default="06", description="进京目的地")
    jjzzl: str = Field(default="01", description="进京证类型")
    jjlk: str = Field(default="00606", description="进京路况")
    jjmdmc: str = Field(default="其它", description="进京目的地名称")
    jjlkmc: str = Field(default="其他道路", description="进京路况名称")
    applyIdOld: str | None = Field(default=None, description="续办申请id")
    jjrq: str = Field(default="", description="进京日期(申请生效日期)")
    vId: str = Field(default="", description="车辆识别代号")
    jsrxm: str = Field(default="", description="车主姓名")
    jszh: str = Field(default="", description="车主身份证号")
    hphm: str = Field(default="", description="车牌号")
    sfzj: int = Field(default=1, description="是否在京")
    xxdz: str = Field(default="北京动物园", description="详细地址")
    zjxxdz: str = Field(default="北京动物园", description="在京详细地址")

    def __init__(self, 
                 vehicle_info: VehicleInfo = None,
                 apply_date: str = "",
                 name: str = "",
                 id_number: str = "",
                 destination: str = "北京动物园",
                 form_type: str = "六环内",
                 **kwargs):
        """
        初始化进京证申请表单
        
        Args:
            vehicle_info: 车辆信息对象
            apply_date: 申请日期 (格式: YYYY-MM-DD)
            name: 车主姓名
            id_number: 车主身份证号
            destination: 目的地地址
            form_type: 表单类型（六环内/六环外）
            **kwargs: 其他字段参数
        """
        # 设置默认值
        data = {
            "sqdzgdjd": "116.4",
            "sqdzgdwd": "39.9", 
            "sqdzbdjd": "116.273348",
            "sqdzbdwd": "40.040219",
            "txrxx": [],
            "hpzl": "52",  # 默认小型新能源汽车
            "jjdq": "010",
            "jjmd": "06",
            "jjzzl": "01" if form_type == "六环内" else "02",
            "jjlk": "00606",
            "jjmdmc": "其它",
            "jjlkmc": "其他道路",
            "applyIdOld": "",
            "jjrq": apply_date,
            "vId": "",
            "jsrxm": name,
            "jszh": id_number,
            "hphm": "",
            "sfzj": 1,
            "zjxxdz": destination,
            "xxdz": destination,
        }
        
        # 如果提供了车辆信息，使用车辆信息填充
        if vehicle_info:
            data.update({
                "hpzl": vehicle_info.license_plate_type,
                "hphm": vehicle_info.license_number,
                "vId": vehicle_info.vehicle_id or "",
            })
        
        # 更新用户提供的参数
        data.update(kwargs)
        
        super().__init__(**data)

    @classmethod
    def create_from_vehicle(cls, 
                           vehicle_info: VehicleInfo,
                           apply_date: str = "",
                           name: str = "",
                           id_number: str = "",
                           destination: str = "北京动物园",
                           form_type: str = "六环内",
                           **kwargs) -> "ApplyForm":
        """
        从车辆信息创建申请表单
        
        Args:
            vehicle_info: 车辆信息对象
            apply_date: 申请日期
            name: 车主姓名
            id_number: 车主身份证号
            destination: 目的地地址
            form_type: 表单类型（六环内/六环外）
            **kwargs: 其他参数
            
        Returns:
            ApplyForm: 申请表单实例
        """
        return cls(
            vehicle_info=vehicle_info,
            apply_date=apply_date,
            name=name,
            id_number=id_number,
            destination=destination,
            form_type=form_type,
            **kwargs
        )
    @classmethod
    def create_from_state_data(cls, state_data: dict, form_type: str = "六环内") -> "ApplyForm":
        return cls(
            vehicle_info=VehicleInfo.from_api_response(state_data["bzclxx"][0]),
            apply_date=state_data["yxqz"],
            name=state_data["jsrxm"],
            id_number=state_data["jszh"],
            form_type=form_type,
            destination=state_data["xxdz"],
        )
    def to_api_payload(self) -> dict:
        """转换为API请求的payload格式"""
        return {
            "sqdzgdjd": self.sqdzgdjd,
            "sqdzgdwd": self.sqdzgdwd,
            "sqdzbdjd": self.sqdzbdjd,
            "sqdzbdwd": self.sqdzbdwd,
            "txrxx": self.txrxx,
            "hpzl": self.hpzl,
            "jjdq": self.jjdq,
            "jjmd": self.jjmd,
            "jjzzl": self.jjzzl,
            "jjlk": self.jjlk,
            "jjmdmc": self.jjmdmc,
            "jjlkmc": self.jjlkmc,
            "applyIdOld": self.applyIdOld,
            "jjrq": self.jjrq,
            "vId": self.vId,
            "jsrxm": self.jsrxm,
            "jszh": self.jszh,
            "hphm": self.hphm,
            "sfzj": self.sfzj,
            "zjxxdz": self.zjxxdz,
            "xxdz": self.xxdz,
        }

class RecordInfo(BaseModel, AllowNoneConfig):
    """进京证申请记录信息模型"""
    vId: str = Field(default="", description="车辆识别代号")
    applyId: str = Field(default="", description="申请id")
    blzt: int = Field(default=0, description="进京证办理状态")
    blztmc: str = Field(default="", description="进京证办理状态名称")
    sxrqmc: str = Field(default="", description="生效日期名称")
    sxrzmc: str | None = Field(default=None, description="结束日期名称")
    yxqs: str = Field(default="", description="有效期开始日期")
    yxqz: str | None = Field(default=None, description="有效期结束日期")
    sxsyts: int | None = Field(default=None, description="剩余剩余天数")
    jjzzl: str = Field(default="", description="进京证类型")
    jjzzlmc: str = Field(default="", description="进京证类型名称")
    jjzh: str | None = Field(default=None, description="进京证号")
    sqsj: str = Field(default="", description="申请时间")
    jsrxm: str = Field(default="", description="车主姓名")
    jszh: str = Field(default="", description="车主身份证号")
    sfzmhm: str | None = Field(default=None, description="身份证明号码")
    shsbyy: str | None = Field(default=None, description="审核不通过原因")
    shsbyyms: str | None = Field(default=None, description="审核不通过原因描述")
    hphm: str = Field(default="", description="车牌号")
    hpzl: str = Field(default="", description="车牌类型")
    vid: str = Field(default="", description="车辆识别代号")
    
    @classmethod
    def from_api_response(cls, data: dict) -> "RecordInfo":
        """从API响应数据创建RecordInfo实例"""
        return cls(
            vId=data.get("vId", ""),
            applyId=data.get("applyId", ""),
            blzt=data.get("blzt", 0),
            blztmc=data.get("blztmc", ""),
            sxrqmc=data.get("sxrqmc", ""),
            sxrzmc=data.get("sxrzmc"),
            yxqs=data.get("yxqs", ""),
            yxqz=data.get("yxqz"),
            sxsyts=data.get("sxsyts"),
            jjzzl=data.get("jjzzl", ""),
            jjzzlmc=data.get("jjzzlmc", ""),
            jjzh=data.get("jjzh"),
            sqsj=data.get("sqsj", ""),
            jsrxm=data.get("jsrxm", ""),
            jszh=data.get("jszh", ""),
            sfzmhm=data.get("sfzmhm"),
            shsbyy=data.get("shsbyy"),
            shsbyyms=data.get("shsbyyms"),
            hphm=data.get("hphm", ""),
            hpzl=data.get("hpzl", ""),
            vid=str(data.get("vid", "")),
        )
    
    
    
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if not self.yxqz:
            return False
        from datetime import datetime
        try:
            expire_date = datetime.strptime(self.yxqz, "%Y-%m-%d")
            return expire_date < datetime.now()
        except ValueError:
            return False
    
    def get_status_description(self) -> str:
        """获取状态描述"""
        return self.blztmc
    def calc_remaining_days(self) -> int:
        """计算剩余天数"""
        if self.yxqz is not None:
            try:
                return days_between_dates(datetime.now().strftime("%Y-%m-%d"), self.yxqz)
            except (ValueError, TypeError):
                pass
        return 0
    def get_remaining_days(self) -> int:
        """获取剩余天数"""
        if self.sxsyts is not None:
            try:
                return int(self.sxsyts)
            except (ValueError, TypeError):
                pass
        return 0
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "vId": self.vId,
            "applyId": self.applyId,
            "blzt": self.blzt,
            "blztmc": self.blztmc,
            "sxrqmc": self.sxrqmc,
            "sxrzmc": self.sxrzmc,
            "yxqs": self.yxqs,
            "yxqz": self.yxqz,
            "sxsyts": self.sxsyts,
            "jjzzl": self.jjzzl,
            "jjzzlmc": self.jjzzlmc,
            "jjzh": self.jjzh,
            "sqsj": self.sqsj,
            "jsrxm": self.jsrxm,
            "jszh": self.jszh,
            "sfzmhm": self.sfzmhm,
            "shsbyy": self.shsbyy,
            "shsbyyms": self.shsbyyms,
            "hphm": self.hphm,
            "hpzl": self.hpzl,
            "vid": self.vid,
        }
    

class StateDataInfo(BaseModel, AllowNoneConfig):
    """车辆状态数据信息模型"""
    vId: str = Field(default="", description="车辆识别代号")
    hpzl: str = Field(default="", description="车牌类型")
    hphm: str = Field(default="", description="车牌号")
    ybcs: int = Field(default=0, description="已办次数")
    bzts: int = Field(default=0, description="办证天数")
    kjts: int = Field(default=0, description="可进天数")
    sycs: str = Field(default="", description="剩余次数")
    syts: str = Field(default="", description="剩余天数")
    ylzsfkb: bool = Field(default=False, description="一类证是否可办")
    elzsfkb: bool = Field(default=False, description="二类证是否可办")
    bnbzyy: str | None = Field(default=None, description="不能办证原因")
    qyzt: int = Field(default=0, description="启用状态")
    cllx: str = Field(default="", description="车辆类型")
    bzxx: list[RecordInfo] = Field(default=[], description="办证信息列表")
    ecbzxx: list[RecordInfo] = Field(default=[], description="二次办证信息列表")
    sfyecbzxx: bool = Field(default=False, description="是否有二次办证信息")
    ecztbz: bool | None = Field(default=None, description="二次状态办证")
    
    @classmethod
    def from_api_response(cls, data: dict) -> "StateDataInfo":
        """从API响应数据创建StateDataInfo实例"""
        # 处理办证信息列表
        bzxx_list = []
        if data.get("bzxx"):
            bzxx_list = [RecordInfo.from_api_response(record) for record in data["bzxx"]]
        
        # 处理二次办证信息列表
        ecbzxx_list = []
        if data.get("ecbzxx"):
            ecbzxx_list = [RecordInfo.from_api_response(record) for record in data["ecbzxx"]]
        
        return cls(
            vId=data.get("vId", ""),
            hpzl=data.get("hpzl", ""),
            hphm=data.get("hphm", ""),
            ybcs=data.get("ybcs", 0),
            bzts=data.get("bzts", 0),
            kjts=data.get("kjts", 0),
            sycs=str(data.get("sycs", "")),
            syts=str(data.get("syts", "")),
            ylzsfkb=data.get("ylzsfkb", False),
            elzsfkb=data.get("elzsfkb", False),
            bnbzyy=data.get("bnbzyy"),
            qyzt=data.get("qyzt", 0),
            cllx=data.get("cllx", ""),
            bzxx=bzxx_list,
            ecbzxx=ecbzxx_list,
            sfyecbzxx=data.get("sfyecbzxx", False),
            ecztbz=data.get("ecztbz", False),
        )
    
    def get_latest_record(self) -> RecordInfo | None:
        """获取最新的申请记录（优先二次办证信息）"""
        if self.ecbzxx and len(self.ecbzxx) > 0:
            return self.ecbzxx[0]
        elif self.bzxx and len(self.bzxx) > 0:
            return self.bzxx[0]
        return None
    
    def can_apply(self) -> bool:
        """检查是否可以申请进京证"""
        return self.ylzsfkb or self.elzsfkb
    
    def get_remaining_quota(self) -> dict:
        """获取剩余配额信息"""
        return {
            "remaining_times": int(self.sycs) if self.sycs.isdigit() else 0,
            "remaining_days": int(self.syts) if self.syts.isdigit() else 0,
            "used_times": self.ybcs,
            "total_days": self.bzts,
            "available_days": self.kjts
        }
    
   

class StateData(BaseModel, AllowNoneConfig):
    """状态数据模型"""
    sfzmhm: str = Field(default="", description="身份证明号码")
    ylzqyms: str = Field(default="", description="一类证说明")
    ylzmc: str = Field(default="", description="一类证名称")
    elzqyms: str = Field(default="", description="二类证说明")
    elzmc: str = Field(default="", description="二类证名称")
    bzclxx: list[StateDataInfo] = Field(default=[], description="办证车辆信息列表")
    
    @classmethod
    def from_api_response(cls, data: dict) -> "StateData":
        """从API响应数据创建StateData实例"""
        # 处理车辆信息列表
        bzclxx_list = []
        if data.get("bzclxx"):
            bzclxx_list = [StateDataInfo.from_api_response(vehicle) for vehicle in data["bzclxx"]]
        
        return cls(
            sfzmhm=data.get("sfzmhm", ""),
            ylzqyms=data.get("ylzqyms", ""),
            ylzmc=data.get("ylzmc", ""),
            elzqyms=data.get("elzqyms", ""),
            elzmc=data.get("elzmc", ""),
            bzclxx=bzclxx_list,
        )
    
    def get_first_vehicle(self) -> StateDataInfo | None:
        """获取第一辆车的信息"""
        return self.bzclxx[0] if self.bzclxx else None
    
    def get_vehicle_by_id(self, vId: str) -> StateDataInfo | None:
        """根据车辆ID获取车辆信息"""
        for vehicle in self.bzclxx:
            if vehicle.vId == vId:
                return vehicle
        return None
    
    def get_latest_record(self) -> RecordInfo | None:
        """获取最新的申请记录（从第一辆车）"""
        first_vehicle = self.get_first_vehicle()
        return first_vehicle.get_latest_record() if first_vehicle else None
    
    def can_apply(self) -> bool:
        """检查是否可以申请进京证（第一辆车）"""
        first_vehicle = self.get_first_vehicle()
        return first_vehicle.can_apply() if first_vehicle else False
    
    def get_quota_info(self) -> dict:
        """获取配额信息（第一辆车）"""
        first_vehicle = self.get_first_vehicle()
        return first_vehicle.get_remaining_quota() if first_vehicle else {}

import requests
import traceback
from loguru import logger
from model import VehicleInfo, UserInfo, ApplyForm, UserDetailInfo, NewApplyForm, StateData
from constant import SOURCE


class JTGLManager:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self._new_session()

    def _new_session(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": self.token, "Content-Type": "application/json"}
        )

    def _call_api(self, url, data=None, headers=None, method="POST"):
        if headers is None:
            headers = self.session.headers
        else:
            headers.update(self.session.headers)
        response = self.session.request(method, url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result.get("code") != 200:
            raise Exception(f"API 调用失败，url: {url}, data: {data}, result: {result}")
        return result


class VehicleManager(JTGLManager):
    def list_vehicles(self) -> list[VehicleInfo]:
        url = f"{self.url}/pro//vehicleController/getUserIdInfo"
        response = self._call_api(url, data={})
        return [
            VehicleInfo.from_api_response(vehicle) for vehicle in response.get("data")
        ]

    def delete_vehicle(self, vId):
        url = f"{self.url}/pro//relationController/deleteRelation"
        response = self._call_api(url, data={"vId": vId})
        return response

    def add_vehicle(self, vehicle_info: VehicleInfo):
        url = f"{self.url}/pro//relationController/add"
        payload = {"relation": {}, "vehicle": vehicle_info.to_dict()}
        response = self._call_api(url, data=payload)
        return response


class UserManager(JTGLManager):
    def get_user_info(self) -> UserInfo:
        url = f"{self.url}/pro/applyRecordController/getJsrxx"
        response = self._call_api(url, data={})
        return UserInfo.from_api_response(response.get("data"))
    def get_user_detail_info(self) -> UserDetailInfo:
        try:
            url = f"{self.url}/auth/userController/loginUser?state=101000004071"
            headers = {"Source": SOURCE}
            response = self._call_api(
                url,
                data={"token": self.token, "state": "101000004071"},
                headers=headers,
            )
            if response.get("code") != 200:
                raise Exception(f"登录失败，url: {url}, result: {response}")
            user_info = UserDetailInfo.from_api_response(response.get("data"))
        except Exception as e:
            logger.error(f"traceback.format_exc(): {traceback.format_exc()}")
            raise Exception(f"登录失败，url: {url}, result: {e}")
        return user_info


class ApplyRecordManager(JTGLManager):
    def get_state_data(self) -> StateData:
        """获取状态数据"""
        url = f"{self.url}/pro/applyRecordController/stateList"
        response = self._call_api(url, data={})
        return StateData.from_api_response(response.get("data"))
    
    def do_apply_record(self, apply_form: NewApplyForm | ApplyForm) -> dict:
        if isinstance(apply_form, NewApplyForm):
            return self.do_apply_record_v2(apply_form)
        else:
            return self.do_apply_record_v1(apply_form)
    def do_apply_record_v2(self, apply_form: NewApplyForm) -> dict:
        url = f"{self.url}/pro/applyRecordController/insertApplyRecord"
        response = self._call_api(url, data=apply_form.to_api_payload())
        return response
    def do_apply_record_v1(self, apply_form: ApplyForm) -> dict:
        url = f"{self.url}/pro/applyRecordController/insertApplyRecord"
        response = self._call_api(url, data=apply_form.to_api_payload())
        return response



import os
import json
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bjt_login import BeijingTong, get_token
from utils import logger, encrypt_url, decrypt_url

# 通用配置，允许 None 值
class AllowNoneConfig:
    model_config = ConfigDict(extra='ignore', validate_assignment=True)

class UserConfig(BaseModel, AllowNoneConfig):
    name: str = Field(default="", description="用户名")
    auth: str = Field(default="", description="认证token")
    bjt_phone: str = Field(default="", description="北京通手机号")
    bjt_pwd: str = Field(default="", description="北京通密码")
    entry_type: str = Field(default="六环内", description="进京证类型")
    # 推送配置，支持多种推送方式
    notify_urls: list[str] = Field(default=[], description="推送服务URL列表")


class ConfigData(BaseModel):
    url: str = Field(default="", description="接口地址（加密存储）")
    users: list[UserConfig] = Field(default=[], description="用户配置")
    
    def get_decrypted_url(self) -> str:
        """获取解密后的URL"""
        return decrypt_url(self.url)
    
    def set_encrypted_url(self, url: str):
        """设置加密后的URL"""
        self.url = encrypt_url(url)


class ConfigManager:
    """配置管理器，负责处理认证信息的自动获取和保存"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config_data: Optional[ConfigData] = None
        self._load_config()
        self.process_all_users()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
            self.config_data = ConfigData(**config_dict)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    

    def _save_config(self):
        """保存配置文件"""
        try:
            config_dict = self.config_data.model_dump()
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=4)
            logger.info("配置文件保存成功")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    def _has_auth(self, user: UserConfig) -> bool:
        """检查用户是否已有认证信息"""
        return bool(user.auth and user.auth.strip())
    
    def _has_bjt_credentials(self, user: UserConfig) -> bool:
        """检查用户是否填写了北京通手机号和密码"""
        return bool(user.bjt_phone and user.bjt_phone.strip() and 
                   user.bjt_pwd and user.bjt_pwd.strip())
    
    def _get_auth_token(self, user: UserConfig) -> Optional[str]:
        """通过北京通登录获取认证token"""
        try:
            logger.info(f"开始为用户 {user.name} 获取认证token")
            
            # 创建北京通登录实例
            bjt = BeijingTong(user.bjt_phone, user.bjt_pwd, user.notify_urls)
            
            # 执行登录
            auth_url = bjt.login()
            if not auth_url:
                logger.error(f"用户 {user.name} 北京通登录失败")
                return None
            
            # 获取token
            token = get_token(auth_url)
            if not token:
                logger.error(f"用户 {user.name} 获取token失败")
                return None
            
            logger.info(f"用户 {user.name} 成功获取认证token")
            return token
            
        except Exception as e:
            logger.error(f"用户 {user.name} 获取认证token时发生错误: {e}")
            return None
    
    def process_user_auth(self, user: UserConfig) -> UserConfig:
        """处理单个用户的认证信息"""
        # 如果已有认证信息，直接返回
        if self._has_auth(user):
            logger.info(f"用户 {user.name} 已有认证信息，跳过")
            return user
        
        # 如果没有北京通手机号和密码，跳过
        if not self._has_bjt_credentials(user):
            logger.info(f"用户 {user.name} 未填写北京通手机号和密码，跳过认证")
            return user
        
        # 尝试获取认证token
        token = self._get_auth_token(user)
        if token:
            user.auth = token
            logger.info(f"用户 {user.name} 认证信息已更新")
        else:
            logger.warning(f"用户 {user.name} 认证信息获取失败")
        
        return user
    
    def process_all_users(self):
        """处理所有用户的认证信息"""
        if not self.config_data:
            logger.error("配置数据未加载")
            return
        
        updated = False
        for i, user in enumerate(self.config_data.users):
            original_auth = user.auth
            processed_user = self.process_user_auth(user)
            
            
            # 如果认证信息发生了变化，更新配置
            if processed_user.auth != original_auth:
                self.config_data.users[i] = processed_user
                updated = True
        
        # 如果有更新，保存配置文件
        if updated:
            self._save_config()
            logger.info("所有用户认证信息处理完成，配置文件已更新")
        else:
            logger.info("所有用户认证信息处理完成，无需更新配置文件")
        final_auth_users = []
        for user in self.config_data.users:
            if user.auth:
                final_auth_users.append(user)
        self.config_data.users = final_auth_users
    
    def get_config(self) -> ConfigData:
        """获取配置数据"""
        return self.config_data
    
    def get_user_configs(self) -> list[UserConfig]:
        """获取用户配置列表"""
        return self.config_data.users if self.config_data else []
    
    def get_decrypted_url(self) -> str:
        """获取解密后的URL"""
        return self.config_data.get_decrypted_url() if self.config_data else ""


# 创建全局配置管理器实例
config_manager = ConfigManager()
config = config_manager.get_config()


def get_user_configs() -> list[UserConfig]:
    return config_manager.get_user_configs()
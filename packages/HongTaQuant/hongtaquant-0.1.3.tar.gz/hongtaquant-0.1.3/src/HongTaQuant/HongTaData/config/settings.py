"""Settings模块，包含配置信息"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_prefix="HONGTA_",
    env_file=".env",
    case_sensitive=False,
  )

  # HTTP客户端配置
  http_base_url:str = Field(default="", description="HTTP API基础URL")
  http_username:str = Field(default="", description="HTTP API用户名")
  http_password:str = Field(default="", description="HTTP API密码")
  http_timeout:int = Field(default=30, description="HTTP请求超时时间（秒）")

# 全局配置实例
settings = Settings()

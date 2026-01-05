"""
应用配置模块
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    app_name: str = "CorpPilot"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # CORS 配置
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000"
    ]
    
    # 文件上传配置
    upload_dir: str = "./uploads"
    max_upload_size: int = 50  # MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# 确保上传目录存在
os.makedirs(settings.upload_dir, exist_ok=True)



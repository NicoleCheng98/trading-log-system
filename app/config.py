"""
配置模块
从.env文件加载配置变量，并提供给应用使用
"""
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

class Config:
    """应用配置类"""
    # 数据库配置
    # 强制使用SQLite数据库，忽略环境变量中的配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trading_log.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # CSRF保护
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', 'csrf_dev_secret_key')
    
    # 应用配置
    APP_NAME = os.getenv('APP_NAME', '交易日志系统')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

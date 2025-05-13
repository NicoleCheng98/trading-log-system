"""
应用初始化模块
这个模块负责创建和配置Flask应用实例
"""
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

# 创建数据库实例
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    """
    创建并配置Flask应用
    
    返回:
        Flask: 配置好的Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__)
    
    # 从config.py加载配置
    from app.config import Config
    app.config.from_object(Config)
    
    # 初始化扩展
    # 确保使用SQLite而非PostgreSQL
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        # 为SQLite启用外键约束
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'check_same_thread': False},
            'poolclass': None
        }
    
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # 启用跨域请求支持
    csrf.init_app(app)  # 启用CSRF保护
    
    # 添加模板上下文处理器
    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.now().year,
            'request': request
        }
    
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    from app.api.webhook import webhook_bp
    app.register_blueprint(webhook_bp, url_prefix='/api')
    
    # 确保模型被加载，以便数据库迁移能够检测到表结构
    with app.app_context():
        from app import models
    
    # 创建数据库表(如果不存在)
    with app.app_context():
        db.create_all()
    
    return app

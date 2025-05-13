#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用启动脚本
用于启动Flask应用服务器
"""
from app import create_app
from app import models  # 导入模型，确保数据库迁移能够检测到表结构
import os

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 从环境变量获取端口，默认为5001（避开macOS的AirPlay服务）
    port = int(os.environ.get('PORT', 5001))
    
    # 启动应用
    app.run(host='0.0.0.0', port=port, debug=True)
    
    print(f"交易日志系统已启动，访问 http://localhost:{port} 查看")

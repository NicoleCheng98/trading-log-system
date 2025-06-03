#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交易日志系统修复脚本
自动修复常见问题，包括缺少的导入和依赖
作者: Nicole Cheng
创建日期: 2025-06-03
"""

import os
import sys
import subprocess
import time

def print_color(text, color="green"):
    """打印彩色文本"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, colors['green'])}{text}{colors['end']}")

def print_step(step, description):
    """打印步骤信息"""
    print("\n" + "=" * 60)
    print_color(f"步骤 {step}: {description}", "blue")
    print("=" * 60)

def print_success(message):
    """打印成功信息"""
    print_color(f"✅ {message}")

def print_warning(message):
    """打印警告信息"""
    print_color(f"⚠️ {message}", "yellow")

def print_error(message):
    """打印错误信息"""
    print_color(f"❌ {message}", "red")

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def backup_database():
    """备份数据库文件"""
    print_step(1, "备份数据库")
    
    if os.path.exists("trading_log.db"):
        backup_name = f"trading_log_backup_{int(time.time())}.db"
        try:
            import shutil
            shutil.copy2("trading_log.db", backup_name)
            print_success(f"数据库已备份为: {backup_name}")
        except Exception as e:
            print_error(f"备份数据库时出错: {str(e)}")
            return False
    else:
        print_warning("未找到数据库文件，跳过备份步骤")
    
    return True

def fix_routes_file():
    """修复routes.py中缺少的timedelta导入"""
    print_step(2, "修复routes.py文件")
    
    routes_path = os.path.join('app', 'routes.py')
    if not os.path.exists(routes_path):
        print_error(f"找不到文件: {routes_path}")
        return False
    
    try:
        with open(routes_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if 'from datetime import datetime, timedelta' in content:
            print_success("routes.py文件已包含timedelta导入，无需修改")
        else:
            # 修复缺少的timedelta导入
            content = content.replace(
                'from datetime import datetime', 
                'from datetime import datetime, timedelta'
            )
            
            with open(routes_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            print_success("已成功修复routes.py中缺少的timedelta导入")
    except Exception as e:
        print_error(f"修复routes.py文件时出错: {str(e)}")
        return False
    
    return True

def install_dependencies():
    """安装缺少的依赖"""
    print_step(3, "安装缺少的依赖")
    
    dependencies = [
        "Flask-WTF",
        "Flask-SQLAlchemy",
        "Flask-Migrate",
        "Flask-Cors",
        "python-dotenv",
        "marshmallow"
    ]
    
    for dep in dependencies:
        print(f"正在安装 {dep}...")
        success, output = run_command(f"{sys.executable} -m pip install {dep}")
        if success:
            print_success(f"{dep} 安装成功")
        else:
            print_warning(f"{dep} 安装过程中出现警告，但可能不影响使用")
    
    return True

def main():
    """主函数"""
    print_color("\n欢迎使用交易日志系统修复工具！", "purple")
    print("本工具将自动修复常见问题，包括缺少的导入和依赖。")
    print("修复过程不会影响您已有的数据。")
    
    # 检查是否在项目根目录
    if not os.path.exists("app") or not os.path.exists("run.py"):
        print_error("错误: 请确保您在交易日志系统的根目录运行此脚本")
        print("提示: 此脚本应该与run.py文件放在同一个文件夹中")
        return
    
    # 备份数据库
    if not backup_database():
        if input("是否继续修复过程？(y/n): ").lower() != 'y':
            return
    
    # 修复routes.py文件
    if not fix_routes_file():
        if input("是否继续修复过程？(y/n): ").lower() != 'y':
            return
    
    # 安装缺少的依赖
    if not install_dependencies():
        if input("是否继续修复过程？(y/n): ").lower() != 'y':
            return
    
    print_color("\n🎉 修复已完成！", "purple")
    print_color("\n请按照以下步骤重启应用:", "blue")
    print("1. 如果应用正在运行，按Ctrl+C停止")
    print("2. 重新启动应用:")
    print("   - Windows系统: python run.py")
    print("   - Mac系统: python3 run.py")
    print("\n如果您仍然遇到问题，请联系系统管理员获取帮助。")

if __name__ == "__main__":
    main()

#!/bin/bash

# 自动从GitHub更新交易日志系统
# 作者: Nicole Cheng
# 创建日期: 2025-05-14

# 日志文件路径
LOG_FILE="/var/www/trading_log/update.log"

# 项目路径
PROJECT_PATH="/var/www/trading_log"

# 记录日志的函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 确保日志文件存在
touch "$LOG_FILE"

# 开始记录
log_message "开始更新交易日志系统..."

# 进入项目目录
cd "$PROJECT_PATH" || {
    log_message "错误: 无法进入项目目录 $PROJECT_PATH"
    exit 1
}

# 保存当前的 Git 哈希值
OLD_HASH=$(git rev-parse HEAD)
log_message "当前版本: $OLD_HASH"

# 检查是否有未提交的更改
if [[ -n $(git status -s) ]]; then
    log_message "警告: 本地有未提交的更改，将被保存为 stash"
    git stash
fi

# 拉取最新代码
log_message "从 GitHub 拉取最新代码..."
git pull origin master

# 检查是否有更新
NEW_HASH=$(git rev-parse HEAD)
if [[ "$OLD_HASH" == "$NEW_HASH" ]]; then
    log_message "没有发现新的更新，退出脚本"
    exit 0
fi

log_message "检测到新版本: $NEW_HASH"

# 激活虚拟环境
source venv/bin/activate || {
    log_message "错误: 无法激活虚拟环境"
    exit 1
}

# 安装/更新依赖
log_message "更新依赖..."
pip install -r requirements.txt

# 执行数据库迁移
log_message "执行数据库迁移..."
export FLASK_APP=run.py
flask db migrate -m "自动更新: $(date '+%Y-%m-%d %H:%M:%S')"
flask db upgrade

# 重启 Gunicorn 服务
log_message "重启 Gunicorn 服务..."
sudo systemctl restart trading_log

# 检查服务状态
SERVICE_STATUS=$(sudo systemctl is-active trading_log)
if [[ "$SERVICE_STATUS" == "active" ]]; then
    log_message "Gunicorn 服务已成功重启"
else
    log_message "错误: Gunicorn 服务重启失败，状态: $SERVICE_STATUS"
    log_message "查看服务日志: sudo journalctl -u trading_log"
fi

# 完成
log_message "更新完成! 从 $OLD_HASH 更新到 $NEW_HASH"

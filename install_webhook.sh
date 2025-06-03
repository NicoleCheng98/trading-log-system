#!/bin/bash

# 安装修复后的webhook代码
# 作者: Nicole Cheng
# 创建日期: 2025-05-15

# 设置工作目录
cd /var/www/trading_log

# 备份原始文件
echo "备份原始webhook.py文件..."
cp app/api/webhook.py app/api/webhook.py.bak

# 应用修复
echo "应用webhook修复..."
cp fix_webhook.py app/api/webhook.py

# 重启服务
echo "重启交易日志系统服务..."
systemctl daemon-reload
systemctl restart trading_log

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 测试webhook
echo "测试webhook端点..."
curl -X POST http://localhost:5001/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT", "direction":"buy", "price":45000, "strategy":"测试策略"}'

echo ""
echo "测试tradingview专用端点..."
curl -X POST http://localhost:5001/api/tradingview \
  -H "Content-Type: application/json" \
  -d '{"symbol":"ETHUSDT", "direction":"sell", "price":2500, "strategy":"TradingView测试"}'

echo ""
echo "安装完成!"

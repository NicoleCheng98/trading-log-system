#!/bin/bash

# 测试Webhook端点
curl -X POST http://localhost:5001/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT", "direction":"buy", "price":45000, "strategy":"测试策略"}'

echo ""
echo "测试完成"

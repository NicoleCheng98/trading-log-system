"""
修复Webhook端点的CSRF保护问题
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import json
from app import db, csrf
from app.models import PendingTrade

# 创建蓝图
webhook_bp = Blueprint('webhook', __name__)

# 为Webhook端点禁用CSRF保护
@webhook_bp.route('/webhook', methods=['POST'])
@csrf.exempt
def receive_webhook():
    """
    接收TradingView发送的webhook
    
    TradingView会发送JSON格式的交易信号，包含以下字段:
    - symbol: 交易品种代码
    - direction: 交易方向(buy/sell)
    - price: 信号价格
    - timestamp: 信号时间(可选，如果没有提供则使用当前时间)
    - strategy: 策略名称(可选)
    - notes: 备注信息(可选)
    
    交易分析字段(全部可选):
    - current_trend: 当前趋势(上涨/下跌/震荡)
    - weekly_resistance: 周线阻力位
    - weekly_support: 周线支撑位
    - daily_resistance: 日线阻力位
    - daily_support: 日线支撑位
    - h4_resistance: 4小时阻力位
    - h4_support: 4小时支撑位
    - timeframe: 考虑交易的时间周期
    - risk_reward_ratio: 盈亏比
    - entry_price_target: 目标进场价格
    - stop_loss: 止损价格
    - take_profit: 止盈价格
    - support_resistance_reaction: K线触及支撑阻力位的反应
    
    返回:
        JSON: 包含处理结果的JSON响应
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 打印接收到的数据(调试用)
        print(f"接收到webhook数据: {data}")
        
        # 验证必要字段
        required_fields = ['symbol', 'direction', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必要字段: {field}'
                }), 400
        
        # 处理时间戳
        timestamp = None
        if 'timestamp' in data and data['timestamp']:
            try:
                # 尝试解析ISO格式的时间戳
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                # 如果解析失败，使用当前时间
                timestamp = datetime.utcnow()
        else:
            # 如果没有提供时间戳，使用当前时间
            timestamp = datetime.utcnow()
        
        # 创建新的待处理交易记录
        new_trade = PendingTrade(
            symbol=data['symbol'],
            direction=data['direction'],
            price=float(data['price']),
            timestamp=timestamp,
            strategy=data.get('strategy', ''),
            notes=data.get('notes', ''),
            status='pending',
            
            # 新增交易分析字段
            current_trend=data.get('current_trend', None),
            weekly_resistance=data.get('weekly_resistance', None),
            weekly_support=data.get('weekly_support', None),
            daily_resistance=data.get('daily_resistance', None),
            daily_support=data.get('daily_support', None),
            h4_resistance=data.get('h4_resistance', None),
            h4_support=data.get('h4_support', None),
            timeframe=data.get('timeframe', None),
            risk_reward_ratio=float(data.get('risk_reward_ratio', 0)) if data.get('risk_reward_ratio') else None,
            entry_price_target=float(data.get('entry_price_target', 0)) if data.get('entry_price_target') else None,
            stop_loss=float(data.get('stop_loss', 0)) if data.get('stop_loss') else None,
            take_profit=float(data.get('take_profit', 0)) if data.get('take_profit') else None,
            support_resistance_reaction=data.get('support_resistance_reaction', None)
        )
        
        # 保存到数据库
        db.session.add(new_trade)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '交易信号已保存',
            'trade_id': new_trade.id
        })
        
    except Exception as e:
        # 回滚数据库事务
        db.session.rollback()
        
        # 返回错误信息
        return jsonify({
            'status': 'error',
            'message': f'处理webhook时出错: {str(e)}'
        }), 500

# 添加专门用于TradingView的端点
@webhook_bp.route('/tradingview', methods=['POST'])
@csrf.exempt
def tradingview_webhook():
    """
    专门用于接收TradingView发送的webhook
    """
    return receive_webhook()

@webhook_bp.route('/test', methods=['GET'])
def test_webhook():
    """
    测试webhook接口是否正常工作
    
    返回:
        JSON: 包含测试结果的JSON响应
    """
    return jsonify({
        'status': 'success',
        'message': 'Webhook接口正常工作'
    })

@webhook_bp.route('/example', methods=['GET'])
def webhook_example():
    """
    返回webhook的示例payload
    
    返回:
        JSON: 包含示例payload的JSON响应
    """
    example = {
        "symbol": "BTCUSDT",
        "direction": "buy",
        "price": 45000,
        "timestamp": "2025-05-14T12:00:00Z",
        "strategy": "MA交叉策略",
        "notes": "强势突破，成交量增加",
        "current_trend": "上涨",
        "weekly_resistance": "48000, 50000",
        "weekly_support": "42000, 40000",
        "daily_resistance": "46000",
        "daily_support": "44000",
        "h4_resistance": "45500",
        "h4_support": "44500",
        "timeframe": "1h",
        "risk_reward_ratio": 2.5,
        "entry_price_target": 45000,
        "stop_loss": 44000,
        "take_profit": 47500,
        "support_resistance_reaction": "强烈反弹"
    }
    
    return jsonify(example)

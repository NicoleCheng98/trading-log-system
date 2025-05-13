"""
数据模型模块
定义应用使用的数据库模型/表结构
"""
from datetime import datetime
from app import db

class PendingTrade(db.Model):
    """
    待处理交易表
    用于存储从TradingView接收的交易信号
    """
    __tablename__ = 'pending_trades'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, comment='交易品种代码')
    direction = db.Column(db.String(10), nullable=False, comment='交易方向(buy/sell)')
    price = db.Column(db.Float, nullable=False, comment='信号价格')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, comment='信号时间')
    strategy = db.Column(db.String(100), comment='策略名称')
    status = db.Column(db.String(20), default='pending', comment='信号状态(pending/confirmed/rejected)')
    notes = db.Column(db.Text, comment='备注信息')
    
    # 新增交易分析字段
    current_trend = db.Column(db.String(20), comment='当前趋势(上涨/下跌/震荡)')
    weekly_resistance = db.Column(db.String(100), comment='周线阻力位')
    weekly_support = db.Column(db.String(100), comment='周线支撑位')
    daily_resistance = db.Column(db.String(100), comment='日线阻力位')
    daily_support = db.Column(db.String(100), comment='日线支撑位')
    h4_resistance = db.Column(db.String(100), comment='4小时阻力位')
    h4_support = db.Column(db.String(100), comment='4小时支撑位')
    timeframe = db.Column(db.String(50), comment='考虑交易的时间周期')
    risk_reward_ratio = db.Column(db.Float, comment='盈亏比')
    entry_price_target = db.Column(db.Float, comment='目标进场价格')
    stop_loss = db.Column(db.Float, comment='止损价格')
    take_profit = db.Column(db.Float, comment='止盈价格')
    support_resistance_reaction = db.Column(db.Text, comment='K线触及支撑阻力位的反应')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联到正式交易记录
    trades = db.relationship('Trade', backref='pending_trade', lazy=True)
    
    def __repr__(self):
        """返回对象的字符串表示"""
        return f"<PendingTrade {self.symbol} {self.direction} at {self.price}>"
    
    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'direction': self.direction,
            'price': self.price,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'strategy': self.strategy,
            'status': self.status,
            'notes': self.notes,
            'current_trend': self.current_trend,
            'weekly_resistance': self.weekly_resistance,
            'weekly_support': self.weekly_support,
            'daily_resistance': self.daily_resistance,
            'daily_support': self.daily_support,
            'h4_resistance': self.h4_resistance,
            'h4_support': self.h4_support,
            'timeframe': self.timeframe,
            'risk_reward_ratio': self.risk_reward_ratio,
            'entry_price_target': self.entry_price_target,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'support_resistance_reaction': self.support_resistance_reaction,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Trade(db.Model):
    """
    正式交易表
    用于存储已确认的交易记录，包含完整的交易信息
    """
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    pending_trade_id = db.Column(db.Integer, db.ForeignKey('pending_trades.id'), comment='关联的待处理交易ID')
    symbol = db.Column(db.String(20), nullable=False, comment='交易品种代码')
    direction = db.Column(db.String(10), nullable=False, comment='交易方向(buy/sell)')
    entry_price = db.Column(db.Float, nullable=False, comment='入场价格')
    exit_price = db.Column(db.Float, comment='出场价格')
    entry_time = db.Column(db.DateTime, nullable=False, comment='入场时间')
    exit_time = db.Column(db.DateTime, comment='出场时间')
    profit_loss = db.Column(db.Float, comment='盈亏金额')
    profit_loss_percent = db.Column(db.Float, comment='盈亏百分比')
    strategy = db.Column(db.String(100), comment='策略名称')
    notes = db.Column(db.Text, comment='交易笔记')
    
    # 新增交易分析字段
    current_trend = db.Column(db.String(20), comment='当前趋势(上涨/下跌/震荡)')
    weekly_resistance = db.Column(db.String(100), comment='周线阻力位')
    weekly_support = db.Column(db.String(100), comment='周线支撑位')
    daily_resistance = db.Column(db.String(100), comment='日线阻力位')
    daily_support = db.Column(db.String(100), comment='日线支撑位')
    h4_resistance = db.Column(db.String(100), comment='4小时阻力位')
    h4_support = db.Column(db.String(100), comment='4小时支撑位')
    timeframe = db.Column(db.String(50), comment='考虑交易的时间周期')
    risk_reward_ratio = db.Column(db.Float, comment='盈亏比')
    stop_loss = db.Column(db.Float, comment='止损价格')
    take_profit = db.Column(db.Float, comment='止盈价格')
    support_resistance_reaction = db.Column(db.Text, comment='K线触及支撑阻力位的反应')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """返回对象的字符串表示"""
        return f"<Trade {self.symbol} {self.direction} entry:{self.entry_price} exit:{self.exit_price}>"
    
    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'pending_trade_id': self.pending_trade_id,
            'symbol': self.symbol,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'profit_loss': self.profit_loss,
            'profit_loss_percent': self.profit_loss_percent,
            'strategy': self.strategy,
            'notes': self.notes,
            'current_trend': self.current_trend,
            'weekly_resistance': self.weekly_resistance,
            'weekly_support': self.weekly_support,
            'daily_resistance': self.daily_resistance,
            'daily_support': self.daily_support,
            'h4_resistance': self.h4_resistance,
            'h4_support': self.h4_support,
            'timeframe': self.timeframe,
            'risk_reward_ratio': self.risk_reward_ratio,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'support_resistance_reaction': self.support_resistance_reaction,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

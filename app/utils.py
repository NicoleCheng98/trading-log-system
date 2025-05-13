"""
工具函数模块
提供各种辅助函数，用于处理日期、数据验证等
"""
from datetime import datetime
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_iso_datetime(date_string):
    """
    解析ISO格式的日期时间字符串
    
    参数:
        date_string (str): ISO格式的日期时间字符串
        
    返回:
        datetime: 解析后的datetime对象，如果解析失败则返回None
    """
    try:
        # 处理带Z的UTC时间格式
        if date_string.endswith('Z'):
            date_string = date_string.replace('Z', '+00:00')
        return datetime.fromisoformat(date_string)
    except (ValueError, TypeError) as e:
        logger.error(f"日期解析错误: {e}")
        return None

def calculate_profit_loss(entry_price, exit_price, direction):
    """
    计算交易的盈亏金额和百分比
    
    参数:
        entry_price (float): 入场价格
        exit_price (float): 出场价格
        direction (str): 交易方向，'buy'或'sell'
        
    返回:
        tuple: (盈亏金额, 盈亏百分比)
    """
    if not all([entry_price, exit_price, direction]):
        return None, None
    
    try:
        if direction.lower() == 'buy':
            # 买入交易: 出场价格 - 入场价格
            profit = exit_price - entry_price
        else:
            # 卖出交易: 入场价格 - 出场价格
            profit = entry_price - exit_price
        
        # 计算百分比
        percent = (profit / entry_price) * 100
        
        return profit, percent
    except Exception as e:
        logger.error(f"计算盈亏时发生错误: {e}")
        return None, None

def validate_trade_data(data, required_fields=None):
    """
    验证交易数据是否包含所有必要字段
    
    参数:
        data (dict): 要验证的数据
        required_fields (list): 必要字段列表，如果为None则使用默认列表
        
    返回:
        tuple: (是否有效, 错误消息)
    """
    if required_fields is None:
        required_fields = ['symbol', 'direction', 'price']
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必要字段: {', '.join(missing_fields)}"
    
    return True, None

def format_log_message(message, data=None):
    """
    格式化日志消息，可选择包含JSON数据
    
    参数:
        message (str): 日志消息
        data (dict): 要包含在日志中的数据
        
    返回:
        str: 格式化后的日志消息
    """
    if data:
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            return f"{message} - 数据: {json_str}"
        except Exception:
            return message
    return message

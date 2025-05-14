"""
主路由模块
处理应用的主要路由和视图函数
"""
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from app.models import PendingTrade, Trade
from app import db
from datetime import datetime
import json
from sqlalchemy import desc, func

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页路由"""
    # 获取统计数据
    pending_count = PendingTrade.query.filter_by(status='pending').count()
    confirmed_count = PendingTrade.query.filter_by(status='confirmed').count()
    
    # 获取最近的交易信号
    recent_pending_trades = PendingTrade.query.order_by(desc(PendingTrade.timestamp)).limit(5).all()
    
    # 盈亏统计
    trades = Trade.query.all()
    profit_trades = sum(1 for trade in trades if trade.profit_loss and trade.profit_loss > 0)
    loss_trades = sum(1 for trade in trades if trade.profit_loss and trade.profit_loss <= 0)
    
    total_profit = sum(trade.profit_loss for trade in trades if trade.profit_loss and trade.profit_loss > 0) or 0
    total_loss = sum(trade.profit_loss for trade in trades if trade.profit_loss and trade.profit_loss <= 0) or 0
    net_profit = total_profit + total_loss
    
    # 胜率
    total_trades = profit_trades + loss_trades
    win_rate = (profit_trades / total_trades * 100) if total_trades > 0 else 0
    
    # 平均盈亏比
    avg_profit_loss_ratio = 0
    if trades:
        ratios = [trade.risk_reward_ratio for trade in trades if trade.risk_reward_ratio]
        avg_profit_loss_ratio = sum(ratios) / len(ratios) if ratios else 0
    
    # 平均持仓时间
    avg_holding_days = 0
    if trades:
        holding_days = []
        for trade in trades:
            if trade.entry_time and trade.exit_time:
                days = (trade.exit_time - trade.entry_time).days
                holding_days.append(days)
        avg_holding_days = sum(holding_days) / len(holding_days) if holding_days else 0
    
    # 生成累计盈亏数据
    performance_dates = []
    cumulative_profit_loss = []
    
    if trades:
        sorted_trades = sorted([t for t in trades if t.exit_time], key=lambda x: x.exit_time)
        cumulative = 0
        for trade in sorted_trades:
            if trade.profit_loss:
                cumulative += trade.profit_loss
                performance_dates.append(trade.exit_time.strftime('%Y-%m-%d'))
                cumulative_profit_loss.append(cumulative)
    
    # 如果没有数据，添加一个默认值
    if not performance_dates:
        performance_dates = [datetime.now().strftime('%Y-%m-%d')]
        cumulative_profit_loss = [0]
    
    return render_template('index.html',
                           current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                           pending_count=pending_count,
                           confirmed_count=confirmed_count,
                           recent_pending_trades=recent_pending_trades,
                           profit_trades=profit_trades,
                           loss_trades=loss_trades,
                           total_profit=total_profit,
                           total_loss=total_loss,
                           net_profit=net_profit,
                           win_rate=win_rate,
                           avg_profit_loss_ratio=avg_profit_loss_ratio,
                           avg_holding_days=avg_holding_days,
                           performance_dates=json.dumps(performance_dates),
                           cumulative_profit_loss=json.dumps(cumulative_profit_loss),
                           current_year=datetime.now().year)

@main_bp.route('/health')
def health_check():
    """健康检查路由"""
    return jsonify({
        'status': 'ok',
        'database': 'connected'
    })

@main_bp.route('/pending-trades')
def pending_trades():
    """待处理交易页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 构建查询
    query = PendingTrade.query
    
    # 应用过滤器
    if request.args.get('symbol'):
        query = query.filter(PendingTrade.symbol.ilike(f'%{request.args.get("symbol")}%'))
    if request.args.get('direction'):
        query = query.filter_by(direction=request.args.get('direction'))
    if request.args.get('strategy'):
        query = query.filter(PendingTrade.strategy.ilike(f'%{request.args.get("strategy")}%'))
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    
    # 排序
    query = query.order_by(PendingTrade.timestamp.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    trades = pagination.items
    
    return render_template('pending_trades.html', trades=trades, pagination=pagination)

@main_bp.route('/trades')
def trades():
    """已确认交易页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 构建查询
    query = Trade.query
    
    # 应用过滤器
    if request.args.get('symbol'):
        query = query.filter(Trade.symbol.ilike(f'%{request.args.get("symbol")}%'))
    if request.args.get('direction'):
        query = query.filter_by(direction=request.args.get('direction'))
    if request.args.get('strategy'):
        query = query.filter(Trade.strategy.ilike(f'%{request.args.get("strategy")}%'))
    
    # 排序
    query = query.order_by(Trade.entry_time.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    trades = pagination.items
    
    return render_template('trades.html', trades=trades, pagination=pagination)

@main_bp.route('/pending-trade/<int:trade_id>')
def view_pending_trade(trade_id):
    """查看待处理交易详情"""
    trade = PendingTrade.query.get_or_404(trade_id)
    return render_template('trade_detail.html', trade=trade)

@main_bp.route('/trade/<int:trade_id>')
def view_trade(trade_id):
    """查看已确认交易详情"""
    trade = Trade.query.get_or_404(trade_id)
    return render_template('trade_detail.html', trade=trade)

@main_bp.route('/add-trade', methods=['GET', 'POST'])
def add_trade():
    """添加新交易"""
    if request.method == 'POST':
        try:
            # 获取表单数据
            new_trade = PendingTrade(
                symbol=request.form.get('symbol'),
                direction=request.form.get('direction'),
                price=float(request.form.get('price')) if request.form.get('price') else None,
                timestamp=datetime.strptime(request.form.get('timestamp'), '%Y-%m-%dT%H:%M') if request.form.get('timestamp') else datetime.now(),
                strategy=request.form.get('strategy'),
                status=request.form.get('status', 'pending'),
                notes=request.form.get('notes'),
                
                # 交易分析字段
                current_trend=request.form.get('current_trend'),
                weekly_resistance=request.form.get('weekly_resistance'),
                weekly_support=request.form.get('weekly_support'),
                daily_resistance=request.form.get('daily_resistance'),
                daily_support=request.form.get('daily_support'),
                h4_resistance=request.form.get('h4_resistance'),
                h4_support=request.form.get('h4_support'),
                timeframe=request.form.get('timeframe'),
                risk_reward_ratio=float(request.form.get('risk_reward_ratio')) if request.form.get('risk_reward_ratio') else None,
                entry_price_target=float(request.form.get('entry_price_target')) if request.form.get('entry_price_target') else None,
                stop_loss=float(request.form.get('stop_loss')) if request.form.get('stop_loss') else None,
                take_profit=float(request.form.get('take_profit')) if request.form.get('take_profit') else None,
                support_resistance_reaction=request.form.get('support_resistance_reaction')
            )
            
            db.session.add(new_trade)
            db.session.commit()
            
            flash('交易已成功添加', 'success')
            return redirect(url_for('main.pending_trades'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'添加交易失败: {str(e)}', 'danger')
    
    # GET请求，显示表单
    trade = PendingTrade()
    return render_template('trade_form.html', trade=trade, title='添加交易')

@main_bp.route('/edit-pending-trade/<int:trade_id>', methods=['GET', 'POST'])
def edit_pending_trade(trade_id):
    """编辑待处理交易"""
    trade = PendingTrade.query.get_or_404(trade_id)
    
    if request.method == 'POST':
        try:
            # 更新交易数据
            trade.symbol = request.form.get('symbol')
            trade.direction = request.form.get('direction')
            trade.price = float(request.form.get('price')) if request.form.get('price') else None
            trade.timestamp = datetime.strptime(request.form.get('timestamp'), '%Y-%m-%dT%H:%M') if request.form.get('timestamp') else datetime.now()
            trade.strategy = request.form.get('strategy')
            trade.status = request.form.get('status', 'pending')
            trade.notes = request.form.get('notes')
            
            # 交易分析字段
            trade.current_trend = request.form.get('current_trend')
            trade.weekly_resistance = request.form.get('weekly_resistance')
            trade.weekly_support = request.form.get('weekly_support')
            trade.daily_resistance = request.form.get('daily_resistance')
            trade.daily_support = request.form.get('daily_support')
            trade.h4_resistance = request.form.get('h4_resistance')
            trade.h4_support = request.form.get('h4_support')
            trade.timeframe = request.form.get('timeframe')
            trade.risk_reward_ratio = float(request.form.get('risk_reward_ratio')) if request.form.get('risk_reward_ratio') else None
            trade.entry_price_target = float(request.form.get('entry_price_target')) if request.form.get('entry_price_target') else None
            trade.stop_loss = float(request.form.get('stop_loss')) if request.form.get('stop_loss') else None
            trade.take_profit = float(request.form.get('take_profit')) if request.form.get('take_profit') else None
            trade.support_resistance_reaction = request.form.get('support_resistance_reaction')
            
            db.session.commit()
            
            flash('交易已成功更新', 'success')
            return redirect(url_for('main.view_pending_trade', trade_id=trade.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新交易失败: {str(e)}', 'danger')
    
    # GET请求，显示表单
    return render_template('trade_form.html', trade=trade, title='编辑交易')

@main_bp.route('/confirm-trade/<int:trade_id>')
def confirm_trade(trade_id):
    """确认交易，创建正式交易记录"""
    pending_trade = PendingTrade.query.get_or_404(trade_id)
    
    if pending_trade.status != 'pending':
        flash('只能确认待处理状态的交易', 'warning')
        return redirect(url_for('main.view_pending_trade', trade_id=trade_id))
    
    try:
        # 更新待处理交易状态
        pending_trade.status = 'confirmed'
        
        # 创建新的交易记录
        new_trade = Trade(
            pending_trade_id=pending_trade.id,
            symbol=pending_trade.symbol,
            direction=pending_trade.direction,
            entry_price=pending_trade.price,
            entry_time=pending_trade.timestamp,
            strategy=pending_trade.strategy,
            notes=pending_trade.notes,
            
            # 交易分析字段
            current_trend=pending_trade.current_trend,
            weekly_resistance=pending_trade.weekly_resistance,
            weekly_support=pending_trade.weekly_support,
            daily_resistance=pending_trade.daily_resistance,
            daily_support=pending_trade.daily_support,
            h4_resistance=pending_trade.h4_resistance,
            h4_support=pending_trade.h4_support,
            timeframe=pending_trade.timeframe,
            risk_reward_ratio=pending_trade.risk_reward_ratio,
            stop_loss=pending_trade.stop_loss,
            take_profit=pending_trade.take_profit,
            support_resistance_reaction=pending_trade.support_resistance_reaction
        )
        
        db.session.add(new_trade)
        db.session.commit()
        
        flash('交易已确认并创建正式交易记录', 'success')
        return redirect(url_for('main.view_trade', trade_id=new_trade.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'确认交易失败: {str(e)}', 'danger')
        return redirect(url_for('main.view_pending_trade', trade_id=trade_id))

@main_bp.route('/reject-trade/<int:trade_id>')
def reject_trade(trade_id):
    """拒绝交易"""
    trade = PendingTrade.query.get_or_404(trade_id)
    
    if trade.status != 'pending':
        flash('只能拒绝待处理状态的交易', 'warning')
        return redirect(url_for('main.view_pending_trade', trade_id=trade_id))
    
    try:
        trade.status = 'rejected'
        db.session.commit()
        
        flash('交易已拒绝', 'success')
        return redirect(url_for('main.pending_trades'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'拒绝交易失败: {str(e)}', 'danger')
        return redirect(url_for('main.view_pending_trade', trade_id=trade_id))

@main_bp.route('/delete-pending-trade/<int:trade_id>')
def delete_pending_trade(trade_id):
    """删除待处理交易"""
    trade = PendingTrade.query.get_or_404(trade_id)
    
    try:
        db.session.delete(trade)
        db.session.commit()
        
        flash('交易已删除', 'success')
        return redirect(url_for('main.pending_trades'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'删除交易失败: {str(e)}', 'danger')
        return redirect(url_for('main.view_pending_trade', trade_id=trade_id))

@main_bp.route('/analysis')
def analysis():
    """交易分析页面"""
    # 获取当前日期，用于移动端快速筛选
    now = datetime.now()
    
    # 获取筛选参数
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    symbol = request.args.get('symbol')
    direction = request.args.get('direction')
    
    # 构建查询 - 只查询已完成的交易
    query = Trade.query.filter(Trade.exit_price != None)
    
    # 应用筛选条件
    if date_from:
        query = query.filter(Trade.entry_time >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(Trade.entry_time <= datetime.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    if symbol:
        query = query.filter(Trade.symbol.ilike(f'%{symbol}%'))
    if direction:
        query = query.filter(Trade.direction == direction)
    
    # 获取交易数据
    trades = query.order_by(Trade.entry_time.desc()).all()
    
    # 计算统计数据
    total_trades = len(trades)
    profitable_trades = sum(1 for trade in trades if trade.profit_loss and trade.profit_loss > 0)
    losing_trades = sum(1 for trade in trades if trade.profit_loss and trade.profit_loss < 0)
    
    # 计算胜率和亏损率
    win_rate = f"{profitable_trades / total_trades * 100:.2f}%" if total_trades > 0 else "0%"
    loss_rate = f"{losing_trades / total_trades * 100:.2f}%" if total_trades > 0 else "0%"
    
    # 计算净盈亏
    net_profit_loss = sum(trade.profit_loss or 0 for trade in trades)
    
    # 计算风险管理相关指标
    r_multiples = [trade.r_multiple for trade in trades if trade.r_multiple]
    risk_percentages = [trade.risk_percentage for trade in trades if trade.risk_percentage]
    trade_qualities = [trade.trade_quality for trade in trades if trade.trade_quality]
    
    avg_r_multiple = sum(r_multiples) / len(r_multiples) if r_multiples else 0
    avg_risk_percentage = sum(risk_percentages) / len(risk_percentages) if risk_percentages else 0
    avg_trade_quality = sum(trade_qualities) / len(trade_qualities) if trade_qualities else 0
    
    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = query.order_by(Trade.entry_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    page_trades = pagination.items
    
    return render_template('analysis.html',
                           trades=page_trades,
                           pagination=pagination,
                           total_trades=total_trades,
                           profitable_trades=profitable_trades,
                           losing_trades=losing_trades,
                           win_rate=win_rate,
                           loss_rate=loss_rate,
                           net_profit_loss=f"{net_profit_loss:.2f}",
                           avg_r_multiple=f"{avg_r_multiple:.2f}",
                           avg_risk_percentage=f"{avg_risk_percentage:.2f}",
                           avg_trade_quality=f"{avg_trade_quality:.2f}",
                           now=now,
                           timedelta=timedelta)

@main_bp.route('/trade-review/<int:trade_id>', methods=['GET', 'POST'])
def trade_review(trade_id):
    """交易复盘页面"""
    trade = Trade.query.get_or_404(trade_id)
    
    if request.method == 'POST':
        try:
            # 更新交易复盘信息
            trade.review_date = datetime.now()
            trade.execution_quality = int(request.form.get('execution_quality')) if request.form.get('execution_quality') else None
            trade.psychology_state = request.form.get('psychology_state')
            trade.market_condition = request.form.get('market_condition')
            trade.lessons_learned = request.form.get('lessons_learned')
            trade.improvement_points = request.form.get('improvement_points')
            trade.trade_screenshots = request.form.get('trade_screenshots')
            
            # 处理风险管理相关字段
            trade.trade_quality = int(request.form.get('trade_quality')) if request.form.get('trade_quality') else None
            trade.plan_vs_execution = int(request.form.get('plan_vs_execution')) if request.form.get('plan_vs_execution') else None
            trade.r_multiple = float(request.form.get('r_multiple')) if request.form.get('r_multiple') else None
            
            # 根据已有数据计算其他风险指标
            if trade.profit_loss and trade.initial_risk and trade.initial_risk != 0:
                # 如果没有手动设置R倍数，则自动计算
                if not trade.r_multiple:
                    trade.r_multiple = round(trade.profit_loss / trade.initial_risk, 2)
            
            trade.review_status = 'completed'
            
            db.session.commit()
            
            flash('交易复盘已保存', 'success')
            return redirect(url_for('main.view_trade', trade_id=trade.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'保存复盘失败: {str(e)}', 'danger')
    
    # GET请求，显示复盘表单
    return render_template('trade_review.html', trade=trade)

@main_bp.route('/trade-logs')
def trade_logs():
    """交易日志列表页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 构建查询 - 只显示已复盘的交易
    query = Trade.query.filter_by(review_status='completed')
    
    # 应用过滤器
    if request.args.get('symbol'):
        query = query.filter(Trade.symbol.ilike(f'%{request.args.get("symbol")}%'))
    if request.args.get('direction'):
        query = query.filter_by(direction=request.args.get('direction'))
    if request.args.get('strategy'):
        query = query.filter(Trade.strategy.ilike(f'%{request.args.get("strategy")}%'))
    if request.args.get('start_date') and request.args.get('end_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        query = query.filter(Trade.entry_time.between(start_date, end_date))
    
    # 排序
    query = query.order_by(Trade.review_date.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    trades = pagination.items
    
    return render_template('trade_logs.html', trades=trades, pagination=pagination)

@main_bp.route('/generate-log', methods=['GET', 'POST'])
def generate_log():
    """生成交易日志报告"""
    if request.method == 'POST':
        # 获取表单数据
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        symbol = request.form.get('symbol')
        strategy = request.form.get('strategy')
        direction = request.form.get('direction')
        include_screenshots = 'include_screenshots' in request.form
        
        # 构建查询
        query = Trade.query
        
        # 应用过滤器
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Trade.entry_time.between(start_date, end_date))
        if symbol:
            query = query.filter(Trade.symbol.ilike(f'%{symbol}%'))
        if strategy:
            query = query.filter(Trade.strategy.ilike(f'%{strategy}%'))
        if direction:
            query = query.filter_by(direction=direction)
        
        # 只包含已复盘的交易
        query = query.filter_by(review_status='completed')
        
        # 排序
        query = query.order_by(Trade.entry_time.desc())
        
        # 获取交易
        trades = query.all()
        
        if not trades:
            flash('没有找到符合条件的交易记录', 'warning')
            return redirect(url_for('main.generate_log'))
        
        # 计算统计数据
        total_trades = len(trades)
        profit_trades = sum(1 for trade in trades if trade.profit_loss and trade.profit_loss > 0)
        loss_trades = sum(1 for trade in trades if trade.profit_loss and trade.profit_loss <= 0)
        win_rate = (profit_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(trade.profit_loss for trade in trades if trade.profit_loss and trade.profit_loss > 0) or 0
        total_loss = sum(trade.profit_loss for trade in trades if trade.profit_loss and trade.profit_loss <= 0) or 0
        net_profit = total_profit + total_loss
        
        # 生成报告
        return render_template('trade_log_report.html', 
                              trades=trades, 
                              total_trades=total_trades,
                              profit_trades=profit_trades,
                              loss_trades=loss_trades,
                              win_rate=win_rate,
                              total_profit=total_profit,
                              total_loss=total_loss,
                              net_profit=net_profit,
                              include_screenshots=include_screenshots,
                              start_date=start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else start_date,
                              end_date=end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date)
    
    # GET请求，显示生成报告的表单
    return render_template('generate_log_form.html')

# API路由，用于获取JSON数据

@main_bp.route('/api/pending-trades', methods=['GET'])
def get_pending_trades():
    """获取所有待处理交易"""
    trades = PendingTrade.query.order_by(PendingTrade.timestamp.desc()).all()
    return jsonify({
        'status': 'success',
        'count': len(trades),
        'data': [trade.to_dict() for trade in trades]
    })

@main_bp.route('/api/trades', methods=['GET'])
def get_trades():
    """获取所有已确认交易"""
    trades = Trade.query.order_by(Trade.entry_time.desc()).all()
    return jsonify({
        'status': 'success',
        'count': len(trades),
        'data': [trade.to_dict() for trade in trades]
    })

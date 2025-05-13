# 本地交易日志系统

这是一个用于记录和管理交易信号与结果的本地系统。系统接收来自 TradingView 的 webhook 信号，并提供界面进行交易管理。

## 功能特点

- 接收并存储 TradingView webhook 发送的交易信号
- 管理待处理交易和已确认交易
- 记录交易详情，包括进出场价格、盈亏等信息
- 支持详细的交易分析参数（趋势、支撑阻力位、盈亏比等）
- 基于 Flask 和 PostgreSQL 构建，易于扩展

## 项目结构

```bash
trading_log_system/
│
├── .env                    # 环境变量配置文件
├── .gitignore              # Git忽略文件
├── README.md               # 项目说明文档
├── requirements.txt        # 项目依赖
│
├── app/                    # 应用主目录
│   ├── __init__.py         # 应用初始化
│   ├── config.py           # 配置加载
│   ├── models.py           # 数据模型
│   ├── routes.py           # API路由
│   ├── utils.py            # 工具函数
│   │
│   ├── api/                # API模块
│   │   ├── __init__.py
│   │   └── webhook.py      # Webhook处理
│   │
│   └── templates/          # 前端模板(后续扩展)
│
├── migrations/             # 数据库迁移文件
│
└── run.py                  # 应用启动脚本
```

## 数据库结构

系统使用两个主要数据表：

1. `pending_trades` - 存储从 TradingView 接收的交易信号
   - id: 唯一标识符
   - symbol: 交易品种
   - direction: 交易方向 (买入/卖出)
   - price: 信号价格
   - timestamp: 信号时间
   - strategy: 策略名称
   - status: 信号状态
   - notes: 备注信息
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

2. `trades` - 存储已确认的交易记录
   - id: 唯一标识符
   - pending_trade_id: 关联的待处理交易ID
   - symbol: 交易品种
   - direction: 交易方向
   - entry_price: 入场价格
   - exit_price: 出场价格
   - entry_time: 入场时间
   - exit_time: 出场时间
   - profit_loss: 盈亏金额
   - profit_loss_percent: 盈亏百分比
   - strategy: 策略名称
   - notes: 交易笔记
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

## TradingView 联动说明

系统通过 webhook 与 TradingView 进行联动，具体操作步骤如下：

### 在 TradingView 中设置

1. **创建策略或指标**：在 TradingView 图表上创建你的交易策略或指标

2. **设置 Alert（警报）**：
   - 点击“警报”按钮创建新警报
   - 设置触发条件（例如：当价格突破移动平均线时）
   - 在“通知”选项中，选择 "Webhook URL"
   - 输入本系统的 webhook 地址：`http://你的服务器地址:5001/api/webhook`

3. **设置消息格式**：
   - 在“消息”框中，输入 JSON 格式的数据，例如：

```json
{
  "symbol": "BTCUSDT",
  "direction": "buy",
  "price": 50000,
  "strategy": "突破策略",
  "current_trend": "上涨",
  "weekly_resistance": "52000",
  "weekly_support": "48000",
  "daily_resistance": "51000",
  "daily_support": "49000",
  "h4_resistance": "50500",
  "h4_support": "49500",
  "timeframe": "4h",
  "risk_reward_ratio": 2.5,
  "stop_loss": 49000,
  "take_profit": 53000
}
```

### 必要字段说明

- **symbol**：交易品种代码（必填）
- **direction**：交易方向，buy 或 sell（必填）
- **price**：信号价格（必填）

其他字段都是可选的，用于提供更详细的交易分析信息。

## 如何查看数据库

系统默认使用 SQLite 数据库（也支持 PostgreSQL），你可以通过以下方式查看数据库内容：

### 1. 使用 SQLite 命令行工具

```bash
# 在项目根目录下执行
$ sqlite3 trading_log.db

# 查看表结构
> .schema

# 查看待处理交易
> SELECT * FROM pending_trades;

# 查看已确认交易
> SELECT * FROM trades;

# 退出
> .exit
```

### 2. 使用图形界面工具

推荐使用 [DB Browser for SQLite](https://sqlitebrowser.org/)（免费开源）：

- 下载并安装 DB Browser for SQLite
- 打开 `trading_log.db` 文件
- 浏览表结构和数据

### 3. 通过系统前端界面

- 访问 [`http://localhost:5001`](http://localhost:5001)
- 使用系统提供的界面查看和管理交易记录

## 安装与设置

### 前提条件

- Python 3.8+
- SQLite (默认) 或 PostgreSQL 数据库

### 安装步骤

1. **克隆仓库**

   ```bash
   # 克隆仓库
   git clone https://github.com/yourusername/trading-log-system.git
   cd trading-log-system
   ```

1. **创建虚拟环境**

   ```bash
   # 创建虚拟环境
   python -m venv venv

   # 激活虚拟环境
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

1. **初始化数据库**

   ```bash
   # 设置 Flask 应用
   export FLASK_APP=run.py

   # 初始化数据库迁移
   flask db init
   flask db migrate -m "初始化数据库表结构"
   flask db upgrade
   ```

1. **运行应用**

   ```bash
   python run.py
   ```

应用将在 [`http://localhost:5001`](http://localhost:5001) 上运行。

### 使用说明

1. **浏览交易信号**
   - 访问首页查看系统概览和最近交易信号
   - 点击“待处理交易”查看所有待处理的交易信号

2. **管理交易信号**
   - 确认信号：将待处理交易转换为正式交易
   - 拒绝信号：将信号标记为已拒绝
   - 编辑信号：修改信号的各项参数

3. **记录交易结果**
   - 输入出场价格和时间
   - 系统自动计算盈亏金额和百分比

4. **分析交易数据**
   - 查看交易统计信息
   - 分析交易成功率和盈亏比

## 交易分析字段说明

系统支持以下交易分析字段，用于进行更全面的交易决策：

1. **当前价格**：自动填入当前市场价格

2. **当前趋势**：上涨/下跌/震荡

3. **支撑阻力位**：
   - 周线支撑阻力位
   - 日线支撑阻力位
   - 4小时支撑阻力位

4. **交易时间周期**：考虑交易的时间周期

5. **盈亏比分析**：
   - 盈亏比值（如 3 或 4）
   - 目标进场价格
   - 止损价格
   - 止盈价格

6. **K线反应**：在K线触及支撑阻力位时的反应情况

这些字段可以帮助你在小区间交易中更好地评估风险和收益潜力。

## 后续开发计划

- 添加用户认证系统
- 开发前端界面，实现可视化交易管理
- 集成交易分析和统计功能
- 添加AI辅助决策模块

## 许可证

MIT

## 作者

[您的名字]

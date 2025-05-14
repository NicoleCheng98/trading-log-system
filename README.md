# 本地交易日志系统

这是一个用于记录和管理交易信号与结果的本地系统。系统接收来自 TradingView 的 webhook 信号，并提供界面进行交易管理。

## 功能特点

- 接收并存储 TradingView webhook 发送的交易信号
- 管理待处理交易和已确认交易
- 记录交易详情，包括进出场价格、盈亏等信息
- 支持详细的交易分析参数（趋势、支撑阻力位、盈亏比等）
- 提供完善的风险管理功能，包括账户资金管理、风险控制和R倍数计算
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
   - account_size: 交易时的账户总资金
   - risk_percentage: 风险占账户百分比
   - position_size: 仓位大小
   - r_multiple: R倍数(盈亏与初始风险的比值)
   - initial_risk: 初始风险金额
   - plan_vs_execution: 计划执行一致性评分(1-10)
   - trade_quality: 交易质量评分(1-10)

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

## 风险管理功能

本系统提供了完善的风险管理功能，帮助交易者更好地控制交易风险，提高交易成功率。

### 风险管理字段

系统包含以下风险管理相关字段：

1. **账户总资金**：交易时的账户总资金量

2. **风险百分比**：单笔交易风险占账户总资金的百分比（建议控制在1-2%以内）

3. **初始风险金额**：根据账户总资金和风险百分比自动计算的单笔交易风险金额

4. **仓位大小**：根据初始风险金额、入场价格和止损价格自动计算的合适仓位大小

5. **R倍数**：交易盈亏与初始风险的比值，用于衡量交易效率

6. **计划执行一致性**：评估交易计划与实际执行的一致程度（1-10分）

7. **交易质量评分**：对交易整体质量的评估（1-10分）

### 风险计算器

系统集成了自动风险计算器，可以实时计算以下数据：

1. **初始风险计算**：输入账户总资金和风险百分比，自动计算初始风险金额
   ```
   初始风险 = 账户总资金 × 风险百分比 ÷ 100
   ```

2. **仓位大小计算**：根据初始风险、入场价格和止损价格计算合适的仓位大小
   ```
   每单位风险 = |入场价格 - 止损价格|
   仓位大小 = 初始风险 ÷ 每单位风险
   ```

3. **R倍数计算**：根据盈亏金额和初始风险计算R倍数
   ```
   R倍数 = 盈亏金额 ÷ 初始风险
   ```

### 使用方法

1. **交易前的风险管理**：
   - 在交易表单的“风险管理”选项卡中输入账户总资金和风险百分比
   - 系统自动计算初始风险金额
   - 输入入场价格和止损价格后，系统自动计算合适的仓位大小

2. **交易后的风险评估**：
   - 交易完成后，系统根据实际盈亏和初始风险自动计算R倍数
   - 在交易复盘页面中评估交易质量和计划执行一致性

3. **交易详情查看**：
   - 在交易详情页面中查看完整的风险管理数据
   - 系统会使用颜色编码（绿色、黄色、红色）直观显示风险指标的好坏

### 风险管理最佳实践

1. **控制单笔交易风险**：将单笔交易风险控制在1-2%以内，避免过大风险

2. **关注R倍数**：追求更高的R倍数，提高交易效率

3. **定期评估交易质量**：使用交易质量评分和计划执行一致性评分进行自我审视

4. **追踪账户增长**：定期更新账户总资金，跟踪账户增长情况

## VPS 部署指南

系统已经成功部署在服务器上，可以通过 [`http://46.250.226.112`](http://46.250.226.112) 访问。以下是完整的部署步骤，便于你在其他服务器上部署相同的系统。

### 第一步：连接到 VPS

```bash
ssh root@你的服务器IP
```

### 第二步：更新系统并安装必要的软件包

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装必要的软件包
sudo apt install -y python3-pip python3-venv git nginx
```

### 第三步：创建项目目录并克隆代码

```bash
# 创建项目目录
mkdir -p /var/www/trading_log
cd /var/www/trading_log

# 克隆代码
git clone https://github.com/NicoleCheng98/trading-log-system.git .
```

### 第四步：设置 Python 虚拟环境并安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 gunicorn（用于生产环境部署）
pip install gunicorn
```

### 第五步：配置数据库

```bash
# 设置 Flask 应用
export FLASK_APP=run.py

# 初始化数据库
flask db init
flask db migrate -m "初始化数据库表结构"
flask db upgrade
```

### 第六步：配置 Gunicorn 服务

创建 Gunicorn 服务文件：

```bash
sudo nano /etc/systemd/system/trading_log.service
```

添加以下内容：

```ini
[Unit]
Description=Gunicorn instance to serve trading log system
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/trading_log
Environment="PATH=/var/www/trading_log/venv/bin"
ExecStart=/var/www/trading_log/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5001 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动并设置开机自启：

```bash
sudo systemctl start trading_log
sudo systemctl enable trading_log
```

### 第七步：配置 Nginx 反向代理

创建 Nginx 配置文件：

```bash
sudo nano /etc/nginx/sites-available/trading_log
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name 46.250.226.112;  # 你的服务器 IP

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置并重启 Nginx：

```bash
sudo ln -s /etc/nginx/sites-available/trading_log /etc/nginx/sites-enabled
sudo nginx -t  # 测试配置是否正确
sudo systemctl restart nginx
```

### 第八步：配置防火墙

```bash
# 允许 SSH、HTTP 和 HTTPS 连接
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# 启用防火墙
sudo ufw enable
```

### 第九步：测试系统

现在，你可以通过浏览器访问你的交易日志系统：

```text
http://46.250.226.112
```

### 第十步：配置 TradingView Webhook

在 TradingView 中设置 webhook URL 为：

```text
http://46.250.226.112/api/webhook
```

### 交易复盘与日志功能

本系统提供了完整的交易复盘和日志生成功能，帮助交易者分析过去的交易，总结经验教训，提高交易水平。

#### 交易复盘功能

交易复盘功能允许用户对已完成的交易进行详细的复盘评估，包括：

- 执行质量评分：对交易执行质量进行1-10分的评分
- 交易心理状态：记录交易时的心理状态（冷静、恐惧、贪婪等）
- 市场条件：记录交易时的市场环境（强势上涨、强势下跌、震荡整理等）
- 经验教训：记录从本次交易中学到的经验和教训
- 改进点：记录下次交易需要改进的地方
- 交易截图：上传交易相关的截图路径，方便后续查看

使用方法：

1. 在已确认交易列表中找到需要复盘的交易
2. 点击"编辑复盘"按钮进入复盘页面
3. 填写复盘表单并保存

#### 交易日志功能

交易日志功能允许用户查看所有已复盘的交易记录，并生成综合报告：

- 交易日志列表：显示所有已复盘的交易记录，支持按品种、方向、策略、日期等筛选
- 日志报告生成：根据筛选条件生成详细的交易日志报告
- 报告打印：支持将生成的报告打印或保存为PDF文件

使用方法：

1. 点击导航栏中的"交易日志"查看所有已复盘的交易记录
2. 点击"生成报告"按钮，设置筛选条件生成交易日志报告
3. 在报告页面点击"打印报告"按钮，可以打印或保存为PDF文件

### 系统维护

定期备份数据库：

```bash
# 备份 SQLite 数据库
mkdir -p /var/www/trading_log/backups
cp /var/www/trading_log/trading_log.db /var/www/trading_log/backups/trading_log_$(date +%Y%m%d).db
```

### 故障排除

如果系统无法正常工作，可以查看日志：

```bash
# 查看 Gunicorn 服务日志
sudo journalctl -u trading_log

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/error.log
```

## 后续开发计划

- 添加用户认证系统
- 开发前端界面，实现可视化交易管理
- 集成交易分析和统计功能
- 添加AI辅助决策模块

## 许可证

MIT

## 作者

[您的名字]

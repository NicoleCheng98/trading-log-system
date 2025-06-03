# 交易日志系统 - 简易安装指南

这是一个专为初学者设计的交易日志系统安装指南。按照以下步骤，即使没有任何编程基础，也能成功安装和使用系统。

## 安装步骤

### 第一步：下载代码

1. **安装Git**
   - 访问 https://git-scm.com/downloads
   - 下载适合您系统的Git安装包
   - 安装时全部选择默认选项

2. **下载项目代码**
   - 打开"终端"(Mac)或"命令提示符"(Windows)
   - 输入以下命令：
   ```
   git clone https://github.com/NicoleCheng98/trading-log-system.git
   cd trading-log-system
   ```

### 第二步：安装Python

1. **下载Python**
   - 访问 https://www.python.org/downloads/
   - 下载Python 3.10版本
   - 安装时勾选"Add Python to PATH"选项（非常重要！）

### 第三步：安装依赖和设置环境

1. **创建虚拟环境**

   **Windows系统**:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   **Mac系统**:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **安装依赖**
   ```
   pip install -r requirements.txt
   ```

   如果上面的命令出错，可以尝试：
   ```
   pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-WTF Flask-Cors python-dotenv marshmallow
   ```

3. **设置环境变量**

   **Windows系统**:
   ```
   set FLASK_APP=app
   ```

   **Mac系统**:
   ```
   export FLASK_APP=app
   ```

4. **初始化数据库**
   ```
   flask db init
   flask db migrate -m "初始化数据库"
   flask db upgrade
   ```

### 第四步：运行应用

1. **启动应用**

   **Windows系统**:
   ```
   python run.py
   ```

   **Mac系统**:
   ```
   python3 run.py
   ```

2. **访问应用**
   - 打开浏览器，输入：`http://127.0.0.1:5001`

## 常见问题解决

### 1. "找不到模块"错误
解决方法：确保已激活虚拟环境，然后运行：
```
pip install 模块名
```

### 2. 数据库错误
解决方法：删除`trading_log.db`文件，然后重新运行：
```
flask db init
flask db migrate -m "初始化数据库"
flask db upgrade
```

### 3. 端口被占用
解决方法：修改`run.py`文件中的端口号，例如从5001改为5002。

## 使用提示

1. 保持终端窗口打开，否则应用会停止运行
2. 每次使用前需要激活虚拟环境
3. 使用Ctrl+C停止应用

如有任何问题，请联系系统管理员获取帮助。

@echo off
REM CalEE 启动脚本 (Windows)

cd backend

REM 检查虚拟环境
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 运行应用
echo 启动 CalEE...
python -m app.main

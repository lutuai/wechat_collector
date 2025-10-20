@echo off
chcp 65001 > nul
echo 微信公众号文章采集器
echo ==================

REM 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.x
    pause
    exit /b 1
)

REM 检查依赖包
echo 检查依赖包...
pip show requests > nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖包安装失败，请检查网络连接
        pause
        exit /b 1
    )
)

REM 运行程序
echo 启动程序...
python main.py

pause

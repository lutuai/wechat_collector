#!/bin/bash

echo "微信公众号文章采集器"
echo "=================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.x"
    exit 1
fi

# 检查依赖包
echo "检查依赖包..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "依赖包安装失败，请检查网络连接"
        exit 1
    fi
fi

# 运行程序
echo "启动程序..."
python3 main.py

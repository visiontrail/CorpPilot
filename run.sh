#!/bin/bash

# CostMatrix API 启动脚本

echo "========================================"
echo "   CostMatrix API 启动脚本"
echo "========================================"

# 检查 Python 版本
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python 版本: $PYTHON_VERSION"

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "发现虚拟环境，正在激活..."
    source venv/bin/activate
else
    echo "未发现虚拟环境，建议创建:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    read -p "是否继续使用全局 Python 环境？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查依赖
echo "检查依赖..."
pip show fastapi > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "未安装依赖，正在安装..."
    pip install -r requirements.txt
fi

# 启动服务
echo ""
echo "========================================"
echo "   启动 FastAPI 服务..."
echo "========================================"
echo "服务地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"
echo ""

python main.py



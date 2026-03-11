#!/bin/bash

# 邮件发送系统启动脚本

echo "======================================"
echo "Mail Sender API - Startup Script"
echo "======================================"

# 检查依赖
echo "✓ Checking dependencies..."
pip install -r requirements.txt

# 初始化数据库
echo "✓ Initializing database..."
python -c "from app.database import init_db; init_db()"

# 启动 Celery Worker
echo "✓ Starting Celery Worker..."
celery -A app.tasks worker --loglevel=info &

# 等待 Celery 启动
sleep 2

# 启动 FastAPI 应用
echo "✓ Starting FastAPI Application..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 10001 --reload

echo "======================================"
echo "✓ Services started successfully!"
echo "API available at: http://localhost:10001"
echo "API Docs: http://localhost:10001/docs"
echo "======================================"

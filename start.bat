@echo off

REM Start Redis (if using local Redis)
start redis-server.exe

REM Start Celery worker
start celery -A tasks.celery worker --loglevel=info

REM Start Flask app
python app.py

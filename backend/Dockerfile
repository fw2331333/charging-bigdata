FROM python:3.11-slim

WORKDIR /app

# 使用 PyMySQL，无需 apt 安装 gcc / libmysqlclient
COPY backend/requirements.txt .
RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -r requirements.txt

COPY backend/app ./app
COPY backend/main.py .
COPY sql/migrations/009_v6_v7_manual_align.sql ./sql/migrations/009_v6_v7_manual_align.sql
# 预测服务依赖 analytics.ml_data（Docker 内与本地目录结构一致）
COPY analytics/__init__.py analytics/ml_data.py analytics/hdfs_io.py ./analytics/

RUN mkdir -p /app/analytics/output/models

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MYSQL_HOST=mysql \
    MYSQL_PORT=3306 \
    MYSQL_USER=root \
    MYSQL_DATABASE=charging_bigdata \
    ANALYTICS_OUTPUT_DIR=/app/analytics/output

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

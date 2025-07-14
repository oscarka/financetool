# 使用多阶段构建优化部署速度和镜像大小
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖（编译需要）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 升级pip并安装依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 第二阶段：运行时镜像
FROM python:3.11-slim as runtime

# 设置工作目录
WORKDIR /app

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制应用代码
COPY . .

# 确保数据和日志目录存在，并设置正确的权限
RUN mkdir -p data logs backups && \
    chmod 755 data logs backups

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app && \
    chmod -R 755 /app/data /app/logs /app/backups

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 数据持久化相关环境变量
ENV DATABASE_PERSISTENT_PATH=/app/data
ENV DATABASE_BACKUP_ENABLED=true
ENV DATABASE_BACKUP_INTERVAL_HOURS=24

# Railway环境检测
ENV RAILWAY_ENVIRONMENT=production

# 暴露端口
EXPOSE 8000

# 切换到非root用户
USER app

# 启动命令
CMD ["python", "run.py"]
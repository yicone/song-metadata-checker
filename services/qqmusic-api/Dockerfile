# QQ 音乐 API Dockerfile
# 基于 Python 的简单 API 服务器

FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 3001

# 启动服务
CMD ["python", "server.py"]

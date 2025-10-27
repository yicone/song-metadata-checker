#!/bin/bash

# Nginx + ngrok API 网关设置脚本
# 用途: 将 NetEase API (3000) 和 QQ Music API (3001) 合并到一个端口 (8080)

set -e

echo "🚀 开始设置 Nginx API 网关..."
echo ""

# 步骤 1: 停止并删除旧的 nginx-proxy 容器（如果存在）
echo "📦 清理旧容器..."
docker stop nginx-proxy 2>/dev/null || true
docker rm nginx-proxy 2>/dev/null || true
echo "✅ 清理完成"
echo ""

# 步骤 2: 创建 Nginx 配置文件
echo "📝 创建 Nginx 配置..."
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    server {
        listen 8080;
        server_name localhost;

        # NetEase API - 路径前缀 /netease
        location /netease/ {
            # 移除 /netease 前缀并转发到后端
            rewrite ^/netease/(.*) /$1 break;
            proxy_pass http://localhost:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # QQ Music API - 路径前缀 /qqmusic
        location /qqmusic/ {
            # 移除 /qqmusic 前缀并转发到后端
            rewrite ^/qqmusic/(.*) /$1 break;
            proxy_pass http://localhost:3001;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 健康检查端点
        location /health {
            access_log off;
            return 200 "OK\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
echo "✅ 配置文件已创建: nginx.conf"
echo ""

# 步骤 3: 检查 API 服务是否运行
echo "🔍 检查 API 服务状态..."
if curl -s http://localhost:3000/song/detail?ids=2758218600 > /dev/null 2>&1; then
    echo "✅ NetEase API (端口 3000) 正在运行"
else
    echo "⚠️  NetEase API (端口 3000) 未响应"
    echo "   请先启动: cd services/netease-api && docker-compose up -d"
fi

if curl -s http://localhost:3001/search?key=test > /dev/null 2>&1; then
    echo "✅ QQ Music API (端口 3001) 正在运行"
else
    echo "⚠️  QQ Music API (端口 3001) 未响应"
    echo "   请先启动: cd services/qqmusic-api && docker-compose up -d"
fi
echo ""

# 步骤 4: 启动 Nginx 容器
echo "🐳 启动 Nginx 代理容器..."
docker run -d \
  --name nginx-proxy \
  --network host \
  -v "$(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro" \
  nginx:alpine

echo "✅ Nginx 代理已启动"
echo ""

# 步骤 5: 等待 Nginx 启动
echo "⏳ 等待 Nginx 启动..."
sleep 3

# 步骤 6: 测试代理
echo "🧪 测试 Nginx 代理..."
echo ""

echo "测试 1: 健康检查"
if curl -s http://localhost:8080/health | grep -q "OK"; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败"
fi

echo ""
echo "测试 2: NetEase API 代理"
NETEASE_RESULT=$(curl -s "http://localhost:8080/netease/song/detail?ids=2758218600" | jq -r '.songs[0].name' 2>/dev/null || echo "失败")
if [ "$NETEASE_RESULT" != "失败" ] && [ -n "$NETEASE_RESULT" ]; then
    echo "✅ NetEase API 代理成功"
    echo "   歌曲名称: $NETEASE_RESULT"
else
    echo "❌ NetEase API 代理失败"
    echo "   请检查 Nginx 日志: docker logs nginx-proxy"
fi

echo ""
echo "测试 3: QQ Music API 代理"
QQMUSIC_RESULT=$(curl -s "http://localhost:8080/qqmusic/search?key=test" | jq -r '.result' 2>/dev/null || echo "失败")
if [ "$QQMUSIC_RESULT" != "失败" ]; then
    echo "✅ QQ Music API 代理成功"
else
    echo "❌ QQ Music API 代理失败"
    echo "   请检查 Nginx 日志: docker logs nginx-proxy"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Nginx 代理设置完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 本地访问地址:"
echo "   - NetEase API: http://localhost:8080/netease/"
echo "   - QQ Music API: http://localhost:8080/qqmusic/"
echo "   - 健康检查: http://localhost:8080/health"
echo ""
echo "🌐 下一步: 使用 ngrok 暴露到公网"
echo ""
echo "   运行命令:"
echo "   $ ngrok http 8080"
echo ""
echo "   然后在 Dify Cloud 中配置环境变量:"
echo "   NETEASE_API_HOST=https://your-ngrok-url.ngrok.io/netease"
echo "   QQ_MUSIC_API_HOST=https://your-ngrok-url.ngrok.io/qqmusic"
echo ""
echo "💡 管理命令:"
echo "   - 查看日志: docker logs -f nginx-proxy"
echo "   - 停止代理: docker stop nginx-proxy"
echo "   - 重启代理: docker restart nginx-proxy"
echo "   - 删除代理: docker stop nginx-proxy && docker rm nginx-proxy"
echo ""

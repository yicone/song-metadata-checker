# ✅ Nginx API 网关设置成功

> **⚠️ 文档已归档 / ARCHIVED**  
> 本文档已整合到 Dify Cloud 快速开始指南。  
> 请参考最新文档：[docs/guides/DIFY_CLOUD_QUICK_START.md](docs/guides/DIFY_CLOUD_QUICK_START.md)
>
> **归档原因**：
>
> - Nginx 配置已整合到 Dify Cloud 部署流程
> - 内容与 DIFY_CLOUD_QUICK_START.md 重复
> - 归档日期：2025-01-27

## 📊 当前状态

**Nginx 代理**: ✅ 运行中  
**本地端口**: 8888  
**容器名称**: nginx-proxy

## 🔗 本地访问地址

| 服务             | URL                            | 状态    |
| ---------------- | ------------------------------ | ------- |
| **健康检查**     | <http://localhost:8888/health>   | ✅ 正常 |
| **NetEase API**  | <http://localhost:8888/netease/> | ✅ 正常 |
| **QQ Music API** | <http://localhost:8888/qqmusic/> | ✅ 正常 |

## 🧪 测试结果

```bash
# 健康检查
$ curl http://localhost:8888/health
OK

# NetEase API 测试
$ curl "http://localhost:8888/netease/song/detail?ids=2758218600" | jq -r '.songs[0].name'
顽疾 (Live)  ✅

# QQ Music API 测试
$ curl "http://localhost:8888/qqmusic/search?key=test&pageSize=1"
{"result": ...}  ✅
```

---

## 🌐 下一步: 使用 ngrok 暴露到公网

### 步骤 1: 启动 ngrok

```bash
ngrok http 8888
```

### 步骤 2: 复制 HTTPS URL

ngrok 会显示类似以下输出:

```
Forwarding  https://abc123-456-789.ngrok-free.app -> http://localhost:8888
```

复制 HTTPS URL: `https://abc123-456-789.ngrok-free.app`

### 步骤 3: 在 Dify Cloud 配置环境变量

在 Dify Cloud 工作流设置中添加:

```bash
NETEASE_API_HOST=https://abc123-456-789.ngrok-free.app/netease
QQ_MUSIC_API_HOST=https://abc123-456-789.ngrok-free.app/qqmusic
```

**⚠️ 重要**:

- 替换 `abc123-456-789.ngrok-free.app` 为你的实际 ngrok URL
- URL 末尾包含 `/netease` 和 `/qqmusic` 路径前缀

### 步骤 4: 测试公网访问

```bash
# 替换为你的 ngrok URL
NGROK_URL="https://abc123-456-789.ngrok-free.app"

# 测试健康检查
curl "$NGROK_URL/health"

# 测试 NetEase API
curl "$NGROK_URL/netease/song/detail?ids=2758218600"

# 测试 QQ Music API
curl "$NGROK_URL/qqmusic/search?key=test"
```

---

## 💡 管理命令

### 查看日志

```bash
# 实时查看日志
docker logs -f nginx-proxy

# 查看最近 50 行
docker logs --tail 50 nginx-proxy
```

### 重启代理

```bash
docker restart nginx-proxy
```

### 停止代理

```bash
docker stop nginx-proxy
```

### 删除代理

```bash
docker stop nginx-proxy && docker rm nginx-proxy
```

### 重新创建代理

```bash
# 停止并删除
docker stop nginx-proxy && docker rm nginx-proxy

# 重新启动
docker run -d \
  --name nginx-proxy \
  -p 8888:8888 \
  -v "$(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro" \
  nginx:alpine
```

---

## 📝 配置文件

**位置**: `/Users/tr/Workspace/song-metadata-checker/nginx.conf`

**关键配置**:

```nginx
server {
    listen 8888;

    # NetEase API
    location /netease/ {
        rewrite ^/netease/(.*) /$1 break;
        proxy_pass http://host.docker.internal:3000;
    }

    # QQ Music API
    location /qqmusic/ {
        rewrite ^/qqmusic/(.*) /$1 break;
        proxy_pass http://host.docker.internal:3001;
    }
}
```

---

## ⚠️ ngrok 免费版限制

- **会话时长**: 每 2 小时断开一次
- **URL 变化**: 每次重启 URL 都会改变
- **需要更新**: 重启后需要更新 Dify Cloud 环境变量

### 解决方案

**临时测试**: 接受限制，手动重启  
**长期使用**: 考虑以下选项

1. **ngrok 付费版** ($8/月)
   - 固定域名
   - 无时间限制

2. **Cloudflare Tunnel** (免费)
   - 完全免费
   - 稳定不断线
   - 需要域名

3. **云服务器部署** (推荐生产环境)
   - 完全控制
   - 固定 IP/域名
   - 成本: $10-30/月

---

## 🔧 故障排除

### 问题 1: 无法访问 API

**检查清单**:

```bash
# 1. 检查 Nginx 是否运行
docker ps | grep nginx-proxy

# 2. 检查端口是否监听
lsof -i :8888

# 3. 检查后端 API 是否运行
curl http://localhost:3000/song/detail?ids=2758218600
curl http://localhost:3001/search?key=test

# 4. 查看 Nginx 日志
docker logs nginx-proxy
```

### 问题 2: 502 Bad Gateway

**原因**: 后端 API 未运行

**解决**:

```bash
# 启动 NetEase API
cd services/netease-api && docker-compose up -d

# 启动 QQ Music API
cd services/qqmusic-api && docker-compose up -d
```

### 问题 3: ngrok 连接失败

**检查**:

```bash
# 确保 ngrok 指向正确端口
ngrok http 8888  # 不是 8080!
```

---

## 📚 相关文档

- [Dify Cloud 快速开始](docs/guides/DIFY_CLOUD_QUICK_START.md)
- [Dify Cloud 故障排除](docs/guides/DIFY_CLOUD_TROUBLESHOOTING.md)
- [完整手动创建指南](docs/guides/DIFY_CLOUD_MANUAL_SETUP.md)

---

**创建时间**: 2025-10-27  
**状态**: ✅ 运行中  
**端口**: 8888

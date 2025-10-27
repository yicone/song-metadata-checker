# QQ Music API 容器化设置指南

> **目标**: 在容器内运行 Rain120 QQ Music API，无需在本机安装 Node.js

## 🏗️ 架构

```
┌─────────────────────────────────────┐
│  Docker Compose                     │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │ qqmusic-upstream             │  │
│  │ (Rain120 API)                │  │
│  │ - Node.js 18                 │  │
│  │ - Port: 3300                 │  │
│  │ - Volume: ./volumes/qq-music │  │
│  └──────────────────────────────┘  │
│            ↓                        │
│  ┌──────────────────────────────┐  │
│  │ qqmusic-api                  │  │
│  │ (Proxy Layer)                │  │
│  │ - Python Flask               │  │
│  │ - Port: 3001                 │  │
│  │ - Forwards to upstream       │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

---

## 🚀 快速开始

### 步骤 1: 克隆 Rain120 API

```bash
cd services/qqmusic-api

# 运行设置脚本
chmod +x setup-upstream.sh
./setup-upstream.sh
```

这会将 Rain120/qq-music-api 克隆到 `./volumes/qq-music-api/`

### 步骤 2: 启动容器化服务

```bash
# 启动完整服务（上游 + 代理）
docker-compose -f docker-compose-with-upstream.yml up -d
```

### 步骤 3: 等待服务就绪

```bash
# 查看日志
docker-compose -f docker-compose-with-upstream.yml logs -f

# 等待看到:
# qqmusic-upstream | Server running at http://0.0.0.0:3300
# qqmusic-api      | QQ Music API Proxy starting on port 3001...
```

**⏱️ 首次启动**: 需要 1-2 分钟安装 npm 依赖

### 步骤 4: 测试服务

```bash
# 测试上游 API (直接访问 Rain120)
curl "http://localhost:3300/getSearchByKey?key=周杰伦&pageSize=5"

# 测试代理 API (通过 Flask 代理) - 推荐
curl "http://localhost:3001/search?key=周杰伦&pageSize=5"
```

---

## 📋 管理命令

### 启动服务

```bash
docker-compose -f docker-compose-with-upstream.yml up -d
```

### 停止服务

```bash
docker-compose -f docker-compose-with-upstream.yml down
```

### 查看日志

```bash
# 所有服务
docker-compose -f docker-compose-with-upstream.yml logs -f

# 仅上游 API
docker-compose -f docker-compose-with-upstream.yml logs -f qqmusic-upstream

# 仅代理
docker-compose -f docker-compose-with-upstream.yml logs -f qqmusic-api
```

### 重启服务

```bash
docker-compose -f docker-compose-with-upstream.yml restart
```

### 重新构建

```bash
# 如果修改了代码
docker-compose -f docker-compose-with-upstream.yml build
docker-compose -f docker-compose-with-upstream.yml up -d
```

---

## 🔧 配置说明

### 环境变量

在 `docker-compose-with-upstream.yml` 中配置：

```yaml
services:
  qqmusic-api:
    environment:
      - PORT=3001
      - QQMUSIC_API_BASE=http://qqmusic-upstream:3300  # 上游 API 地址
```

### 端口映射

| 服务 | 容器端口 | 主机端口 | 用途 |
|------|---------|---------|------|
| qqmusic-upstream | 3300 | 3300 | Rain120 API（可选暴露） |
| qqmusic-api | 3001 | 3001 | 代理 API（主要使用） |

### 数据卷

```
./volumes/qq-music-api/  → /app (qqmusic-upstream 容器内)
```

**优势**:

- ✅ 代码持久化
- ✅ 可以在本地编辑
- ✅ 容器重启不丢失

---

## 🧪 测试 API

### 搜索歌曲

```bash
# 通过代理
curl "http://localhost:3001/search?key=顽疾&pageSize=5" | jq '.data.song.list[0]'

# 直接访问上游 (Rain120 端点)
curl "http://localhost:3300/getSearchByKey?key=顽疾&pageSize=5" | jq '.data.song.list[0]'
```

### 获取歌曲详情

```bash
# 通过代理
curl "http://localhost:3001/song?songmid=SONG_MID" | jq '.'

# 直接访问上游
curl "http://localhost:3300/getSongInfo?songmid=SONG_MID" | jq '.'
```

---

## 🔗 集成到 Nginx

更新 `nginx.conf` 使用容器化的 QQ Music API：

```nginx
events { worker_connections 1024; }
http {
    server {
        listen 8888;
        
        # NetEase API
        location /netease/ {
            rewrite ^/netease/(.*) /$1 break;
            proxy_pass http://host.docker.internal:3000;
        }
        
        # QQ Music API - 使用代理层
        location /qqmusic/ {
            rewrite ^/qqmusic/(.*) /$1 break;
            proxy_pass http://host.docker.internal:3001;
        }
    }
}
```

重启 Nginx:

```bash
docker restart nginx-proxy
```

---

## ⚠️ 故障排除

### 问题 1: npm install 失败

**症状**: 容器启动后立即退出

**检查日志**:

```bash
docker-compose -f docker-compose-with-upstream.yml logs qqmusic-upstream
```

**解决**:

```bash
# 删除 node_modules 重新安装
rm -rf volumes/qq-music-api/node_modules
docker-compose -f docker-compose-with-upstream.yml restart qqmusic-upstream
```

### 问题 2: 端口冲突

**症状**: `Error: bind: address already in use`

**检查端口占用**:

```bash
lsof -i :3300
lsof -i :3001
```

**解决**: 修改 `docker-compose-with-upstream.yml` 中的端口映射

### 问题 3: 上游 API 返回错误

**检查健康状态**:

```bash
docker-compose -f docker-compose-with-upstream.yml ps
```

**测试上游 API**:

```bash
curl "http://localhost:3300/getSearchByKey?key=test"
```

### 问题 4: 代理无法连接上游

**检查网络**:

```bash
docker network inspect qqmusic-api_music-metadata-network
```

**测试容器间连接**:

```bash
docker exec qqmusic-api curl http://qqmusic-upstream:3300
```

---

## 📁 目录结构

```
services/qqmusic-api/
├── docker-compose.yml                    # 简化版（仅代理）
├── docker-compose-with-upstream.yml      # 完整版（上游 + 代理）
├── Dockerfile                            # 代理层镜像
├── server.py                             # Mock 实现
├── server-proxy.py                       # 代理实现 ✅
├── setup-upstream.sh                     # 设置脚本
├── .gitignore                            # 忽略 volumes/
├── CONTAINER_SETUP.md                    # 本文档
└── volumes/                              # 容器卷（不提交到 Git）
    └── qq-music-api/                     # Rain120 API 克隆目录
        ├── package.json
        ├── node_modules/
        └── ...
```

---

## 🎯 推荐工作流

### 开发环境

```bash
# 1. 克隆上游 API
./setup-upstream.sh

# 2. 启动容器
docker-compose -f docker-compose-with-upstream.yml up -d

# 3. 查看日志确认启动
docker-compose -f docker-compose-with-upstream.yml logs -f

# 4. 测试
curl "http://localhost:3001/search?key=test"
```

### 生产环境

```bash
# 使用相同配置，但建议:
# 1. 固定 Rain120 API 版本（git checkout 特定 tag）
# 2. 使用环境变量管理配置
# 3. 配置日志收集
# 4. 设置资源限制
```

---

## 🔄 更新 Rain120 API

```bash
cd volumes/qq-music-api
git pull
cd ../..
docker-compose -f docker-compose-with-upstream.yml restart qqmusic-upstream
```

---

## 📚 相关文档

- [QQ Music API Setup Guide](../../QQ_MUSIC_API_SETUP_GUIDE.md)
- [Rain120/qq-music-api GitHub](https://github.com/Rain120/qq-music-api)
- [Nginx Proxy Setup](../../NGINX_PROXY_SETUP.md)

---

**最后更新**: 2025-10-27  
**维护者**: [tooling-agent]

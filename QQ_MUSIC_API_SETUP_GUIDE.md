# QQ Music API 返回 Mock 数据 - 完整解决方案

> **问题**: QQ Music API 返回示例数据而不是真实搜索结果

## 🔍 问题诊断

### 症状

`find_qqmusic_match` 节点返回:

```json
{
  "match_found": true,
  "match_id": "example_mid_001",
  "match_name": "示例歌曲"
}
```

### 根本原因

当前的 QQ Music API 服务（`services/qqmusic-api/server.py`）只是一个 **mock 实现**，返回硬编码的示例数据。

---

## ✅ 解决方案

### 方案 1: 使用 Rain120/qq-music-api（推荐）⭐

这是一个社区维护的真实 QQ 音乐 API 项目。

#### 步骤 1: 克隆并启动 Rain120 API

```bash
# 在项目外部克隆
cd /Users/tr/Workspace
git clone https://github.com/Rain120/qq-music-api.git
cd qq-music-api

# 安装依赖
npm install

# 启动服务（默认端口 3200）
npm start
```

#### 步骤 2: 测试 Rain120 API

```bash
# 测试搜索 (Rain120 端点)
curl "http://localhost:3200/getSearchByKey?key=周杰伦&pageSize=5"

# 应该返回真实的搜索结果
```

#### 步骤 3: 配置代理转发

有两个选择：

**选择 A: 修改 Nginx 配置（推荐）**

直接将 QQ Music 请求转发到 Rain120 API:

```bash
# 编辑 nginx.conf
cat > nginx.conf << 'EOF'
events { worker_connections 1024; }
http {
    server {
        listen 8888;

        # NetEase API
        location /netease/ {
            rewrite ^/netease/(.*) /$1 break;
            proxy_pass http://host.docker.internal:3000;
        }

        # QQ Music API - 转发到代理层（推荐）
        location /qqmusic/ {
            proxy_pass http://host.docker.internal:3001/;
        }

        # 或直接转发到 Rain120 API（不推荐）
        # location /qqmusic/search {
        #     rewrite ^/qqmusic/search /getSearchByKey break;
        #     proxy_pass http://host.docker.internal:3200;
        # }
        # location /qqmusic/song {
        #     rewrite ^/qqmusic/song /getSongInfo break;
        #     proxy_pass http://host.docker.internal:3200;
        # }
    }
}
EOF

# 重启 Nginx
docker restart nginx-proxy
```

**选择 B: 使用 server-proxy.py**

修改 QQ Music API 容器使用代理版本:

```bash
# 1. 修改 Dockerfile 已完成（使用 server-proxy.py）

# 2. 重新构建并启动容器
cd services/qqmusic-api
docker-compose down
docker-compose build
docker-compose up -d
```

#### 步骤 4: 测试集成

```bash
# 通过 Nginx 测试
curl "http://localhost:8888/qqmusic/search?key=周杰伦&pageSize=5"

# 应该返回真实数据，而不是 mock 数据
```

---

### 方案 2: 仅用于测试 - 继续使用 Mock 数据

如果只是测试 Dify 工作流逻辑，可以暂时使用 mock 数据：

1. **修改 `find_qqmusic_match` 节点**，跳过真实匹配
2. **在 `consolidate` 节点中**，标记为"未核验"

---

## 🧪 完整测试流程

### 1. 启动所有服务

```bash
# NetEase API
cd services/netease-api && docker-compose up -d

# Rain120 QQ Music API
cd /Users/tr/Workspace/qq-music-api
npm start &

# Nginx 代理
cd /Users/tr/Workspace/song-metadata-checker
docker restart nginx-proxy

# ngrok（如果使用 Dify Cloud）
ngrok http 8888
```

### 2. 测试 API 链路

```bash
# 测试 NetEase
curl "http://localhost:8888/netease/song/detail?ids=2758218600" | jq '.songs[0].name'

# 测试 QQ Music
curl "http://localhost:8888/qqmusic/search?key=顽疾&pageSize=5" | jq '.data.song.list[0].songname'
```

### 3. 在 Dify Cloud 中测试

使用 ngrok URL 更新环境变量后，重新运行工作流。

---

## 📋 Rain120 API 端点说明

### 搜索歌曲

**端点**: `/search/song`

**参数**:

- `key`: 搜索关键词
- `pageSize`: 每页数量（可选，默认 10）
- `pageNo`: 页码（可选，默认 1）

**响应**:

```json
{
  "code": 0,
  "data": {
    "song": {
      "list": [
        {
          "songmid": "real_song_mid",
          "songname": "真实歌曲名",
          "singer": [{ "name": "真实歌手" }],
          "albumname": "真实专辑"
        }
      ]
    }
  }
}
```

### 获取歌曲详情

**端点**: `/song`

**参数**:

- `songmid`: 歌曲 MID

---

## ⚠️ 常见问题

### 问题 1: Rain120 API 启动失败

**检查**:

```bash
# 检查 Node.js 版本
node --version  # 需要 >= 14

# 检查端口占用
lsof -i :3200  # Rain120 API 默认端口
lsof -i :3001  # 代理层端口
```

### 问题 2: Nginx 转发失败

**检查**:

```bash
# 查看 Nginx 日志
docker logs nginx-proxy

# 测试 Rain120 API 直接访问
curl "http://localhost:3200/getSearchByKey?key=test"

# 测试代理层（如果使用容器化部署）
curl "http://localhost:3001/search?key=test"
```

### 问题 3: 仍然返回 Mock 数据

**原因**: 可能缓存了旧的响应

**解决**:

```bash
# 重启所有服务
docker restart nginx-proxy
docker-compose -f services/qqmusic-api/docker-compose.yml restart

# 清除浏览器缓存
# 在 Dify Cloud 中重新运行工作流
```

---

## 🎯 推荐配置（生产环境）

### 架构

```
Dify Cloud
    ↓ HTTPS
ngrok (https://xxx.ngrok.io)
    ↓
Nginx (localhost:8888)
    ├→ /netease → NetEase API (localhost:3000)
    └→ /qqmusic → QQ Music Proxy (localhost:3001) → Rain120 API
```

### 优势

- ✅ 单一 ngrok 隧道
- ✅ 统一的 API 网关
- ✅ 真实的 QQ 音乐数据
- ✅ 易于维护和监控

---

## 📚 相关文档

- [QQ Music API 服务说明](services/qqmusic-api/README.md)
- [Rain120/qq-music-api GitHub](https://github.com/Rain120/qq-music-api)
- [Nginx 代理设置](NGINX_PROXY_SETUP.md)
- [Dify Cloud 故障排除](docs/guides/DIFY_CLOUD_TROUBLESHOOTING.md)

---

**最后更新**: 2025-10-27  
**状态**: 需要部署 Rain120 API

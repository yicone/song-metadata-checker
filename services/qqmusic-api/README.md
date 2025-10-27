# QQ 音乐 API 服务

## 简介

本服务提供 QQ 音乐的 API 代理接口，用于核验网易云音乐的元数据。

## 核验原理

由于核验需要**多个独立数据源**进行交叉验证：

- **网易云音乐** = 数据源（待核验的数据）
- **QQ 音乐** = 核验源（用于比对验证）
- **Spotify** = 可选的额外核验源

单一数据源无法完成核验，必须有至少一个独立的第三方数据源。

## 架构说明

本项目使用 **双层架构**：

```
用户/应用
    ↓
代理层 (qqmusic-api) - Port 3001
    ↓
上游 API (Rain120) - Port 3200 (容器内) / 3300 (主机)
```

### 为什么需要代理层？

1. **端点标准化**: Rain120 API 使用 `/getSearchByKey`，代理层简化为 `/search`
2. **响应格式统一**: 统一处理不同上游 API 的响应格式
3. **错误处理**: 提供一致的错误响应
4. **未来扩展**: 可以轻松切换或添加其他音乐 API

## 端口映射表

| 服务 | 容器内端口 | 主机端口 | 访问地址 | 推荐使用 |
|------|-----------|---------|---------|----------|
| **qqmusic-api (代理层)** | 3001 | 3001 | `http://localhost:3001` | ✅ **推荐** |
| qqmusic-upstream (Rain120) | 3200 | 3300 | `http://localhost:3300` | ⚠️ 仅调试 |

**重要**: 应用应该连接到代理层 (3001)，而不是直接连接上游 API (3300)。

## 快速启动

### 方式 1: 使用 Docker Compose（推荐）

```bash
cd services/qqmusic-api

# 使用自动化脚本（推荐）
./setup-upstream.sh

# 或手动启动
docker-compose -f docker-compose-with-upstream.yml up -d
```

这会启动两个容器：

- `qqmusic-upstream`: Rain120 API (端口 3300)
- `qqmusic-api`: 代理层 (端口 3001)

### 方式 2: 手动启动上游 API

如果你想自己管理 Rain120 API：

```bash
# 1. 克隆并启动 Rain120 API
git clone https://github.com/Rain120/qq-music-api.git /tmp/qq-music-api
cd /tmp/qq-music-api
npm install
npm start  # 默认端口 3200

# 2. 启动代理层
cd services/qqmusic-api
export QQMUSIC_API_BASE=http://localhost:3200
python server-proxy.py
```

## API 端点对照表

### 代理层端点（推荐使用）

**Base URL**: `http://localhost:3001`

| 端点 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/` | GET | - | 健康检查 |
| `/search` | GET | `key`, `pageSize`, `pageNo` | 搜索歌曲 |
| `/song` | GET | `songmid` | 获取歌曲详情 |

### 上游 API 端点（Rain120）

**Base URL**: `http://localhost:3300` (仅供参考)

| 端点 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/getSearchByKey` | GET | `key`, `pageSize`, `pageNo` | 搜索歌曲 |
| `/getSongInfo` | GET | `songmid` | 获取歌曲详情 |

**注意**: 代理层会自动将请求转发到正确的上游端点。

## 环境变量配置

### 应用配置（项目根目录 .env）

```bash
# ✅ 正确：使用代理层
QQ_MUSIC_API_HOST=http://localhost:3001

# ❌ 错误：直接使用上游 API
# QQ_MUSIC_API_HOST=http://localhost:3300
```

### 代理层配置（services/qqmusic-api/.env）

```bash
# 代理层监听端口
PORT=3001

# 上游 API 地址
# Docker 环境
QQMUSIC_API_BASE=http://qqmusic-upstream:3200

# 本地开发环境
# QQMUSIC_API_BASE=http://localhost:3200
```

## 测试 API

### 测试代理层（推荐）

```bash
# 健康检查
curl "http://localhost:3001/"

# 搜索歌曲
curl "http://localhost:3001/search?key=周杰伦&pageSize=5" | jq '.data.song.list[0]'

# 获取歌曲详情
curl "http://localhost:3001/song?songmid=002w3cVJ4baewp" | jq '.response.songinfo.data.track_info'
```

### 测试上游 API（调试用）

```bash
# 搜索歌曲
curl "http://localhost:3300/getSearchByKey?key=周杰伦&pageSize=5" | jq '.data.song.list[0]'

# 获取歌曲详情
curl "http://localhost:3300/getSongInfo?songmid=002w3cVJ4baewp" | jq '.data.track_info'
```

## 替代方案

如果无法使用 QQ 音乐 API：

1. **使用 Spotify**：配置 Spotify API 作为核验源
2. **使用 Apple Music API**：如果有开发者账号
3. **多个网易云账号**：使用不同地区的网易云 API（不推荐）
4. **人工核验**：导出数据后人工比对

## 法律声明

使用非官方 API 可能违反服务条款。请确保：

- 仅用于个人学习和研究
- 不用于商业用途
- 遵守相关法律法规
- 尊重版权和知识产权

## 停止服务

```bash
docker-compose down
```

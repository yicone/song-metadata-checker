# QQ 音乐 API 服务

## 简介

本服务提供 QQ 音乐的 API 代理接口，用于核验网易云音乐的元数据。

## 核验原理

由于核验需要**多个独立数据源**进行交叉验证：

- **网易云音乐** = 数据源（待核验的数据）
- **QQ 音乐** = 核验源（用于比对验证）
- **Spotify** = 可选的额外核验源

单一数据源无法完成核验，必须有至少一个独立的第三方数据源。

## 实现方案

### 方案 1: 使用现有的 QQ 音乐 API 项目

推荐使用社区项目 [Rain120/qq-music-api](https://github.com/Rain120/qq-music-api)：

```bash
# 克隆项目
git clone https://github.com/Rain120/qq-music-api.git
cd qq-music-api

# 安装依赖
npm install

# 启动服务
npm start
```

服务默认运行在 `http://localhost:3300`，更新 `.env` 中的 `QQ_MUSIC_API_HOST`。

### 方案 2: 使用本项目的简化代理

当前 `server.py` 提供了基础框架，需要集成实际的 API 调用逻辑。

## 快速启动

```bash
cd services/qqmusic-api
docker-compose up -d
```

服务将在 `http://localhost:3001` 启动。

## API 端点

### 健康检查

```bash
GET /
```

### 搜索歌曲

```bash
GET /search?key=歌曲名&pageSize=10&pageNo=1
```

### 获取歌曲详情

```bash
GET /song?songmid=歌曲MID
```

## 推荐配置

### 使用 Rain120/qq-music-api

1. **克隆并启动服务**：

```bash
git clone https://github.com/Rain120/qq-music-api.git ../qqmusic-api-external
cd ../qqmusic-api-external
npm install
npm start
```

2. **更新环境变量**：

```bash
# 在项目根目录的 .env 文件中
QQ_MUSIC_API_HOST=http://localhost:3300
```

3. **测试 API**：

```bash
# 搜索歌曲
curl "http://localhost:3300/search/song?key=周杰伦"

# 获取歌曲详情
curl "http://localhost:3300/song?songmid=xxx"
```

### API 端点映射

| 功能 | Rain120 API | 本项目需要 |
|------|-------------|-----------|
| 搜索 | `/search/song?key=xxx` | `/search?key=xxx` |
| 详情 | `/song?songmid=xxx` | `/song?songmid=xxx` |

如果端点不匹配，可以在 `server.py` 中添加代理转发。

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

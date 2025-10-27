# QQ 音乐 API 配置指南

> **⚠️ 文档已归档 / ARCHIVED**  
> 本文档已过时，仅供历史参考。  
> **请使用最新文档**: [services/qqmusic-api/CONTAINER_SETUP.md](../../services/qqmusic-api/CONTAINER_SETUP.md)
>
> **主要问题**:
>
> - 端点路径已变更 (`/search/song` → `/getSearchByKey`)
> - 端口配置不准确 (3300 vs 3200 vs 3001)
> - 缺少代理层架构说明

---

## 为什么需要 QQ 音乐 API？

核验系统的核心原理是**多源交叉验证**：

```
网易云音乐（数据源）
    ↓
提取元数据
    ↓
与 QQ 音乐数据比对 ← 核验源（必需）
    ↓
生成核验报告
```

**单一数据源无法完成核验**，必须有至少一个独立的第三方数据源进行比对。

## 推荐方案：使用 Rain120/qq-music-api

### 步骤 1: 克隆并安装

```bash
# 在项目外部克隆（避免混淆）
cd ..
git clone https://github.com/Rain120/qq-music-api.git
cd qq-music-api

# 安装依赖
npm install
```

### 步骤 2: 启动服务

```bash
# 启动 QQ 音乐 API 服务
npm start
```

服务将在 `http://localhost:3300` 启动。

### 步骤 3: 测试 API

```bash
# 测试搜索功能
curl "http://localhost:3300/search/song?key=周杰伦"

# 测试歌曲详情
curl "http://localhost:3300/song?songmid=001JD1SR29d8VX"
```

### 步骤 4: 更新项目配置

编辑 `song-metadata-checker/.env` 文件：

```bash
# QQ Music API Configuration
QQ_MUSIC_API_HOST=http://localhost:3300
```

### 步骤 5: 验证集成

```bash
cd song-metadata-checker
poetry run python scripts/validate_apis.py
```

应该看到 QQ 音乐 API 测试通过。

## 方案 2: 使用代理服务器

如果 Rain120 API 的端点格式不匹配，可以使用我们提供的代理服务器：

```bash
cd song-metadata-checker/services/qqmusic-api

# 设置上游 API 地址
export QQMUSIC_API_BASE=http://localhost:3300

# 启动代理服务器
python server-proxy.py
```

代理服务器会将请求转发到 Rain120 API，并统一接口格式。

## API 端点说明

### Rain120/qq-music-api 端点

| 功能     | 端点           | 参数                        |
| -------- | -------------- | --------------------------- |
| 搜索歌曲 | `/search/song` | `key`, `pageSize`, `pageNo` |
| 歌曲详情 | `/song`        | `songmid`                   |
| 歌词     | `/lyric`       | `songmid`                   |

### 本项目需要的端点

| 功能     | 端点      | 参数                        |
| -------- | --------- | --------------------------- |
| 搜索歌曲 | `/search` | `key`, `pageSize`, `pageNo` |
| 歌曲详情 | `/song`   | `songmid`                   |

## 数据格式示例

### 搜索响应

```json
{
  "code": 0,
  "data": {
    "song": {
      "list": [
        {
          "songmid": "001JD1SR29d8VX",
          "songname": "晴天",
          "singer": [{ "name": "周杰伦" }],
          "albumname": "叶惠美",
          "interval": 269
        }
      ]
    }
  }
}
```

### 歌曲详情响应

```json
{
  "code": 0,
  "data": {
    "songmid": "001JD1SR29d8VX",
    "songname": "晴天",
    "singer": [{ "name": "周杰伦" }],
    "albumname": "叶惠美",
    "albummid": "000MkMni19ClKG",
    "interval": 269
  }
}
```

## 故障排除

### 问题 1: Rain120 API 无法启动

**错误**: `npm start` 失败

**解决方案**:

```bash
# 检查 Node.js 版本（需要 14+）
node --version

# 清理并重新安装
rm -rf node_modules package-lock.json
npm install
```

### 问题 2: 搜索返回空结果

**原因**: QQ 音乐 API 可能需要登录或有访问限制

**解决方案**:

1. 检查 Rain120 项目的文档，看是否需要配置 Cookie
2. 尝试使用不同的搜索关键词
3. 查看 Rain120 项目的 Issues

### 问题 3: 端点格式不匹配

**错误**: Dify 工作流调用失败

**解决方案**: 使用代理服务器 `server-proxy.py` 统一接口格式

## 替代方案

如果无法使用 QQ 音乐 API，可以考虑：

### 方案 A: 使用 Spotify API

配置 Spotify 作为核验源（需要申请开发者账号）：

```bash
# 在 .env 中配置
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

然后使用完整版工作流 `music-metadata-checker.yml`。

### 方案 B: 使用其他音乐平台

- Apple Music API（需要开发者账号）
- YouTube Music（非官方 API）
- Last.fm API（音乐数据库）

### 方案 C: 仅数据提取（不核验）

如果只需要从网易云提取数据，不需要核验：

1. 修改工作流，移除 QQ 音乐节点
2. 直接输出网易云的结构化数据
3. 后续可以人工核验

## 生产环境建议

### 1. 使用 Docker 部署

创建 `docker-compose.yml` 统一管理所有服务：

```yaml
version: "3.8"
services:
  netease-api:
    # ...
  qqmusic-api:
    # ...
  metadata-checker:
    # ...
```

### 2. 添加缓存层

使用 Redis 缓存 QQ 音乐 API 响应，减少请求次数：

```python
import redis
cache = redis.Redis(host='localhost', port=6379)
```

### 3. 实现降级策略

当 QQ 音乐 API 不可用时：

- 自动切换到 Spotify
- 或标记为"待人工核验"
- 记录日志供后续处理

### 4. 监控和告警

监控 QQ 音乐 API 的可用性：

```bash
# 定期健康检查
*/5 * * * * curl -f http://localhost:3300 || echo "QQ Music API down"
```

## 法律和合规性

⚠️ **重要提示**:

1. QQ 音乐没有官方 API，使用非官方 API 可能违反服务条款
2. 仅用于个人学习和研究目的
3. 不要用于商业用途或大规模爬取
4. 尊重版权和知识产权
5. 遵守相关法律法规

## 下一步

配置完成后：

1. 运行 `poetry run python scripts/validate_apis.py` 验证所有 API
2. 在 Dify 中导入工作流 `music-metadata-checker-simple.yml`
3. 测试完整的核验流程
4. 根据需要调整匹配算法和核验规则

## 获取帮助

- Rain120/qq-music-api 项目: <https://github.com/Rain120/qq-music-api>
- 本项目 Issues: 提交问题和建议
- 查看 `services/qqmusic-api/README.md` 了解更多细节

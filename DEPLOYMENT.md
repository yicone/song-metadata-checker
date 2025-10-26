# 部署指南

本文档详细说明如何部署音乐元数据核验系统。

## 前置要求

### 系统要求

- Docker 和 Docker Compose
- Python 3.8+
- 稳定的网络连接

### API 密钥

在开始部署前，请准备以下 API 密钥：

1. **Google Gemini API Key**
   - 访问 [Google AI Studio](https://aistudio.google.com/)
   - 创建 API 密钥

2. **Spotify API 凭证**
   - 访问 [Spotify for Developers](https://developer.spotify.com/dashboard)
   - 创建应用获取 Client ID 和 Client Secret

3. **Dify 平台**
   - 自托管：参考 [Dify 部署文档](https://docs.dify.ai/)
   - 云服务：注册 [Dify Cloud](https://dify.ai/)

## 部署步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd song-metadata-checker
```

### 2. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥：

```env
# Google Gemini API
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_AUTH_URL=https://accounts.spotify.com/api/token
SPOTIFY_API_BASE_URL=https://api.spotify.com/v1

# NeteaseCloudMusicApi
NETEASE_API_HOST=http://localhost:3000
```

### 3. 部署 NeteaseCloudMusicApi 服务

```bash
cd services/netease-api
docker-compose up -d
```

验证服务运行：

```bash
curl http://localhost:3000
```

### 4. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 5. 测试 API 连通性

```bash
python scripts/validate_apis.py
```

确保所有 API 测试通过。

### 6. 部署 Dify 平台

#### 选项 A: 自托管 Dify

```bash
# 克隆 Dify 仓库
git clone https://github.com/langgenius/dify.git
cd dify/docker

# 启动服务
docker-compose up -d

# 访问 http://localhost/install 完成初始化
```

#### 选项 B: 使用 Dify Cloud

直接访问 [Dify Cloud](https://cloud.dify.ai/) 注册账号。

### 7. 导入工作流

1. 登录 Dify 平台
2. 点击「创建应用」→「工作流」
3. 选择「导入 DSL」
4. 上传 `dify-workflow/music-metadata-checker.yml`
5. 配置环境变量（在工作流设置中）

### 8. 配置工作流环境变量

在 Dify 工作流设置中，添加以下环境变量：

- `GEMINI_API_KEY`
- `GEMINI_API_BASE_URL`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_AUTH_URL`
- `SPOTIFY_API_BASE_URL`
- `NETEASE_API_HOST`

### 9. 测试工作流

在 Dify 界面中测试工作流：

**输入：**
- `song_url`: `https://music.163.com#/song?id=2758218600`
- `credits_image_url`: （可选）制作人员图片 URL

点击「运行」查看结果。

### 10. 发布为 API（可选）

如果需要通过 API 调用工作流：

1. 在 Dify 工作流界面点击「发布」
2. 选择「API」
3. 获取 API 密钥和端点
4. 更新 `.env` 文件中的 `DIFY_API_KEY` 和 `DIFY_API_BASE_URL`

## 验证部署

### 运行完整测试

```bash
python scripts/test_workflow.py --url "https://music.163.com#/song?id=2758218600"
```

### 预期输出

测试成功后，你应该看到：

```
✅ 工作流执行成功！

核验报告
============================================================
{
  "metadata": {
    "song_id": "2758218600",
    "source": "NetEase Cloud Music"
  },
  "fields": {
    "title": {
      "value": "歌曲名称",
      "status": "确认",
      "confirmed_by": ["Spotify"]
    },
    ...
  },
  "summary": {
    "total_fields": 10,
    "confirmed": 7,
    "questionable": 2,
    "not_found": 1,
    "confidence_score": 0.7
  }
}
```

## 故障排除

### NeteaseCloudMusicApi 无法访问

**问题：** `curl http://localhost:3000` 失败

**解决方案：**
```bash
# 检查容器状态
docker ps | grep netease

# 查看日志
docker logs netease-music-api

# 重启服务
cd services/netease-api
docker-compose restart
```

### Spotify API 认证失败

**问题：** `❌ Spotify OAuth 认证失败: 401`

**解决方案：**
1. 确认 Client ID 和 Client Secret 正确
2. 检查 Spotify 应用状态（是否被暂停）
3. 验证 Base64 编码是否正确

### Gemini API 超时

**问题：** `❌ Gemini API 测试失败: timeout`

**解决方案：**
1. 检查网络连接
2. 确认 API 密钥有效
3. 增加超时时间（在 HTTP 节点配置中）

### Dify 工作流导入失败

**问题：** 工作流 YAML 导入错误

**解决方案：**
1. 确认 Dify 版本兼容性（推荐 0.8.0+）
2. 检查 YAML 格式是否正确
3. 尝试手动创建节点并配置

## 性能优化

### 启用缓存

使用 Redis 缓存已处理的歌曲数据：

```bash
# 启动 Redis
docker run -d -p 6379:6379 redis:alpine

# 更新 .env
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 并行处理

在 `consolidate.py` 中使用 `asyncio` 并行调用多个 API：

```python
import asyncio
import aiohttp

async def fetch_all_sources():
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_spotify(session),
            fetch_qqmusic(session)
        ]
        return await asyncio.gather(*tasks)
```

### 速率限制

实现请求队列避免触发 API 限流：

```python
from time import sleep

def rate_limited_request(url, max_per_minute=60):
    sleep(60 / max_per_minute)
    return requests.get(url)
```

## 监控与日志

### 配置日志

在 `.env` 中设置：

```env
LOG_LEVEL=INFO
LOG_FILE=logs/workflow.log
```

### 监控 API 状态

使用 cron 定期运行健康检查：

```bash
# 添加到 crontab
*/5 * * * * /path/to/python /path/to/scripts/validate_apis.py >> /var/log/api-health.log 2>&1
```

### 告警配置

当 API 失效时发送通知（示例使用钉钉机器人）：

```python
import requests

def send_alert(message):
    webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
    data = {
        "msgtype": "text",
        "text": {"content": f"⚠️ API 告警: {message}"}
    }
    requests.post(webhook_url, json=data)
```

## 安全建议

1. **不要提交 `.env` 文件到版本控制**
2. **使用环境变量或密钥管理服务存储敏感信息**
3. **定期轮换 API 密钥**
4. **限制 API 访问 IP 白名单**
5. **启用 HTTPS 加密通信**

## 更新与维护

### 更新 NeteaseCloudMusicApi

```bash
cd services/netease-api
docker-compose pull
docker-compose up -d
```

### 更新工作流

1. 修改 `dify-workflow/music-metadata-checker.yml`
2. 在 Dify 界面重新导入
3. 测试更新后的工作流

### 备份配置

定期备份重要配置：

```bash
# 备份环境变量
cp .env .env.backup.$(date +%Y%m%d)

# 导出 Dify 工作流
# 在 Dify 界面导出 DSL 文件
```

## 生产环境建议

1. **使用负载均衡器**分发请求
2. **部署多个 NeteaseCloudMusicApi 实例**提高可用性
3. **实现断路器模式**处理 API 故障
4. **设置监控告警**及时发现问题
5. **定期审查日志**分析性能瓶颈

## 支持与反馈

如遇到问题，请：

1. 查看 [FAQ](README.md#常见问题)
2. 搜索 [Issues](https://github.com/your-repo/issues)
3. 提交新的 Issue 并附上详细日志

## 下一步

- 阅读 [API 文档](docs/API.md)
- 了解[工作流架构](docs/音乐网站歌曲信息核验流程.md)
- 贡献代码改进项目

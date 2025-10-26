# Quick Start Guide / 快速开始指南

Get the Music Metadata Verification System running in 5 minutes.

> **Note**: This guide focuses on getting started quickly. For complete deployment instructions, see [Deployment Guide](guides/DEPLOYMENT.md).

## 📌 Choose Your Setup / 选择配置方式

This guide provides two setup options:

- **[Standard Setup](#standard-setup-with-spotify)** - Uses Spotify (official API, international coverage)
- **[简化配置](#simplified-setup-with-qq-music-简化配置)** - 使用 QQ 音乐（社区 API，中国市场覆盖好）

---

## Standard Setup (with Spotify)

### 📋 Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ (with Poetry recommended)
- API keys ready (see below)

### 🔑 Step 1: Obtain API Keys

**Required**:

- **Google Gemini API**: Visit [Google AI Studio](https://aistudio.google.com/)
- **QQ Music API**: See [QQ Music Setup Guide](guides/QQMUSIC_API_SETUP.md)

**Optional**:

- **Spotify API**: Visit [Spotify for Developers](https://developer.spotify.com/dashboard)

### ⚙️ Step 2: Configure Environment

```bash
# Navigate to project directory
cd song-metadata-checker

# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

Required configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
NETEASE_API_HOST=http://localhost:3000
QQ_MUSIC_API_HOST=http://localhost:3300
```

### 🚀 Step 3: Start Services

```bash
# Start NetEase Cloud Music API
cd services/netease-api
docker-compose up -d
cd ../..

# Start QQ Music API (see setup guide for details)
cd services/qqmusic-api
docker-compose up -d
cd ../..

# Install Python dependencies
poetry install
# or: pip install -r requirements.txt
```

### ✅ Step 4: Validate APIs

```bash
# Run validation script
poetry run python scripts/validate_apis.py
```

Expected output:

```
✅ NetEase Cloud Music API: Connected
✅ QQ Music API: Connected
✅ Gemini API: Connected
⏭️ Spotify API: Skipped (optional)
🎉 All required APIs operational!
```

### 📥 Step 5: Import Dify Workflow

#### Option A: Dify Cloud

1. Visit [Dify Cloud](https://cloud.dify.ai/)
2. Create new Workflow application
3. Import `dify-workflow/music-metadata-checker.yml`
4. Configure environment variables in workflow settings

#### Option B: Self-Hosted Dify

```bash
# Clone Dify repository
git clone https://github.com/langgenius/dify.git
cd dify/docker

# Start services
docker-compose up -d

# Visit http://localhost/install to complete setup
```

### 🧪 Step 6: Test Workflow

#### In Dify Interface

**Input**:

- `song_url`: `https://music.163.com#/song?id=2758218600`
- `credits_image_url`: (optional)

Click "Run" to execute.

### Command Line

```bash
poetry run python scripts/test_workflow.py \
  --url "https://music.163.com#/song?id=2758218600"
```

### 🎉 Success

You can now:

- Run workflows in Dify interface
- Call workflows via API
- Customize workflow nodes
- Integrate into your applications

## 📚 Next Steps

- **[Functional Specification](FUNCTIONAL_SPEC.md)** - Learn about all features
- **[Deployment Guide](guides/DEPLOYMENT.md)** - Production deployment
- **[Workflow Overview](guides/WORKFLOW_OVERVIEW.md)** - Technical architecture

## ❓ Troubleshooting

### NetEase API Not Accessible

```bash
# Check container status
docker ps | grep netease

# View logs
docker logs netease-music-api
```

### QQ Music API Issues

See [QQ Music Setup Guide](guides/QQMUSIC_API_SETUP.md) for detailed troubleshooting.

### Gemini API Timeout

- Verify API key is correct
- Check network connectivity to Google services
- Ensure API quota is not exceeded

### Spotify Authentication Failed (Optional)

- Verify Client ID and Secret
- Check application status in Spotify Dashboard
- Ensure credentials are correctly encoded

## 🆘 Get Help

- Check [Deployment Guide](guides/DEPLOYMENT.md#troubleshooting) for detailed troubleshooting
- Review [Fixes Index](FIXES_INDEX.md) for known issues
- Submit an issue on GitHub

---

## Simplified Setup (with QQ Music) / 简化配置

使用网易云音乐 + QQ 音乐 + Gemini API 的简化实现。

### 📊 配置对比

| 特性 | Standard Setup | Simplified Setup |
|------|----------------|------------------|
| **核验源** | Spotify (官方 API) | QQ Music (社区 API) |
| **配置复杂度** | 中等 (需 OAuth) | 简单 (无需 OAuth) |
| **市场覆盖** | 国际 | 中国 |
| **API 稳定性** | 高 (官方) | 中 (社区维护) |
| **环境变量** | 6 个 | 4 个 |

### 🎯 为什么选择简化配置？

核验的本质是**多源交叉验证**：

- **网易云音乐** = 待核验的数据源
- **QQ 音乐** = 独立的核验源（用于比对）
- 单一数据源无法完成核验

**适用场景**：

- ✅ 主要面向中国市场音乐
- ✅ 希望快速部署（配置简单）
- ✅ 无法或不想配置 Spotify OAuth
- ✅ 需要更快的执行速度

### 📋 前置要求

- Docker 和 Docker Compose
- Python 3.8+ (推荐使用 Poetry)
- 已准备好 API 密钥

### 🔑 步骤 1: 获取 API 密钥

**必需**：

- **Google Gemini API**: 访问 [Google AI Studio](https://aistudio.google.com/)
- **QQ 音乐 API**: 参考 [QQ 音乐配置指南](guides/QQMUSIC_API_SETUP.md)

**可选**：

- Spotify API（如需额外核验源）

### ⚙️ 步骤 2: 配置环境

```bash
# 进入项目目录
cd song-metadata-checker

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env
```

必需配置：

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
NETEASE_API_HOST=http://localhost:3000
QQ_MUSIC_API_HOST=http://localhost:3300
```

### 🚀 步骤 3: 启动服务

```bash
# 启动网易云音乐 API
cd services/netease-api
docker-compose up -d
cd ../..

# 启动 QQ 音乐 API
cd services/qqmusic-api
docker-compose up -d
cd ../..

# 安装 Python 依赖
poetry install
# 或: pip install -r requirements.txt
```

### ✅ 步骤 4: 验证 API

```bash
# 运行验证脚本
poetry run python scripts/validate_apis.py
```

预期输出：

```
✅ NetEase Cloud Music API: Connected
✅ QQ Music API: Connected
✅ Gemini API: Connected
⏭️ Spotify API: Skipped (optional)
🎉 All required APIs operational!
```

### 📥 步骤 5: 导入 Dify 工作流

#### 选项 A: Dify Cloud

1. 访问 [Dify Cloud](https://cloud.dify.ai/)
2. 创建新的 Workflow 应用
3. 导入 `dify-workflow/music-metadata-checker-simple.yml`
4. 在工作流设置中配置环境变量

#### 选项 B: 自托管 Dify

```bash
# 克隆 Dify 仓库
git clone https://github.com/langgenius/dify.git
cd dify/docker

# 启动服务
docker-compose up -d

# 访问 http://localhost/install 完成初始化
```

### 🧪 步骤 6: 测试工作流

#### 在 Dify 界面测试

**输入**：

- `song_url`: `https://music.163.com#/song?id=2758218600`
- `credits_image_url`: (可选)

点击 "Run" 执行。

#### 命令行测试

```bash
# 基础测试
poetry run python scripts/test_workflow.py \
  --url "https://music.163.com#/song?id=2758218600"

# 包含 OCR 提取
poetry run python scripts/test_workflow.py \
  --url "https://music.163.com#/song?id=2758218600" \
  --credits-image "https://example.com/credits.jpg"
```

### 📊 工作流程图

```
用户输入 URL
    ↓
解析歌曲 ID
    ↓
获取网易云数据（歌曲详情 + 歌词）
    ↓
数据结构化
    ↓
[可选] Gemini OCR 提取制作人员
    ↓
QQ 音乐搜索与核验
    ↓
生成核验报告
```

### 🎉 成功

现在你可以：

- 在 Dify 界面运行工作流
- 通过 API 调用工作流
- 自定义工作流节点
- 集成到你的应用中

### 📚 下一步

- **[功能规格](FUNCTIONAL_SPEC.md)** - 了解所有功能
- **[部署指南](guides/DEPLOYMENT.md)** - 生产环境部署
- **[工作流详解](guides/WORKFLOW_OVERVIEW.md)** - 技术架构

### ❓ 故障排除

#### 网易云 API 无法访问

```bash
docker ps | grep netease
docker logs netease-music-api
```

#### QQ 音乐 API 问题

参考 [QQ 音乐配置指南](guides/QQMUSIC_API_SETUP.md) 获取详细故障排除步骤。

#### Gemini API 超时

- 检查 API 密钥是否正确
- 确认网络可以访问 Google 服务
- 确保 API 配额未超限

#### 不需要 QQ 音乐核验？

如果只需要数据提取而不需要核验：

- 在 Dify 工作流中禁用 QQ 音乐相关节点
- 或直接使用网易云数据作为最终结果

### 🆘 获取帮助

- 查看 [部署指南](guides/DEPLOYMENT.md#troubleshooting) 获取详细故障排除
- 查看 [修复索引](FIXES_INDEX.md) 了解已知问题
- 在 GitHub 提交 issue

---

**Last Updated**: 2025-10-26  
**Maintained By**: [documentation-agent]

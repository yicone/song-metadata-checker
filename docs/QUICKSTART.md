# Quick Start Guide / 快速开始指南

Get the Music Metadata Verification System running in 5 minutes with minimal configuration.

> **📖 For Complete Instructions**: This is a **quick path** guide with essential commands only.  
> For detailed explanations, troubleshooting, and production setup, see the authoritative [Deployment Guide](guides/DEPLOYMENT.md).
>
> **📌 Validation Sources**:
>
> - **QQ Music**: Active (required)
> - **Spotify**: Optional, currently disabled (can be enabled later)
> - See [Enabling Spotify](guides/WORKFLOW_OVERVIEW.md#enabling-spotify-validation) for details

---

## Quick Setup / 快速设置

### Prerequisites / 前置条件

**System**: Docker, Python 3.8+, API keys

[📖 See complete prerequisites →](guides/DEPLOYMENT.md#prerequisites)

### Setup Steps / 设置步骤 (3 Steps)

#### 1️⃣ Get API Keys / 获取 API 密钥

**Required / 必需**:

- **Gemini**: [Get key →](https://aistudio.google.com/) / [获取密钥 →](https://aistudio.google.com/)
- **QQ Music / QQ 音乐**: [Setup guide →](guides/QQMUSIC_API_SETUP.md) / [配置指南 →](guides/QQMUSIC_API_SETUP.md)

**Optional / 可选** (currently disabled / 当前禁用):

- **Spotify**: [Get credentials →](https://developer.spotify.com/dashboard) (see [how to enable](guides/WORKFLOW_OVERVIEW.md#enabling-spotify-validation))

[📖 See detailed API setup →](guides/DEPLOYMENT.md#api-keys-required)

#### 2️⃣ Configure & Start / 配置与启动 (3 commands)

```bash
cp .env.example .env
# Edit .env with your API keys / 编辑 .env 填入 API 密钥
docker-compose up -d
```

[📖 See complete environment configuration →](guides/DEPLOYMENT.md#step-2-configure-environment)

#### 3️⃣ Import & Test / 导入与测试

**Import workflow / 导入工作流**:

- **Dify Cloud**: Use [manual setup guide](guides/../../dify-workflow/BUILD_GUIDE.md) (YAML import not supported)
- **Self-hosted Dify**: Import `dify-workflow/music-metadata-checker.yml`

**Test / 测试**:

```bash
poetry run python scripts/test_workflow.py \
  --url "https://music.163.com#/song?id=2758218600"
```

[📖 See complete testing guide →](guides/DEPLOYMENT.md#verification)

### ✅ Success / 成功

You're ready to verify music metadata / 你已准备好核验音乐元数据

**Next steps / 下一步**:

- [📖 Complete Deployment Guide](guides/DEPLOYMENT.md) - Detailed setup / 详细设置
- [🔧 Troubleshooting](guides/DEPLOYMENT.md#troubleshooting) - Common issues / 常见问题
- [🚀 Production Setup](guides/DEPLOYMENT.md#production-considerations) - Best practices / 最佳实践
- [🎵 Enable Spotify](guides/WORKFLOW_OVERVIEW.md#enabling-spotify-validation) - Optional validation source / 可选核验源

---

**Last Updated**: 2025-10-27  
**Maintained By**: [documentation-agent]

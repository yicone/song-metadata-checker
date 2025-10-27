# Quick Start Guide / 快速开始指南

Get the Music Metadata Verification System running in 5 minutes with minimal configuration.

> **📖 For Complete Instructions**: This is a **quick path** guide with essential commands only.  
> For detailed explanations, troubleshooting, and production setup, see the authoritative [Deployment Guide](guides/DEPLOYMENT.md).

## 📌 Choose Your Setup / 选择配置方式

| Setup Type                                 | Best For            | API Required        | Time   |
| ------------------------------------------ | ------------------- | ------------------- | ------ |
| **[Standard](#standard-setup-spotify)**    | International users | Spotify (official)  | ~5 min |
| **[简化配置](#simplified-setup-qq-music)** | 中国市场用户        | QQ Music (社区 API) | ~5 min |

---

## Standard Setup (Spotify)

### Prerequisites

**System**: Docker, Python 3.8+, API keys

[📖 See complete prerequisites →](guides/DEPLOYMENT.md#prerequisites)

### Quick Setup (3 Steps)

#### 1️⃣ Get API Keys

- **Gemini**: [Get key →](https://aistudio.google.com/)
- **Spotify**: [Get credentials →](https://developer.spotify.com/dashboard)

[📖 See detailed API setup →](guides/DEPLOYMENT.md#api-keys-required)

#### 2️⃣ Configure & Start (3 commands)

```bash
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

[📖 See complete environment configuration →](guides/DEPLOYMENT.md#step-2-configure-environment)

#### 3️⃣ Import & Test

**Import workflow**: `dify-workflow/music-metadata-checker.yml` into [Dify](https://cloud.dify.ai/)

**Test**:

```bash
poetry run python scripts/test_workflow.py \
  --url "https://music.163.com#/song?id=2758218600"
```

[📖 See complete testing guide →](guides/DEPLOYMENT.md#verification)

### ✅ Success

You're ready to verify music metadata. Next:

- [📖 Complete Deployment Guide](guides/DEPLOYMENT.md) - Detailed setup
- [🔧 Troubleshooting](guides/DEPLOYMENT.md#troubleshooting) - Common issues
- [🚀 Production Setup](guides/DEPLOYMENT.md#production-considerations) - Best practices

---

## Simplified Setup (QQ Music)

### 简化配置 / 中国市场

**适用场景**: 中国市场音乐、快速部署、无需 OAuth

[📖 查看配置对比 →](guides/DEPLOYMENT.md#deployment-steps)

### 快速设置（3 步）

#### 1️⃣ 获取 API 密钥

- **Gemini**: [获取密钥 →](https://aistudio.google.com/)
- **QQ 音乐**: [配置指南 →](guides/QQMUSIC_API_SETUP.md)

[📖 查看详细 API 设置 →](guides/DEPLOYMENT.md#api-keys-required)

#### 2️⃣ 配置与启动（3 条命令）

```bash
cp .env.example .env
# 编辑 .env 填入 API 密钥
docker-compose up -d
```

[📖 查看完整环境配置 →](guides/DEPLOYMENT.md#step-2-configure-environment)

#### 3️⃣ 导入与测试

**导入工作流**: `dify-workflow/music-metadata-checker-simple.yml` 到 [Dify](https://cloud.dify.ai/)

**测试**:

```bash
poetry run python scripts/test_workflow.py \
  --url "https://music.163.com#/song?id=2758218600"
```

[📖 查看完整测试指南 →](guides/DEPLOYMENT.md#verification)

### ✅ 成功

你已准备好核验音乐元数据。下一步：

- [📖 完整部署指南](guides/DEPLOYMENT.md) - 详细设置
- [🔧 故障排除](guides/DEPLOYMENT.md#troubleshooting) - 常见问题
- [🚀 生产环境配置](guides/DEPLOYMENT.md#production-considerations) - 最佳实践

---

**Last Updated**: 2025-10-26  
**Maintained By**: [documentation-agent]

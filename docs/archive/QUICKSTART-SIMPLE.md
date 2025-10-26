# 快速开始指南（简化版）

> **Note**: 这是简化版的中文快速开始指南。完整的英文版本请参考 [QUICKSTART.md](QUICKSTART.md)。

使用网易云音乐 + Gemini API 的最小化实现。

## 当前状态

✅ **网易云音乐 API**: 已测试通过（数据源）  
✅ **Gemini API**: 已测试通过（OCR 提取）  
🔧 **QQ 音乐 API**: 必需（核验源 - 需要配置）  
⏭️ **Spotify API**: 可选（额外核验源）

## 为什么需要 QQ 音乐 API？

核验的本质是**多源交叉验证**：

- 网易云音乐 = 待核验的数据源
- QQ 音乐 = 独立的核验源（用于比对）
- 单一数据源无法完成核验

如果不需要核验，只需要数据提取，可以跳过 QQ 音乐配置。

## 快速启动（3 步）

### 步骤 1: 确认服务运行

```bash
# 检查网易云音乐 API
curl http://localhost:3000

# 应该返回 API 信息
```

### 步骤 2: 测试基础功能

```bash
# 使用 Poetry 运行测试
poetry run python scripts/test_workflow.py --url "https://music.163.com#/song?id=2758218600"
```

### 步骤 3: 导入简化工作流

在 Dify 中导入：

```
dify-workflow/music-metadata-checker-simple.yml
```

配置环境变量：

- `GEMINI_API_KEY` ✅ 已配置
- `GEMINI_API_BASE_URL` = `https://generativelanguage.googleapis.com/v1beta`
- `NETEASE_API_HOST` = `http://localhost:3000`
- `QQ_MUSIC_API_HOST` = `http://localhost:3001` (可选)

## 当前工作流程

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
[可选] QQ 音乐搜索与核验
    ↓
生成核验报告
```

## 测试示例

### 仅使用网易云数据

```bash
poetry run python scripts/test_workflow.py \
  --url "https://music.163.com#/song?id=2758218600"
```

### 包含 OCR 提取

```bash
poetry run python scripts/test_workflow.py \
  --url "https://music.163.com#/song?id=2758218600" \
  --credits-image "https://example.com/credits.jpg"
```

## QQ 音乐 API（可选）

### 启动 QQ 音乐模拟服务

```bash
cd services/qqmusic-api
docker-compose up -d
```

⚠️ **注意**: 当前为模拟服务，返回示例数据。

### 集成真实 QQ 音乐 API

参考 `services/qqmusic-api/README.md` 了解如何集成真实 API。

## 最小化工作流

如果你只需要网易云音乐数据提取（不需要核验），可以：

1. 只运行阶段一和阶段二的节点
2. 跳过 QQ 音乐搜索
3. 直接输出网易云数据

## 下一步

- ✅ 测试网易云数据提取
- ✅ 测试 Gemini OCR 功能
- 🔄 决定是否需要 QQ 音乐核验
- 📝 根据实际需求调整工作流

## 故障排除

**Q: 网易云 API 无法访问？**

```bash
docker ps | grep netease
docker logs netease-music-api
```

**Q: Gemini API 调用失败？**

- 检查 API 密钥是否正确
- 确认网络可以访问 Google 服务

**Q: 不需要 QQ 音乐核验？**

- 在 Dify 工作流中禁用相关节点
- 或直接使用网易云数据作为最终结果

## 推荐配置

### 最小配置（仅网易云）

- 网易云音乐 API ✅
- Gemini API（用于 OCR）✅

### 完整配置（包含核验）

- 网易云音乐 API ✅
- Gemini API ✅
- QQ 音乐 API 🚧

## 获取帮助

查看完整文档：

- [README.md](../README.md) - 项目概述
- [部署指南](guides/DEPLOYMENT.md) - 详细部署
- [功能规格](FUNCTIONAL_SPEC.md) - 功能说明
- [工作流详解](guides/WORKFLOW_OVERVIEW.md) - 架构设计

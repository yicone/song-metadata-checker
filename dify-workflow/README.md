# Dify 工作流配置

本目录包含音乐元数据核验工作流的 Dify 配置文件。

## 📁 工作流文件

**文件**: `music-metadata-checker.yml`

**核验源状态**:

- ✅ **QQ Music**: 当前启用（必需）
- ⏭️ **Spotify**: 可选，当前禁用（调试优先级低）

**必需 API**: NetEase Cloud Music, Google Gemini, QQ Music  
**可选 API**: Spotify (参考 [启用指南](../docs/guides/WORKFLOW_OVERVIEW.md#enabling-spotify-validation))

## 🚀 快速导入

### 方式 1: 使用打包文件（推荐）

```bash
# 1. 构建自包含的 YML 文件
poetry run python scripts/build_dify_bundle.py

# 2. 在 Dify Cloud 导入
#    上传: music-metadata-checker-bundle.yml

# 3. 配置环境变量
```

### 方式 2: 手动配置

参考 [DIFY_CLOUD_MANUAL_SETUP.md](../docs/guides/DIFY_CLOUD_MANUAL_SETUP.md) 逐步创建节点。

---

**⚠️ 重要**: Dify Cloud 导入需要**自包含的 YML 文件**（所有代码内嵌）。本目录采用模块化结构便于开发，使用构建脚本生成可导入的打包文件。

📖 [打包构建指南 →](BUILD_GUIDE.md)

## 🔧 节点配置

### 代码节点 (`nodes/code-nodes/`)

- `parse_url.py` - URL 解析，提取歌曲 ID
- `normalize_data.py` - 数据规范化
- `find_match.py` - 搜索结果匹配算法
- `consolidate.py` - 数据整合和状态判定

### HTTP 节点 (`nodes/http-nodes/`)

- `netease_*.json` - 网易云音乐 API 调用
- `qqmusic_*.json` - QQ 音乐 API 调用
- `spotify_*.json` - Spotify API 调用
- `gemini_*.json` - Google Gemini API 调用

## 📚 相关文档

- **[Dify 工作流设置](../docs/guides/DIFY_WORKFLOW_SETUP.md)** - 完整导入和配置指南 ⭐
- **[部署指南](../docs/guides/DEPLOYMENT.md)** - 系统部署说明
- **[工作流详解](../docs/guides/WORKFLOW_OVERVIEW.md)** - 技术架构和实现
- **[QQ 音乐配置](../docs/guides/QQMUSIC_API_SETUP.md)** - QQ 音乐 API 设置

---

**最后更新**: 2025-10-27  
**维护者**: [documentation-agent]

# Dify 工作流配置

本目录包含音乐元数据核验工作流的 Dify 配置文件。

## 📁 工作流文件

| 文件 | 版本 | 适用场景 | 必需 API |
|------|------|----------|----------|
| `music-metadata-checker.yml` | 标准版 | 国际用户 | Spotify (官方) |
| `music-metadata-checker-simple.yml` | 简化版 | 中国市场 | QQ 音乐 (社区) |

## 🚀 快速导入

```bash
# 1. 验证 API 服务
poetry run python scripts/validate_apis.py

# 2. 在 Dify 平台导入 .yml 文件
# 3. 配置环境变量
```

[📖 完整设置指南 →](../docs/guides/DIFY_WORKFLOW_SETUP.md)

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

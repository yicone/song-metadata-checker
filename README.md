# 音乐元数据自动核验系统

基于 Dify 平台构建的自动化音乐歌曲上架与核验工作流系统。

## 🎯 项目概述

本系统通过 Dify 工作流自动化处理音乐元数据的提取、验证和核对。系统接收网易云音乐歌曲 URL，自动提取元数据，并通过多个第三方平台（QQ 音乐、Spotify）进行交叉验证，最终生成包含核验状态的标准化数据报告。

## ✨ 核心功能

- **自动数据提取** - 从网易云音乐提取歌曲基础信息
- **OCR 制作人员提取** - 使用 Google Gemini 2.5 Flash 从图片中提取制作人员名单
- **多源交叉验证** - 通过 QQ 音乐和 Spotify 进行数据核验
- **封面图比对** - 使用 AI 视觉能力比对不同来源的专辑封面
- **智能状态判定** - 自动标记数据为「确认」、「存疑」或「未查到」

[查看完整功能列表 →](docs/FUNCTIONAL_SPEC.md)

## 🏗️ 技术架构

**核心组件**:

- Dify 平台 (工作流引擎)
- NeteaseCloudMusicApi (数据源)
- QQ Music API (核验源)
- Spotify Web API (可选核验源)
- Google Gemini 2.5 Flash (AI 增强)

[查看详细架构 →](docs/guides/WORKFLOW_OVERVIEW.md)

## 🚀 快速开始

**3 步快速部署**:

1. 启动 API 服务
2. 配置环境变量
3. 导入 Dify 工作流

[📖 5分钟快速开始 →](docs/QUICKSTART.md) | [📖 完整部署指南 →](docs/guides/DEPLOYMENT.md)

## 📁 项目结构

```
song-metadata-checker/
├── README.md                    # 本文档 (项目导航)
├── CHANGELOG.md                 # 版本历史
├── AGENTS.md                    # AI 协作指南
├── docs/                        # 文档目录
│   ├── README.md                # 文档索引
│   ├── QUICKSTART.md            # 快速开始
│   ├── FUNCTIONAL_SPEC.md       # 功能规格
│   ├── ROADMAP.md               # 路线图和限制
│   ├── FIXES_INDEX.md           # Bug 修复索引
│   └── guides/                  # 详细指南
│       ├── DEPLOYMENT.md        # 部署指南
│       ├── QQMUSIC_API_SETUP.md # QQ音乐配置
│       └── WORKFLOW_OVERVIEW.md # 工作流详解
├── dify-workflow/               # Dify 工作流配置
│   └── music-metadata-checker.yml
├── services/                    # 外部服务
│   ├── netease-api/            # 网易云 API
│   └── qqmusic-api/            # QQ 音乐 API
└── scripts/                     # 辅助脚本
    ├── test_workflow.py
    └── validate_apis.py
```

## 🔑 核心配置

**必需 API**: NetEase, QQ Music, Gemini  
**可选 API**: Spotify

[📖 API 配置详情 →](docs/guides/DEPLOYMENT.md#service-configuration)

## 📖 文档导航

### 👥 用户文档

- **[快速开始](docs/QUICKSTART.md)** - 5分钟快速部署
- **[Dify 工作流设置](docs/guides/DIFY_WORKFLOW_SETUP.md)** - 工作流导入和配置 ⭐
- **[功能规格](docs/FUNCTIONAL_SPEC.md)** - 完整功能列表
- **[部署指南](docs/guides/DEPLOYMENT.md)** - 详细部署说明

### 🔧 开发者文档

- **[工作流详解](docs/guides/WORKFLOW_OVERVIEW.md)** - 技术架构和实现
- **[QQ音乐配置](docs/guides/QQMUSIC_API_SETUP.md)** - API 集成指南
- **[路线图](docs/ROADMAP.md)** - 未来计划和已知限制

### 📝 贡献者文档

- **[AI 协作指南](AGENTS.md)** - AI agent 工作流程
- **[项目状态](PROJECT_STATUS.md)** - 当前进度和下一步
- **[文档索引](docs/README.md)** - 所有文档列表
- **[修复索引](docs/FIXES_INDEX.md)** - Bug 修复记录
- **[变更日志](CHANGELOG.md)** - 版本历史

## 🐛 故障排除

常见问题请查看:

- [部署指南 - 故障排除](docs/guides/DEPLOYMENT.md#troubleshooting)
- [Dify 设置 - 常见问题](docs/guides/DIFY_WORKFLOW_SETUP.md#故障排除)
- [修复索引](docs/FIXES_INDEX.md)

## 🗺️ 路线图

**当前版本**: v0.1.0

**近期计划**:

- 增强错误处理和重试机制
- 实现缓存层提升性能
- 部署自动化工具

[查看完整路线图 →](docs/ROADMAP.md)

## 📊 已知限制

- 依赖非官方 API (NetEase, QQ Music)
- 无缓存机制
- 有限的错误恢复能力

[查看所有限制和解决方案 →](docs/ROADMAP.md#known-limitations)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

查看 [贡献指南](AGENTS.md) 了解 AI 协作流程和文档标准。

## 📄 许可证

MIT License

## 🔗 相关资源

- [Dify 官方文档](https://docs.dify.ai/)
- [NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)

---

**维护者**: [documentation-agent]  
**最后更新**: 2025-10-26

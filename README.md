# 音乐元数据自动核验系统

基于 Dify 平台构建的自动化音乐歌曲上架与核验工作流系统。

## 项目概述

本系统通过 Dify 工作流自动化处理音乐元数据的提取、验证和核对。系统接收网易云音乐歌曲 URL，自动提取元数据，并通过多个第三方平台（QQ 音乐、Spotify）进行交叉验证，最终生成包含核验状态的标准化数据报告。

## 核心功能

- **自动数据提取**: 从网易云音乐提取歌曲基础信息（标题、歌手、专辑、封面、歌词）
- **OCR 制作人员提取**: 使用 Google Gemini 2.5 Flash 从图片中提取制作人员名单
- **多源交叉验证**: 通过 QQ 音乐和 Spotify 进行数据核验
- **封面图比对**: 使用 AI 视觉能力比对不同来源的专辑封面
- **智能状态判定**: 自动标记数据为「确认」、「存疑」或「未查到」

## 技术架构

### 核心组件

- **Dify 平台**: 工作流编排引擎
- **NeteaseCloudMusicApi**: 网易云音乐数据源（社区维护）
- **QQ Music API**: QQ 音乐核验源（社区维护）
- **Spotify Web API**: Spotify 核验源（官方 API）
- **Google Gemini 2.5 Flash**: 多模态 AI（OCR + 图像比对）

### 系统架构图

```
用户输入 (URL)
    ↓
解析歌曲 ID
    ↓
并行获取数据
    ├─→ 网易云歌曲详情
    ├─→ 网易云歌词
    └─→ 制作人员图片 OCR (Gemini)
    ↓
数据规范化与整合
    ↓
多源核验（并行）
    ├─→ QQ 音乐搜索 + 详情
    ├─→ Spotify 认证 + 搜索 + 详情
    └─→ 封面图比对 (Gemini)
    ↓
数据比对与状态判定
    ↓
生成最终 JSON 报告
```

## 快速开始

### 前置要求

- Docker 和 Docker Compose
- Dify 平台实例（自托管或云服务）
- API 密钥：
  - Google Gemini API Key
  - Spotify Client ID 和 Client Secret

### 1. 部署 NeteaseCloudMusicApi

```bash
cd services/netease-api
docker-compose up -d
```

服务将在 `http://localhost:3000` 启动。

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填写必要的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# NeteaseCloudMusicApi
NETEASE_API_HOST=http://localhost:3000
```

### 3. 导入 Dify 工作流

1. 登录 Dify 平台
2. 创建新的 Workflow 应用
3. 导入 `dify-workflow/music-metadata-checker.yml`
4. 在工作流设置中配置环境变量

### 4. 测试工作流

在 Dify 工作流界面中，输入测试 URL：

```
https://music.163.com#/song?id=2758218600
```

## 项目结构

```
song-metadata-checker/
├── README.md                           # 项目说明文档
├── .env.example                        # 环境变量模板
├── docs/                               # 文档目录
│   └── 音乐网站歌曲信息核验流程.md      # 技术方案文档
├── dify-workflow/                      # Dify 工作流配置
│   ├── music-metadata-checker.yml      # 主工作流定义
│   └── nodes/                          # 节点配置
│       ├── code-nodes/                 # 代码节点脚本
│       │   ├── parse_url.py           # URL 解析
│       │   ├── normalize_data.py      # 数据规范化
│       │   ├── find_match.py          # 匹配算法
│       │   └── consolidate.py         # 数据整合
│       └── http-nodes/                 # HTTP 请求配置
│           ├── netease_song.json      # 网易云歌曲详情
│           ├── netease_lyric.json     # 网易云歌词
│           ├── spotify_auth.json      # Spotify 认证
│           ├── spotify_search.json    # Spotify 搜索
│           └── gemini_ocr.json        # Gemini OCR
├── services/                           # 外部服务配置
│   └── netease-api/                   # 网易云 API 服务
│       ├── docker-compose.yml         # Docker 配置
│       └── README.md                  # 服务说明
└── scripts/                            # 辅助脚本
    ├── test_workflow.py               # 工作流测试脚本
    └── validate_apis.py               # API 连通性测试
```

## 核心工作流节点

### 阶段一：数据提取

1. **Start 节点**: 接收 `song_url` 输入
2. **Code 节点**: 解析 URL 提取 `song_id`
3. **HTTP 节点**: 调用网易云 `/song/detail` 接口
4. **HTTP 节点**: 调用网易云 `/lyric` 接口
5. **Code 节点**: 构建初始数据结构

### 阶段二：OCR 提取

6. **HTTP 节点**: 调用 Gemini API 进行图片 OCR
7. **Code 节点**: 解析 OCR 结果并合并到元数据

### 阶段三：多源核验

8. **HTTP 节点**: Spotify OAuth 认证
9. **HTTP 节点**: Spotify 搜索
10. **Code 节点**: 找到最佳匹配
11. **HTTP 节点**: Spotify 曲目详情
12. **HTTP 节点**: QQ 音乐搜索
13. **Code 节点**: 找到最佳匹配
14. **HTTP 节点**: QQ 音乐详情
15. **HTTP 节点**: Gemini 封面图比对

### 阶段四：数据整合

16. **Code 节点**: 数据规范化
17. **Code 节点**: 比对逻辑与状态判定
18. **Code 节点**: 生成最终 JSON
19. **Answer 节点**: 输出结果

## 数据状态定义

- **「确认」(Confirmed)**: 网易云数据与至少一个核验源完全匹配
- **「存疑」(Questionable)**: 数据存在但有差异，或不同核验源结果矛盾
- **「未查到」(Not Found)**: 所有核验平台均未找到对应字段

## API 端点使用

### 网易云音乐 API

- `GET /song/detail?ids={song_id}` - 获取歌曲详情
- `GET /lyric?id={song_id}` - 获取歌词

### Spotify API

- `POST /api/token` - OAuth 认证
- `GET /v1/search?q={query}&type=track` - 搜索歌曲
- `GET /v1/tracks/{id}` - 获取曲目详情

### Google Gemini API

- `POST /v1beta/models/gemini-2.5-flash:generateContent` - OCR 和图像比对

## 错误处理

系统实现了完善的错误处理机制：

- 所有 HTTP 请求节点配置失败分支
- API 调用失败时自动降级，继续执行其他核验
- LLM 输出解析异常捕获
- 详细错误日志记录

## 性能优化建议

1. **缓存机制**: 使用 Redis 缓存已处理的歌曲数据
2. **并行请求**: 在 Code 节点中使用 asyncio 并行调用多个 API
3. **速率限制**: 实现请求队列避免触发 API 限流

## 运营考量

### 稳定性风险

- 网易云和 QQ 音乐使用非官方 API，存在失效风险
- 需要持续监控 API 可用性
- 建议定期更新 API 依赖

### 成本估算

- Gemini API: 按调用次数计费
- Spotify API: 免费层有速率限制
- 服务器: 根据流量选择合适配置

## 部署选项

### 自托管 Dify

```bash
git clone https://github.com/langgenius/dify.git
cd dify/docker
docker-compose up -d
```

### 云服务

使用 Dify Cloud 服务，无需自行部署。

## 测试

运行测试脚本验证系统功能：

```bash
# 测试 API 连通性
python scripts/validate_apis.py

# 测试完整工作流
python scripts/test_workflow.py --url "https://music.163.com#/song?id=2758218600"
```

## 贡献指南

欢迎提交 Issue 和 Pull Request。

## 许可证

MIT License

## 参考文档

- [Dify 官方文档](https://docs.dify.ai/)
- [NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)

## 联系方式

如有问题或建议，请提交 Issue。

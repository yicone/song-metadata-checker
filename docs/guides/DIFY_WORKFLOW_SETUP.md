# Dify 工作流设置指南

完整的 Dify 工作流导入、配置和测试指南。

## 📋 目录

- [前置条件](#前置条件)
- [工作流文件](#工作流文件)
- [导入工作流](#导入工作流)
- [配置环境变量](#配置环境变量)
- [测试工作流](#测试工作流)
- [故障排除](#故障排除)

---

## 前置条件

### 1. API 服务已启动

确认所有 API 服务正常运行：

```bash
poetry run python scripts/validate_apis.py
```

**预期结果**：

```
网易云音乐 API (数据源): ✅ 通过
QQ 音乐 API (核验源): ✅ 通过
Gemini API (OCR): ✅ 通过
Spotify API (可选): ✅ 通过 或 ❌ 失败（可选）
```

### 2. Dify 平台访问

**选项 A: 使用 Dify Cloud**

- 访问 [Dify Cloud](https://cloud.dify.ai/)
- 注册/登录账号
- 创建工作空间

**选项 B: 自托管 Dify**

```bash
git clone https://github.com/langgenius/dify.git
cd dify/docker
docker-compose up -d
```

访问 `http://localhost/install` 完成初始化。

---

## 工作流文件

**文件**: `dify-workflow/music-metadata-checker.yml`

**核验源状态**：

- ✅ **QQ Music**: 当前启用（必需）
- ⏭️ **Spotify**: 可选，当前禁用（调试优先级低）

**必需 API**：

- ✅ NetEase Cloud Music API（数据源）
- ✅ Google Gemini API（OCR，可选）
- ✅ QQ Music API（核验源）

**可选 API**：

- ⏭️ Spotify API（可选核验源，当前禁用）
- 参考 [启用 Spotify](WORKFLOW_OVERVIEW.md#enabling-spotify-validation)

---

## 导入工作流

### ⚠️ Dify Cloud 用户注意

**如果您使用 Dify Cloud**，YAML 导入可能会失败（Import Error），因为：

- YAML 文件包含外部文件引用（`code_file`, `config_file`）
- Dify Cloud 无法访问本地文件系统

**解决方案**：

- **推荐**: 使用 [Dify Cloud 手动创建指南](DIFY_CLOUD_MANUAL_SETUP.md) ⭐
- **备选**: 使用自托管 Dify（支持 YAML 导入）

---

### 步骤 1: 创建工作流应用

1. 登录 Dify 平台
2. 点击 **"创建应用"** 或 **"Create Application"**
3. 选择 **"工作流"** 或 **"Workflow"** 类型
4. 输入应用名称：`Music Metadata Checker`

### 步骤 2: 导入 DSL 文件（仅自托管 Dify）

**⚠️ 此步骤仅适用于自托管 Dify**

1. 在工作流编辑器中，点击右上角的 **"导入"** 或 **"Import"**
2. 选择 **"导入 DSL"** 或 **"Import DSL"**
3. 上传文件：`dify-workflow/music-metadata-checker.yml`
4. 点击 **"确认导入"**

**如果导入失败**：参考 [Dify Cloud 手动创建指南](DIFY_CLOUD_MANUAL_SETUP.md)

### 步骤 3: 验证导入

导入成功后，您应该看到：

- ✅ 多个节点已创建
- ✅ 节点之间有连接线
- ✅ 开始节点和结束节点存在

**节点数量**：约 12-15 个节点（不含 Spotify 节点）

---

## 配置环境变量

### 在 Dify 中配置

1. 点击工作流编辑器右上角的 **"设置"** 图标
2. 选择 **"环境变量"** 或 **"Environment Variables"**
3. 添加以下变量

### 必需变量（标准版）

```bash
# Google Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# NetEase Cloud Music API
NETEASE_API_HOST=http://localhost:3000

# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_AUTH_URL=https://accounts.spotify.com/api/token
SPOTIFY_API_BASE_URL=https://api.spotify.com/v1
```

### 必需变量（简化版）

```bash
# Google Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# NetEase Cloud Music API
NETEASE_API_HOST=http://localhost:3000

# QQ Music API
QQ_MUSIC_API_HOST=http://localhost:3001
```

### 可选变量

```bash
# 日志级别
LOG_LEVEL=INFO

# 超时设置（毫秒）
HTTP_TIMEOUT=30000
```

### ⚠️ 重要提示

**如果使用 Dify Cloud**：

- `NETEASE_API_HOST` 和 `QQ_MUSIC_API_HOST` 必须使用公网可访问的地址
- `localhost` 在云端无法访问
- 需要部署 API 服务到公网或使用内网穿透工具（如 ngrok）

**如果自托管 Dify**：

- 确保 Dify 容器可以访问 API 服务
- 如果 API 在宿主机上，使用 `host.docker.internal` 替代 `localhost`

---

## 测试工作流

### 测试输入

在 Dify 工作流的测试面板中输入：

**基础测试**：

```json
{
  "song_url": "https://music.163.com#/song?id=2758218600"
}
```

**包含 OCR 的测试**（可选）：

```json
{
  "song_url": "https://music.163.com#/song?id=2758218600",
  "credits_image_url": "https://example.com/credits.jpg"
}
```

### 预期输出

工作流应该返回类似以下的 JSON 结构：

```json
{
  "metadata": {
    "song_id": "2758218600",
    "source": "NetEase Cloud Music",
    "timestamp": "2025-10-27T00:00:00Z"
  },
  "fields": {
    "title": {
      "value": "歌曲名称",
      "status": "确认",
      "confirmed_by": ["QQ Music"]
    },
    "artists": {
      "value": ["艺术家1", "艺术家2"],
      "status": "确认",
      "confirmed_by": ["QQ Music", "Spotify"]
    },
    "album": {
      "value": "专辑名称",
      "status": "确认",
      "confirmed_by": ["QQ Music"]
    }
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

### 执行时间

- **正常执行**: 10-20 秒
- **包含 OCR**: 15-25 秒

如果超过 30 秒，检查：

- API 服务是否响应
- 网络连接是否正常
- Gemini API 配额是否充足

---

## 故障排除

### 问题 1: 导入失败 (Import Error)

**症状**: "Import Error" 或 "导入 DSL 失败"，无详细错误信息

**根本原因**:

- YAML 文件包含外部文件引用（`code_file`, `config_file`）
- Dify Cloud 无法访问本地文件系统
- 需要将代码内联到工作流中

**解决方案**：

1. **使用手动创建指南**（推荐）：
   - 查看 [Dify Cloud 手动创建指南](DIFY_CLOUD_MANUAL_SETUP.md)
   - 逐步在 Dify Cloud 中手动创建工作流
   - 直接在界面中编写代码

2. **使用自托管 Dify**：
   - 部署自己的 Dify 实例
   - 自托管版本支持外部文件引用
   - 可以直接导入 YAML 文件

3. **验证 YAML 格式**（仅自托管）：

   ```bash
   # 使用 YAML 验证工具
   python -c "import yaml; yaml.safe_load(open('dify-workflow/music-metadata-checker.yml'))"
   ```

---

### 问题 2: 环境变量未生效

**症状**: 节点报错 "Environment variable not found"

**解决方案**：

1. **检查变量名称**：
   - 确保变量名完全匹配（区分大小写）
   - 不要有多余的空格

2. **重新加载工作流**：
   - 保存环境变量后
   - 刷新页面或重新打开工作流

3. **使用节点内变量**：
   - 如果环境变量不工作
   - 可以在 HTTP 节点中直接配置 URL 和密钥

---

### 问题 3: API 调用失败

**症状**: HTTP 节点返回 404、500 或超时

**解决方案**：

1. **验证 API 可达性**：

   ```bash
   # 从 Dify 服务器测试
   curl http://localhost:3000
   curl http://localhost:3001
   ```

2. **检查网络配置**：
   - Dify Cloud: 使用公网地址
   - 自托管: 检查 Docker 网络配置

3. **查看 API 日志**：

   ```bash
   docker logs netease-music-api
   docker logs qqmusic-api
   ```

---

### 问题 4: Gemini API 超时

**症状**: OCR 或图像比对节点超时

**解决方案**：

1. **检查 API 密钥**：

   ```bash
   curl -H "x-goog-api-key: YOUR_KEY" \
     "https://generativelanguage.googleapis.com/v1beta/models"
   ```

2. **检查配额**：
   - 访问 [Google AI Studio](https://aistudio.google.com/)
   - 查看 API 使用情况和配额

3. **增加超时时间**：
   - 在 HTTP 节点设置中
   - 将超时从 30 秒增加到 60 秒

---

### 问题 5: Spotify 认证失败

**症状**: "Invalid client" 或 "Authentication failed"

**解决方案**：

1. **验证凭证**：

   ```bash
   # 测试 Spotify 认证
   curl -X POST "https://accounts.spotify.com/api/token" \
     -H "Authorization: Basic $(echo -n 'CLIENT_ID:CLIENT_SECRET' | base64)" \
     -d "grant_type=client_credentials"
   ```

2. **检查应用状态**：
   - 访问 [Spotify Dashboard](https://developer.spotify.com/dashboard)
   - 确认应用未被暂停

3. **使用简化版工作流**：
   - 如果 Spotify 不可用
   - 切换到使用 QQ 音乐的简化版

---

## 工作流优化

### 性能优化

1. **启用并行执行**：
   - QQ 音乐和 Spotify 搜索可以并行
   - 在 Dify 中配置并行分支

2. **添加缓存**：
   - 对频繁查询的歌曲启用缓存
   - 使用 Redis 或 Dify 内置缓存

3. **减少不必要的调用**：
   - 如果不需要 OCR，跳过图片上传
   - 如果不需要封面比对，禁用该节点

### 错误处理优化

1. **配置失败分支**：
   - 为每个 HTTP 节点添加失败处理
   - 记录错误但继续执行

2. **添加重试逻辑**：
   - 对临时性错误（超时、503）自动重试
   - 最多重试 3 次

3. **降级策略**：
   - 如果 QQ 音乐失败，尝试 Spotify
   - 如果所有核验源失败，标记为"未核验"

---

## 下一步

工作流配置完成后：

1. **运行完整测试**：

   ```bash
   poetry run python scripts/test_workflow.py \
     --url "https://music.163.com#/song?id=2758218600"
   ```

2. **集成到生产环境**：
   - 发布工作流为 API
   - 集成到您的应用中

3. **监控和维护**：
   - 设置日志收集
   - 监控 API 可用性
   - 定期检查核验准确性

---

## 相关文档

- [部署指南](DEPLOYMENT.md) - 完整部署说明
- [QQ 音乐配置](QQMUSIC_API_SETUP.md) - QQ 音乐 API 设置
- [工作流详解](WORKFLOW_OVERVIEW.md) - 技术架构
- [功能规格](../FUNCTIONAL_SPEC.md) - 功能说明

---

**最后更新**: 2025-10-27  
**维护者**: [documentation-agent]  
**审查频率**: 每月

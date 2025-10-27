# Dify 工作流打包指南

> **问题**: Dify Cloud 导入时需要完全自包含的 YML 文件，但我们的代码采用模块化结构  
> **解决方案**: 使用构建脚本将模块化文件合并为单个自包含的 YML

---

## 🎯 为什么使用 Bundle？

### 传统方式的问题

在 Dify Cloud 中手动创建工作流需要：

1. ❌ **手动创建 11+ 个节点** - 耗时且容易出错
2. ❌ **逐个配置每个节点** - 复制粘贴代码和配置
3. ❌ **手动连接节点** - 设置依赖关系
4. ❌ **难以维护** - YML 文件和手动配置容易不同步
5. ❌ **无法版本控制** - 手动配置难以追踪变更

### Bundle 方式的优势

使用 `music-metadata-checker-bundle.yml`：

1. ✅ **一键导入** - 在 Dify Cloud 选择「导入 DSL 文件」即可
2. ✅ **完全自包含** - 所有代码和配置已内嵌
3. ✅ **版本控制** - Bundle 文件可以 Git 追踪
4. ✅ **易于更新** - 修改源文件后重新构建即可
5. ✅ **无需手动创建** - 节省大量时间

### 对比

| 操作 | 手动创建 | Bundle 导入 |
|------|---------|------------|
| 创建节点 | 手动创建 11+ 个 | 自动创建 |
| 配置代码 | 逐个复制粘贴 | 已内嵌 |
| 设置依赖 | 手动连接 | 已配置 |
| 所需时间 | 1-2 小时 | 2-3 分钟 |
| 出错风险 | 高 | 低 |
| 维护成本 | 高 | 低 |

---

## 🎯 双轨制维护策略

### 开发环境（模块化）

```
dify-workflow/
├── music-metadata-checker.yml          # 工作流定义（引用外部文件）
└── nodes/
    ├── code-nodes/                     # Python 代码文件
    │   ├── parse_url.py
    │   ├── consolidate.py
    │   └── ...
    └── http-nodes/                     # HTTP 配置文件
        ├── netease_song_detail.json
        ├── qqmusic_search.json
        └── ...
```

**优势**:

- ✅ 代码编辑器支持（语法高亮、代码提示）
- ✅ 版本控制友好（Git diff 清晰）
- ✅ 模块化开发（职责分离）
- ✅ 易于测试和调试

---

### 生产环境（自包含）

```
dify-workflow/
└── music-metadata-checker-bundle.yml   # 打包后的自包含文件
```

**特点**:

- ✅ 所有代码和配置内嵌在单个 YML 中
- ✅ 可直接导入 Dify Cloud
- ✅ 无外部依赖

---

## 🚀 使用步骤

### 步骤 1: 开发和修改

在 `dify-workflow/nodes/` 目录中编辑代码和配置：

```bash
# 编辑代码节点
code dify-workflow/nodes/code-nodes/consolidate.py

# 编辑 HTTP 节点
code dify-workflow/nodes/http-nodes/gemini_image_compare.json
```

---

### 步骤 2: 构建打包文件

运行构建脚本：

```bash
# 使用 Poetry
poetry run python scripts/build_dify_bundle.py

# 或直接运行
python scripts/build_dify_bundle.py
```

**输出示例**:

```
🚀 开始构建 Dify 工作流打包文件...

📖 读取源文件: dify-workflow/music-metadata-checker.yml

🔧 处理 15 个节点:

  节点: parse_url (code)
  ✅ 内嵌代码: parse_url.py

  节点: netease_song_detail (http-request)
  ✅ 内嵌配置: netease_song_detail.json

  节点: consolidate (code)
  ✅ 内嵌代码: consolidate.py

  ...

💾 写入打包文件: dify-workflow/music-metadata-checker-bundle.yml

✅ 打包完成！

📦 输出文件: /path/to/music-metadata-checker-bundle.yml
📏 文件大小: 45.23 KB

🎯 下一步:
   1. 在 Dify Cloud 选择「导入 DSL 文件」
   2. 上传: music-metadata-checker-bundle.yml
   3. 配置环境变量
   4. 运行测试
```

---

### 步骤 3: 导入到 Dify Cloud

#### 3.1 导入工作流

1. **登录 Dify Cloud**
   - 访问 <https://cloud.dify.ai>
   - 或使用自托管的 Dify 实例

2. **导入 DSL 文件**
   - 点击「工作流」→「导入 DSL 文件」
   - 选择 `music-metadata-checker-bundle.yml`
   - 点击「导入」
   - 等待导入完成（通常 5-10 秒）

3. **验证导入**
   - 检查所有节点是否正确加载
   - 确认节点连接关系正确
   - 验证代码节点包含完整代码

#### 3.2 配置环境变量

在 Dify 工作流设置中添加以下环境变量：

```bash
# 必需变量
NETEASE_API_HOST=https://your-netease-api.com
QQ_MUSIC_API_HOST=https://your-qqmusic-api.com
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# 可选变量（启用 Spotify 时需要）
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

**详细配置说明**: 参见 [部署指南 - 环境变量配置](../docs/guides/DEPLOYMENT.md#api-keys-required)

#### 3.3 测试工作流

1. **运行测试**
   - 输入测试 URL: `https://music.163.com#/song?id=2758218600`
   - 验证工作流执行

---

## 📁 文件结构对比

### 模块化版本（开发）

```yaml
# music-metadata-checker.yml
nodes:
  - id: "parse_url"
    type: "code"
    config:
      code_file: "nodes/code-nodes/parse_url.py"  # 引用外部文件
      
  - id: "netease_song_detail"
    type: "http-request"
    config_file: "nodes/http-nodes/netease_song_detail.json"  # 引用外部文件
```

---

### 自包含版本（生产）

```yaml
# music-metadata-checker-bundle.yml
nodes:
  - id: "parse_url"
    type: "code"
    config:
      code: |                                      # 代码直接内嵌
        from urllib.parse import urlparse, parse_qs
        
        def main(song_url: str) -> dict:
            # ... 完整代码 ...
      
  - id: "netease_song_detail"
    type: "http-request"
    config:                                        # 配置直接内嵌
      method: "GET"
      url: "{{#env.NETEASE_API_HOST#}}/song/detail"
      # ... 完整配置 ...
```

---

## 🔄 工作流程

### 开发流程

```
1. 编辑代码
   ↓
   dify-workflow/nodes/*.py
   
2. 本地测试（可选）
   ↓
   poetry run python -m pytest
   
3. 构建打包文件
   ↓
   poetry run python scripts/build_dify_bundle.py
   
4. 导入 Dify Cloud
   ↓
   上传 music-metadata-checker-bundle.yml
   
5. 在线测试
   ↓
   Dify Cloud 工作流测试
```

---

### 版本控制

**提交到 Git**:

```bash
# 提交模块化文件（推荐）
git add dify-workflow/nodes/
git add dify-workflow/music-metadata-checker.yml
git commit -m "feat: 更新 consolidate 节点逻辑"

# 打包文件可以忽略（自动生成）
echo "music-metadata-checker-bundle.yml" >> .gitignore
```

**或者两者都提交**:

```bash
# 同时提交模块化和打包文件
git add dify-workflow/
git commit -m "feat: 更新工作流并重新打包"
```

---

## 🛠️ 构建脚本详解

### 脚本功能

**`scripts/build_dify_bundle.py`** 做了什么：

1. **读取源 YML** - 加载 `music-metadata-checker.yml`
2. **处理代码节点** - 将 `code_file: "path/to/file.py"` 替换为 `code: "内嵌代码"`
3. **处理 HTTP 节点** - 将 `config_file: "path/to/config.json"` 替换为 `config: {...}`
4. **添加元数据** - 标记为打包版本
5. **输出 YML** - 生成 `music-metadata-checker-bundle.yml`

---

### 自定义构建

如果需要修改构建逻辑，编辑 `scripts/build_dify_bundle.py`：

```python
# 示例：添加额外的处理步骤
def process_custom_node(node: Dict[str, Any]) -> Dict[str, Any]:
    # 自定义处理逻辑
    return node

# 在 build_bundle() 中调用
for node in workflow.get('nodes', []):
    node = process_custom_node(node)
```

---

## 📊 优势对比

| 特性 | 模块化版本 | 自包含版本 |
|------|----------|----------|
| **开发体验** | ✅ 优秀（IDE 支持） | ❌ 较差（大文件） |
| **版本控制** | ✅ 清晰（独立文件） | ❌ 混乱（大 diff） |
| **导入 Dify** | ❌ 不支持 | ✅ 直接导入 |
| **维护成本** | ✅ 低（模块化） | ❌ 高（单文件） |
| **适用场景** | 开发、测试 | 部署、分享 |

---

## 🔧 故障排除

### 问题 1: 构建脚本找不到文件

**错误**:

```
⚠️ 代码文件不存在: parse_url.py
```

**解决**:

- 检查 `music-metadata-checker.yml` 中的路径是否正确
- 确保 `nodes/code-nodes/parse_url.py` 文件存在

---

### 问题 2: 导入 Dify 时报错

**错误**:

```
DSL 格式不正确
```

**解决**:

- 检查生成的 `music-metadata-checker-bundle.yml` 是否有语法错误
- 使用 YAML 验证工具检查格式：

  ```bash
  poetry run python -c "import yaml; yaml.safe_load(open('dify-workflow/music-metadata-checker-bundle.yml'))"
  ```

---

### 问题 3: 代码节点执行失败

**错误**:

```
Code execution failed
```

**解决**:

- 检查代码是否有语法错误
- 在本地测试代码：

  ```bash
  poetry run python dify-workflow/nodes/code-nodes/parse_url.py
  ```

---

## 📚 相关文档

- **[README.md](README.md)** - Dify 工作流目录说明
- **[DIFY_CLOUD_MANUAL_SETUP.md](../docs/guides/DIFY_CLOUD_MANUAL_SETUP.md)** - 手动配置指南
- **[Dify 官方文档](https://docs.dify.ai)** - DSL 格式规范

---

## 💡 最佳实践

### 1. 开发时使用模块化

```bash
# 编辑代码
code dify-workflow/nodes/code-nodes/consolidate.py

# 测试代码
poetry run python -m pytest tests/test_consolidate.py
```

### 2. 部署前构建打包

```bash
# 构建
poetry run python scripts/build_dify_bundle.py

# 验证
ls -lh dify-workflow/music-metadata-checker-bundle.yml
```

### 3. 版本控制策略

```bash
# 提交模块化文件
git add dify-workflow/nodes/
git add dify-workflow/music-metadata-checker.yml

# 忽略打包文件（可选）
echo "music-metadata-checker-bundle.yml" >> .gitignore
```

### 4. 文档同步

每次修改后：

- ✅ 更新 `DIFY_CLOUD_MANUAL_SETUP.md`
- ✅ 重新构建打包文件
- ✅ 测试导入和执行

---

## ✅ 快速检查清单

部署前检查：

- [ ] 所有代码文件都在 `nodes/code-nodes/` 中
- [ ] 所有 HTTP 配置都在 `nodes/http-nodes/` 中
- [ ] `music-metadata-checker.yml` 正确引用所有文件
- [ ] 运行构建脚本成功
- [ ] 生成的 `music-metadata-checker-bundle.yml` 文件存在
- [ ] YAML 格式验证通过
- [ ] 文件大小合理（< 1MB）

---

**最后更新**: 2025-10-27  
**维护者**: [documentation-agent]  
**脚本位置**: `scripts/build_dify_bundle.py`

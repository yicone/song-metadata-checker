# Dify Workflow 同步更新说明

> **日期**: 2025-10-27  
> **基准**: `docs/guides/DIFY_CLOUD_MANUAL_SETUP.md`  
> **状态**: ✅ 已完成

---

## 🎯 更新目标

将 `dify-workflow` 目录中的配置同步到经过测试的 `DIFY_CLOUD_MANUAL_SETUP.md` 版本。

---

## 📝 更新内容

### 1. 代码节点 (code-nodes/)

#### ✅ 已创建/更新

| 文件名 | 状态 | 说明 |
|--------|------|------|
| `parse_url.py` | ✅ 保留 | URL 解析节点 |
| `initial_data_structuring.py` | ✅ 保留 | 初始数据结构化 |
| `find_qqmusic_match.py` | ✅ 新建 | 找到 QQ 音乐匹配（替代 find_match.py） |
| `parse_qqmusic_response.py` | ✅ 新建 | 解析 QQ 音乐响应（平铺输出） |
| `parse_cover_url.py` | ✅ 新建 | 解析封面图 URL |
| `download_and_encode_covers.py` | ✅ 新建 | 下载并转换封面图为 Base64 |
| `parse_gemini_response.py` | ✅ 新建 | 解析 Gemini 响应 |
| `consolidate.py` | ✅ 更新 | Phase 1 增强版（新输入变量） |

#### ❌ 已删除（过时）

| 文件名 | 原因 |
|--------|------|
| `find_match.py` | 替换为 `find_qqmusic_match.py` |
| `normalize_data.py` | 文档中没有此节点 |
| `parse_ocr_json.py` | 文档中没有此节点 |

---

### 2. HTTP 节点 (http-nodes/)

#### ✅ 已创建/更新

| 文件名 | 状态 | 说明 |
|--------|------|------|
| `netease_song_detail.json` | ✅ 保留 | 网易云歌曲详情 |
| `netease_lyric.json` | ✅ 保留 | 网易云歌词 |
| `qqmusic_search.json` | ✅ 保留 | QQ 音乐搜索 |
| `qqmusic_song_detail.json` | ✅ 保留 | QQ 音乐歌曲详情 |
| `qqmusic_cover_url_raw.json` | ✅ 新建 | QQ 音乐封面图 URL |
| `gemini_cover_comparison.json` | ✅ 重命名 | Gemini 封面图比较（原 gemini_image_compare.json） |

#### ⏭️ 保留但未使用

| 文件名 | 状态 | 说明 |
|--------|------|------|
| `gemini_ocr.json` | ⏭️ 保留 | 文档中未提及，但可能用于未来功能 |
| `spotify_*.json` | ⏭️ 保留 | Spotify 当前禁用，预留接口 |

---

### 3. 主配置文件

| 文件名 | 状态 | 说明 |
|--------|------|------|
| `music-metadata-checker.yml` | ⏳ 待更新 | 需要更新节点引用 |

---

## 🔄 节点对应关系

### 文档中的工作流节点（16个）

1. **Start** - 输入变量
2. **parse_url** - 解析 URL
3. **netease_song_detail** - 获取网易云歌曲详情
4. **netease_lyric** - 获取网易云歌词
5. **initial_data_structuring** - 初始数据结构化
6. **qqmusic_search** - QQ 音乐搜索
7. **find_qqmusic_match** - 找到 QQ 音乐匹配
8. **check_qqmusic_match** - IF/ELSE 条件判断
9. **qqmusic_song_detail** - 获取 QQ 音乐详情
10. **parse_qqmusic_response** - 解析 QQ 音乐响应
11. **qqmusic_cover_url_raw** - 获取 QQ 音乐封面图 URL
12. **parse_cover_url** - 解析封面图 URL
13. **download_and_encode_covers** (可选) - 下载并转换封面图
14. **gemini_cover_comparison** (可选) - Gemini 封面图比较
15. **parse_gemini_response** (可选) - 解析 Gemini 响应
16. **consolidate** - 数据整合与核验
17. **End** - 输出结果

---

## 📊 关键变更

### 1. consolidate 节点输入变量

**之前**:

```python
def main(
    normalized_data: dict,
    cover_match_result: str = None
) -> dict:
```

**现在**:

```python
def main(
    netease_data: dict,
    qqmusic_track_name: str = "",
    qqmusic_interval: int = 0,
    qqmusic_album_name: str = "",
    qqmusic_parsed_data: dict = None,
    gemini_is_same: bool = None,
    gemini_confidence: float = None,
    gemini_differences: list = None,
    gemini_notes: str = None
) -> dict:
```

**原因**: 使用平铺字段避免 Dify Cloud 嵌套访问限制

---

### 2. 新增 Phase 1 增强功能

#### 歌词比较

- 自动去除时间戳
- 计算文本相似度
- 95% 确认，80% 存疑

#### 时长比较

- ±2 秒容差
- 自动格式化为 MM:SS

#### 封面图增强

- 使用 Gemini AI 比较
- 结构化 JSON 响应
- 包含置信度和差异列表

---

### 3. 数据流优化

**之前**:

```
netease → normalize → consolidate
qqmusic → normalize → consolidate
```

**现在**:

```
netease → initial_data_structuring → consolidate
qqmusic → parse_qqmusic_response → consolidate (平铺字段)
gemini → parse_gemini_response → consolidate (平铺字段)
```

**优势**: 避免嵌套访问，提高可靠性

---

## ✅ 验证清单

### 代码节点

- [x] `parse_url.py` - 与文档一致
- [x] `initial_data_structuring.py` - 与文档一致
- [x] `find_qqmusic_match.py` - 新建，与文档一致
- [x] `parse_qqmusic_response.py` - 新建，与文档一致
- [x] `parse_cover_url.py` - 新建，与文档一致
- [x] `download_and_encode_covers.py` - 新建，与文档一致
- [x] `parse_gemini_response.py` - 新建，与文档一致
- [x] `consolidate.py` - 更新为 Phase 1 版本

### HTTP 节点

- [x] `netease_song_detail.json` - 已存在
- [x] `netease_lyric.json` - 已存在
- [x] `qqmusic_search.json` - 已存在
- [x] `qqmusic_song_detail.json` - 已存在
- [x] `qqmusic_cover_url_raw.json` - 新建
- [x] `gemini_cover_comparison.json` - 重命名

### 主配置

- [ ] `music-metadata-checker.yml` - 待更新节点引用

---

## 🚀 下一步

### 1. 更新主配置文件

需要更新 `music-metadata-checker.yml` 中的节点引用：

```yaml
nodes:
  # 更新节点名称
  - id: "find_qqmusic_match"  # 原 find_match
    type: "code"
    config:
      code_file: "nodes/code-nodes/find_qqmusic_match.py"
  
  # 添加新节点
  - id: "parse_qqmusic_response"
    type: "code"
    config:
      code_file: "nodes/code-nodes/parse_qqmusic_response.py"
  
  # ... 其他新节点
```

### 2. 运行构建脚本

```bash
poetry run python scripts/build_dify_bundle.py
```

### 3. 测试导入

1. 导入生成的 `music-metadata-checker-bundle.yml`
2. 配置环境变量
3. 运行测试

---

## 📚 相关文档

- **[DIFY_CLOUD_MANUAL_SETUP.md](../docs/guides/DIFY_CLOUD_MANUAL_SETUP.md)** - 手动配置指南（基准）
- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - 打包构建指南
- **[README.md](README.md)** - 工作流目录说明

---

**更新时间**: 2025-10-27  
**维护者**: [documentation-agent]  
**状态**: ✅ 代码和 HTTP 节点已同步，主配置待更新

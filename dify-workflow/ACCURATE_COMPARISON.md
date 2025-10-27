# 源 YML vs Bundle 准确对比报告

> **日期**: 2025-10-27  
> **源文件**: music-metadata-checker.yml  
> **Bundle 文件**: music-metadata-checker-bundle.yml  
> **构建工具**: build_dify_bundle.py

---

## 📊 节点对比表

| # | 节点 ID | 源 YML 标题 | Bundle 标题 | 类型 | 代码文件 | 代码状态 | 状态 |
|---|---------|------------|------------|------|---------|---------|------|
| 1 | `start` | 开始 | 开始 | start | - | - | ✅ 一致 |
| 2 | `parse_url` | 解析 URL | 解析 URL | code | parse_url.py | ✅ 已内嵌 | ✅ 一致 |
| 3 | `netease_song_detail` | 获取网易云歌曲详情 | 获取网易云歌曲详情 | http-request | - | - | ✅ 一致 |
| 4 | `netease_lyric` | 获取网易云歌词 | 获取网易云歌词 | http-request | - | - | ✅ 一致 |
| 5 | `initial_data_structuring` | 初始数据结构化 | 初始数据结构化 | code | initial_data_structuring.py | ✅ 已内嵌 | ✅ 一致 |
| 6 | `gemini_ocr` | Gemini OCR 提取制作人员 | Gemini OCR 提取制作人员 | http-request | - | - | ✅ 一致 |
| 7 | `parse_ocr_json` | 解析 OCR 结果 | 解析 OCR 结果 | code | parse_ocr_json.py | ⚠️ parse_ocr_json.py | ✅ 一致 |
| 8 | `qqmusic_search` | QQ 音乐搜索 | QQ 音乐搜索 | http-request | - | - | ✅ 一致 |
| 9 | `find_qqmusic_match` | 找到 QQ 音乐匹配 | 找到 QQ 音乐匹配 | code | find_qqmusic_match.py | ✅ 已内嵌 | ✅ 一致 |
| 10 | `qqmusic_song_detail` | 获取 QQ 音乐歌曲详情 | 获取 QQ 音乐歌曲详情 | http-request | - | - | ✅ 一致 |
| 11 | `normalize_data` | 数据规范化 | 数据规范化 | code | normalize_data.py | ⚠️ normalize_data.py | ✅ 一致 |
| 12 | `consolidate` | 数据整合与核验 | 数据整合与核验 | code | consolidate.py | ✅ 已内嵌 | ✅ 一致 |
| 13 | `end` | 输出结果 | 输出结果 | answer | - | - | ✅ 一致 |

---

## 📈 统计总结

| 项目 | 数量 |
|------|------|
| 源 YML 节点总数 | 13 |
| Bundle 节点总数 | 13 |
| 完全一致 | 13 ✅ |
| 标题不同 | 0 |
| 代码节点 | 6 |
| 代码已内嵌 | 4 ✅ |
| 代码文件缺失 | 2 ⚠️ |

---

## ⚠️ 缺失的代码文件

### 1. parse_ocr_json.py

**节点**: `parse_ocr_json` (解析 OCR 结果)  
**类型**: Code Node  
**状态**: ❌ 文件不存在

**影响**:

- 该节点在 Dify 中会显示错误
- OCR 功能无法正常工作

**解决方案**:

创建 `dify-workflow/nodes/code-nodes/parse_ocr_json.py`:

```python
from typing import TypedDict, Dict, Any, Optional

class ParseOcrJsonOutput(TypedDict):
    """OCR JSON 解析输出"""
    metadata: Optional[Dict[str, Any]]
    success: bool
    error: str

def main(gemini_response: str, metadata: dict) -> ParseOcrJsonOutput:
    """
    解析 Gemini OCR 响应
    提取制作人员信息并合并到元数据
    
    Args:
        gemini_response: Gemini API 返回的 JSON 字符串
        metadata: 现有的元数据对象
        
    Returns:
        更新后的元数据
    """
    import json
    
    try:
        # 解析 Gemini 响应
        response_data = json.loads(gemini_response) if isinstance(gemini_response, str) else gemini_response
        
        # 提取制作人员信息
        # TODO: 根据实际 Gemini 响应格式实现
        credits = {}
        
        # 更新元数据
        updated_metadata = metadata.copy()
        updated_metadata['credits'] = credits
        
        return {
            "metadata": updated_metadata,
            "success": True,
            "error": ""
        }
    except Exception as e:
        return {
            "metadata": metadata,
            "success": False,
            "error": f"OCR 解析失败: {str(e)}"
        }
```

---

### 2. normalize_data.py

**节点**: `normalize_data` (数据规范化)  
**类型**: Code Node  
**状态**: ❌ 文件不存在

**影响**:

- 该节点在 Dify 中会显示错误
- 数据整合流程无法完成

**解决方案**:

创建 `dify-workflow/nodes/code-nodes/normalize_data.py`:

```python
from typing import TypedDict, Dict, Any, Optional

class NormalizeDataOutput(TypedDict):
    """数据标准化输出"""
    normalized_data: Dict[str, Any]
    success: bool
    error: str

def main(
    netease_data: dict,
    spotify_data: str = "",
    qqmusic_data: dict = None
) -> NormalizeDataOutput:
    """
    规范化来自不同平台的数据
    
    Args:
        netease_data: 网易云音乐数据
        spotify_data: Spotify 数据（当前为空字符串，未启用）
        qqmusic_data: QQ 音乐数据
        
    Returns:
        标准化后的数据对象
    """
    try:
        normalized = {
            "netease": netease_data or {},
            "qqmusic": qqmusic_data or {},
            "spotify": {}  # Spotify 当前禁用
        }
        
        return {
            "normalized_data": normalized,
            "success": True,
            "error": ""
        }
    except Exception as e:
        return {
            "normalized_data": {},
            "success": False,
            "error": f"数据标准化失败: {str(e)}"
        }
```

---

## ✅ 已成功内嵌的代码节点

| 节点 ID | 文件 | 状态 |
|---------|------|------|
| `parse_url` | parse_url.py | ✅ 已内嵌 |
| `initial_data_structuring` | initial_data_structuring.py | ✅ 已内嵌 |
| `find_qqmusic_match` | find_qqmusic_match.py | ✅ 已内嵌 |
| `consolidate` | consolidate.py | ✅ 已内嵌 |

**说明**: 这些节点的代码已成功内嵌到 Bundle 中，包括 models.py 的内联。

---

## 🔍 与文档的关系

### 重要说明

`music-metadata-checker.yml` 是**新创建的工作流定义文件**，与 `docs/guides/DIFY_CLOUD_MANUAL_SETUP.md` 文档是**不同的内容**：

- **文档** (`DIFY_CLOUD_MANUAL_SETUP.md`):
  - 手动设置指南
  - 逐步教用户如何在 Dify Cloud UI 中创建工作流
  - 不包含 `parse_ocr_json` 和 `normalize_data` 节点

- **YML 文件** (`music-metadata-checker.yml`):
  - 完整的工作流定义
  - 用于自动化构建和导入
  - 包含所有节点定义，包括新增的节点

### 为什么会有差异？

1. **文档是手动设置指南** - 可能是早期版本或简化版本
2. **YML 是完整定义** - 包含最新的工作流架构
3. **两者服务不同目的**:
   - 文档：教学和理解
   - YML：自动化和部署

---

## 🎯 推荐行动

### 立即行动（必需）

1. **创建缺失的代码文件**

   ```bash
   # 创建 parse_ocr_json.py
   # 创建 normalize_data.py
   ```

2. **重新构建 Bundle**

   ```bash
   poetry run python scripts/build_dify_bundle.py
   ```

3. **验证构建结果**
   - 检查无 "代码文件不存在" 警告
   - 确认文件大小合理
   - 验证所有代码已内嵌

### 后续行动（建议）

1. **更新文档**
   - 在 `DIFY_CLOUD_MANUAL_SETUP.md` 中添加新节点的说明
   - 或创建新的文档说明 YML 文件的使用

2. **保持同步**
   - 确保 YML 文件和文档保持一致
   - 或明确说明两者的不同用途

---

## 📋 验证清单

创建文件后应验证：

- [ ] parse_ocr_json.py 已创建
- [ ] normalize_data.py 已创建
- [ ] 两个文件都包含 TypedDict 类型定义
- [ ] 重新构建 Bundle 成功
- [ ] 无 "代码文件不存在" 警告
- [ ] 所有代码节点状态为 "✅ 已内嵌"
- [ ] Bundle 文件可以导入 Dify Cloud

---

**生成时间**: 2025-10-27  
**工具**: build_dify_bundle.py + Python 对比脚本  
**状态**: ⚠️ 需要创建 2 个缺失的代码文件

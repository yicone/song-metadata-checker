# 批量更新所有 Code Node 使用 Pydantic

> **状态**: 📋 待执行  
> **预计时间**: 60-90 分钟  
> **已完成**: 2/8 节点

---

## ✅ 已完成

1. ✅ **parse_url.py** - 已更新并测试通过
2. ✅ **initial_data_structuring.py** - 已更新

---

## 📋 待更新列表

### 3. find_qqmusic_match.py

**当前返回**:

```python
return {
    "match_id": "",
    "match_name": "",
    "match_album": "",
    "match_found": False,
    "error": "搜索无结果"
}
```

**更新为**:

```python
from models import FindQQMusicMatchOutput

output = FindQQMusicMatchOutput(
    match_id="",
    match_name="",
    match_album="",
    match_found=False,
    error="搜索无结果"
)
return output.model_dump()
```

---

### 4. parse_qqmusic_response.py

**当前返回**:

```python
return {
    "parsed_data": qqmusic_parsed,
    "track_name": track_info.get('name', ''),
    "track_title": track_info.get('title', ''),
    # ... 更多字段
    "success": True,
    "error": ""
}
```

**更新为**:

```python
from models import ParseQQMusicResponseOutput

output = ParseQQMusicResponseOutput(
    parsed_data=qqmusic_parsed,
    track_name=track_info.get('name', ''),
    track_title=track_info.get('title', ''),
    # ... 更多字段
    success=True,
    error=""
)
return output.model_dump()
```

---

### 5. parse_cover_url.py

**当前返回**:

```python
return {
    "cover_url": image_url,
    "success": True,
    "error": ""
}
```

**更新为**:

```python
from models import ParseCoverUrlOutput

output = ParseCoverUrlOutput(
    cover_url=image_url,
    success=True,
    error=""
)
return output.model_dump()
```

---

### 6. download_and_encode_covers.py

**当前返回**:

```python
return {
    "netease_cover_base64": netease_base64,
    "qqmusic_cover_base64": qqmusic_base64,
    "success": True,
    "error": ""
}
```

**更新为**:

```python
from models import DownloadAndEncodeCoversOutput

output = DownloadAndEncodeCoversOutput(
    netease_cover_base64=netease_base64,
    qqmusic_cover_base64=qqmusic_base64,
    success=True,
    error=""
)
return output.model_dump()
```

---

### 7. parse_gemini_response.py

**当前返回**:

```python
return {
    "is_same": result_json.get('is_same', False),
    "confidence": result_json.get('confidence', 0.0),
    "differences": result_json.get('differences', []),
    "notes": result_json.get('notes', ''),
    "raw_json": json_text,
    "success": True,
    "error": ""
}
```

**更新为**:

```python
from models import ParseGeminiResponseOutput

output = ParseGeminiResponseOutput(
    is_same=result_json.get('is_same', False),
    confidence=result_json.get('confidence', 0.0),
    differences=result_json.get('differences', []),
    notes=result_json.get('notes', ''),
    raw_json=json_text,
    success=True,
    error=""
)
return output.model_dump()
```

---

### 8. consolidate.py

**当前返回**:

```python
return {
    "final_report": report,
    "success": True,
    "error": ""
}
```

**更新为**:

```python
from models import ConsolidateOutput

output = ConsolidateOutput(
    final_report=report,
    success=True,
    error=""
)
return output.model_dump()
```

---

## 🔧 更新步骤（每个文件）

### 步骤 1: 添加导入

在文件顶部添加：

```python
from models import YourOutputModel
```

### 步骤 2: 更新所有返回语句

找到所有 `return {` 语句，替换为：

```python
output = YourOutputModel(...)
return output.model_dump()
```

### 步骤 3: 测试

```bash
poetry run pytest tests/dify_workflow/test_your_node.py -v
```

---

## ✅ 验证清单

更新每个文件后，确保：

- [ ] 导入了正确的模型
- [ ] 所有返回路径都使用模型
- [ ] 测试通过
- [ ] 没有 lint 错误

---

## 🚀 快速执行

### 一次性运行所有测试

```bash
poetry run pytest tests/dify_workflow/ -v
```

### 预期结果

✅ 42/42 测试通过

---

## 📊 进度追踪

| 文件 | 状态 | 测试 |
|------|------|------|
| parse_url.py | ✅ 完成 | ✅ 通过 |
| initial_data_structuring.py | ✅ 完成 | ⏳ 待测试 |
| find_qqmusic_match.py | ⏳ 待更新 | - |
| parse_qqmusic_response.py | ⏳ 待更新 | - |
| parse_cover_url.py | ⏳ 待更新 | - |
| download_and_encode_covers.py | ⏳ 待更新 | - |
| parse_gemini_response.py | ⏳ 待更新 | - |
| consolidate.py | ⏳ 待更新 | - |

---

## 💡 提示

### 常见模式

**成功情况**:

```python
output = YourModel(
    field1=value1,
    field2=value2,
    success=True,
    error=""
)
return output.model_dump()
```

**错误情况**:

```python
output = YourModel(
    field1=default1,
    field2=default2,
    success=False,
    error=str(e)
)
return output.model_dump()
```

### 注意事项

1. **保持字段名一致** - 模型字段名必须与原返回字典的键名一致
2. **所有返回路径** - 确保所有 return 语句都使用模型
3. **异常处理** - try/except 块中的返回也要使用模型

---

**开始时间**: 2025-10-27  
**预计完成**: 2025-10-27  
**状态**: 🚧 进行中

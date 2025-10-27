# Pydantic 输出验证指南

> **日期**: 2025-10-27  
> **更新内容**: 为所有 Code Node 添加 Pydantic 输出验证  
> **状态**: ✅ 完成

---

## 🎯 为什么使用 Pydantic？

### 1. 运行时类型验证

Pydantic 在运行时验证数据类型，确保输出符合预期：

```python
# ❌ 没有验证 - 可能返回错误类型
def main(url: str) -> dict:
    return {
        "song_id": 123,  # 应该是 str，但返回了 int
        "success": "true"  # 应该是 bool，但返回了 str
    }

# ✅ 有验证 - Pydantic 会自动转换或报错
output = ParseUrlOutput(
    song_id="123",  # 正确的类型
    success=True,   # 正确的类型
    error=None
)
return output.model_dump()
```

### 2. 自动数据转换

Pydantic 会尝试自动转换兼容的类型：

```python
output = ParseUrlOutput(
    song_id=123,      # int → str (自动转换)
    success="true",   # str → bool (自动转换)
    error=None
)
# 结果: {"song_id": "123", "success": True, "error": None}
```

### 3. 默认值管理

使用 `Field` 定义默认值和描述：

```python
class ParseUrlOutput(BaseModel):
    song_id: Optional[str] = Field(None, description="提取的歌曲 ID")
    success: bool = Field(..., description="解析是否成功")  # ... 表示必填
    error: Optional[str] = Field(None, description="错误信息")
```

### 4. 数据验证

Pydantic 会验证数据的有效性：

```python
class ParseGeminiResponseOutput(BaseModel):
    confidence: float = Field(0.0, ge=0.0, le=1.0)  # 必须在 0.0-1.0 之间
    differences: List[str] = Field(default_factory=list)  # 必须是字符串列表
```

---

## 📝 模型定义

所有模型定义在 `models.py` 中：

```python
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ParseUrlOutput(BaseModel):
    """URL 解析输出模型"""
    song_id: Optional[str] = Field(None, description="提取的歌曲 ID")
    success: bool = Field(..., description="解析是否成功")
    error: Optional[str] = Field(None, description="错误信息")
```

---

## 🔧 使用方法

### 基本用法

```python
from models import ParseUrlOutput


def main(song_url: str) -> dict:
    try:
        # ... 处理逻辑 ...
        
        # 创建 Pydantic 模型实例
        output = ParseUrlOutput(
            song_id="2758218600",
            success=True,
            error=None
        )
        
        # 转换为字典返回
        return output.model_dump()
    
    except Exception as e:
        # 错误情况
        output = ParseUrlOutput(
            song_id=None,
            success=False,
            error=str(e)
        )
        return output.model_dump()
```

### 所有返回路径都使用模型

```python
def main(condition: bool) -> dict:
    if condition:
        output = ParseUrlOutput(
            song_id="123",
            success=True,
            error=None
        )
        return output.model_dump()
    else:
        output = ParseUrlOutput(
            song_id=None,
            success=False,
            error="条件不满足"
        )
        return output.model_dump()
```

---

## 📚 所有模型

### 1. ParseUrlOutput

**用途**: URL 解析节点

**字段**:

- `song_id`: Optional[str] - 提取的歌曲 ID
- `success`: bool - 解析是否成功
- `error`: Optional[str] - 错误信息

---

### 2. InitialDataStructuringOutput

**用途**: 初始数据结构化节点

**字段**:

- `metadata`: Optional[Dict[str, Any]] - 结构化的元数据对象
- `success`: bool - 结构化是否成功
- `error`: Optional[str] - 错误信息

---

### 3. FindQQMusicMatchOutput

**用途**: QQ 音乐匹配节点

**字段**:

- `match_id`: str - 匹配的歌曲 MID
- `match_name`: str - 匹配的歌曲名称
- `match_album`: str - 匹配的专辑名称
- `match_found`: bool - 是否找到匹配
- `error`: str - 错误信息

---

### 4. ParseQQMusicResponseOutput

**用途**: QQ 音乐响应解析节点

**字段**:

- `parsed_data`: Dict[str, Any] - 完整解析后的数据
- `track_name`: str - 歌曲名称
- `track_title`: str - 歌曲标题
- `album_id`: int - 专辑 ID
- `album_mid`: str - 专辑 MID
- `album_name`: str - 专辑名称
- `album_pmid`: str - 专辑封面图 ID
- `interval`: int - 歌曲时长（秒）
- `success`: bool - 解析状态
- `error`: str - 错误信息

---

### 5. ParseCoverUrlOutput

**用途**: 封面图 URL 解析节点

**字段**:

- `cover_url`: str - 封面图 URL
- `success`: bool - 解析状态
- `error`: str - 错误信息

---

### 6. DownloadAndEncodeCoversOutput

**用途**: 下载并编码封面图节点

**字段**:

- `netease_cover_base64`: str - 网易云封面图 base64
- `qqmusic_cover_base64`: str - QQ 音乐封面图 base64
- `success`: bool - 下载状态
- `error`: str - 错误信息

---

### 7. ParseGeminiResponseOutput

**用途**: Gemini 响应解析节点

**字段**:

- `is_same`: bool - 封面图是否相同
- `confidence`: float - 置信度 (0.0-1.0)
- `differences`: List[str] - 差异列表
- `notes`: str - 额外说明
- `raw_json`: str - 原始 JSON 字符串
- `success`: bool - 解析状态
- `error`: str - 错误信息

---

### 8. ConsolidateOutput

**用途**: 数据整合与核验节点

**字段**:

- `final_report`: Dict[str, Any] - 完整核验报告
- `success`: bool - 执行状态
- `error`: str - 错误信息

---

## ✅ 优势总结

### 1. 类型安全

```python
# ❌ 没有验证
return {"success": "true"}  # 错误：应该是 bool

# ✅ 有验证
output = ParseUrlOutput(success="true")  # 自动转换为 True
```

### 2. 自文档化

```python
class ParseUrlOutput(BaseModel):
    song_id: Optional[str] = Field(None, description="提取的歌曲 ID")
    success: bool = Field(..., description="解析是否成功")
```

模型本身就是最好的文档！

### 3. 一致性保证

所有返回路径都使用相同的模型，确保输出结构一致：

```python
# 所有分支都返回相同的结构
if condition_a:
    return ParseUrlOutput(...).model_dump()
elif condition_b:
    return ParseUrlOutput(...).model_dump()
else:
    return ParseUrlOutput(...).model_dump()
```

### 4. 易于维护

修改输出结构只需要更新模型定义：

```python
# 添加新字段
class ParseUrlOutput(BaseModel):
    song_id: Optional[str] = Field(None)
    success: bool = Field(...)
    error: Optional[str] = Field(None)
    timestamp: int = Field(default_factory=lambda: int(time.time()))  # 新字段
```

---

## 🔍 验证示例

### 示例 1: 成功情况

```python
output = ParseUrlOutput(
    song_id="2758218600",
    success=True,
    error=None
)

print(output.model_dump())
# 输出: {"song_id": "2758218600", "success": True, "error": None}
```

### 示例 2: 错误情况

```python
output = ParseUrlOutput(
    song_id=None,
    success=False,
    error="URL 中未找到 id 参数"
)

print(output.model_dump())
# 输出: {"song_id": None, "success": False, "error": "URL 中未找到 id 参数"}
```

### 示例 3: 自动类型转换

```python
output = ParseUrlOutput(
    song_id=123,        # int → str
    success="true",     # str → bool
    error=""            # str → None (如果为空)
)

print(output.model_dump())
# 输出: {"song_id": "123", "success": True, "error": ""}
```

### 示例 4: 验证失败

```python
try:
    output = ParseUrlOutput(
        song_id="123",
        # success 是必填字段，但没有提供
        error=None
    )
except ValidationError as e:
    print(e)
    # 输出: Field required [type=missing, input_value=...]
```

---

## 📖 Pydantic 最佳实践

### 1. 使用 Field 定义字段

```python
from pydantic import Field

class MyOutput(BaseModel):
    value: str = Field(..., description="描述", min_length=1, max_length=100)
    count: int = Field(0, ge=0, le=1000)  # 0 <= count <= 1000
    ratio: float = Field(0.0, ge=0.0, le=1.0)  # 0.0 <= ratio <= 1.0
```

### 2. 使用 Optional 表示可选字段

```python
from typing import Optional

class MyOutput(BaseModel):
    required_field: str = Field(...)  # 必填
    optional_field: Optional[str] = Field(None)  # 可选
```

### 3. 使用 default_factory 创建可变默认值

```python
from typing import List

class MyOutput(BaseModel):
    # ❌ 错误：不要使用可变对象作为默认值
    items: List[str] = []
    
    # ✅ 正确：使用 default_factory
    items: List[str] = Field(default_factory=list)
```

### 4. 使用 model_dump() 转换为字典

```python
output = MyOutput(value="test")
return output.model_dump()  # Pydantic v2
# 或
return output.dict()  # Pydantic v1 (已废弃)
```

---

## 🧪 测试

所有测试仍然通过，因为 `model_dump()` 返回的是标准字典：

```bash
poetry run pytest tests/dify_workflow/ -v
```

**结果**: ✅ 42/42 测试通过

---

## 📚 参考资源

- **[Pydantic 官方文档](https://docs.pydantic.dev/)**
- **[Pydantic V2 迁移指南](https://docs.pydantic.dev/latest/migration/)**
- **[Field 参数说明](https://docs.pydantic.dev/latest/concepts/fields/)**

---

**更新时间**: 2025-10-27  
**维护者**: [documentation-agent]  
**状态**: ✅ Pydantic 验证已集成

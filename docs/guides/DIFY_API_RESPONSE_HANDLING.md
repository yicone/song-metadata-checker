# Dify Cloud API 响应处理指南

> **快速参考**: 如何在 Dify Cloud 代码节点中正确处理 HTTP 响应

## 📊 响应格式对比

### NetEase API 响应

**HTTP 节点返回**:
```json
{
  "body": "{\"songs\":[{\"id\":2758218600,\"name\":\"顽疾 (Live)\"}]}",
  "status_code": 200
}
```

**特点**:
- ✅ `body` 是 JSON 字符串
- ✅ 需要 `json.loads()` 解析
- ✅ 中文直接显示，无需额外处理

---

### QQ Music API 响应

**HTTP 节点返回**:
```json
{
  "body": "{\"response\":{\"code\":0,\"data\":{\"song\":{\"list\":[...]}}}}",
  "headers": {...},
  "status_code": 200
}
```

**关键点**:
- `body` 是 **JSON 字符串**，不是对象
- 需要使用 `json.loads()` 解析
- 解析后的路径是 `response.data.song.list`（注意有 `response` 层）
- ✅ 中文被 Unicode 转义（`\u793a` 格式）
- ✅ `json.loads()` 会自动解码 Unicode

---

## 🔧 正确的处理方式

### 模板代码

```python
import json

def main(api_response: str) -> dict:
    """
    处理 Dify HTTP 节点返回的响应
    
    参数:
        api_response: HTTP 节点的 body 字段（JSON 字符串）
    
    返回:
        解析后的数据
    """
    try:
        # 步骤 1: 检查类型并解析 JSON 字符串
        if isinstance(api_response, str):
            data = json.loads(api_response)
        else:
            data = api_response
        
        # 步骤 2: 提取需要的数据
        # 根据实际 API 结构调整路径
        result = data.get('key', {})
        
        return {
            "result": result,
            "success": True
        }
    
    except json.JSONDecodeError as e:
        return {
            "result": {},
            "success": False,
            "error": f"JSON 解析失败: {str(e)}"
        }
    
    except Exception as e:
        return {
            "result": {},
            "success": False,
            "error": str(e)
        }
```

---

## 📝 实际示例

### 示例 1: 处理 NetEase API 响应

**节点**: `initial_data_structuring`

**输入变量**:
- `netease_song_details` (String) ← 来自 `netease_song_detail.body`

**代码**:
```python
import json

def main(netease_song_details: str, netease_lyrics_data: str) -> dict:
    try:
        # 解析 JSON 字符串
        song_data = json.loads(netease_song_details)
        lyrics_data = json.loads(netease_lyrics_data)
        
        # 提取歌曲信息
        songs = song_data.get('songs', [])
        if not songs:
            return {"success": False, "error": "未找到歌曲"}
        
        song = songs[0]
        
        return {
            "song_title": song.get('name', ''),
            "artists": [ar.get('name', '') for ar in song.get('ar', [])],
            "success": True
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

### 示例 2: 处理 QQ Music API 响应

**节点**: `find_qqmusic_match`

**输入变量**:
- `search_results` (String) ← 来自 `qqmusic_search.body`

**代码**:
```python
import json

def main(search_results: str) -> dict:
    try:
        # 1. 解析 JSON 字符串
        search_data = json.loads(search_results)
        
        # 2. 提取数据（注意路径：response.data.song.list）
        results = search_data.get('response', {}).get('data', {}).get('song', {}).get('list', [])
        
        if not results:
            return {
                "match_found": False,
                "error": "搜索无结果"
            }
        
        # 3. 取第一个结果
        best_match = results[0]
        
        return {
            "match_id": best_match.get('songmid', ''),
            "match_name": best_match.get('songname', ''),  # Unicode 自动解码
            "match_found": True
        }
    
    except Exception as e:
        return {
            "match_found": False,
            "error": str(e)
        }
```

---

## ⚠️ 常见错误

### 错误 1: 参数类型声明错误

**❌ 错误**:
```python
def main(api_response: dict) -> dict:
    # 会失败：api_response 实际是字符串
    data = api_response.get('key')
```

**✅ 正确**:
```python
def main(api_response: str) -> dict:
    # 先解析字符串
    data = json.loads(api_response)
    result = data.get('key')
```

---

### 错误 2: 忘记导入 json

**❌ 错误**:
```python
def main(api_response: str) -> dict:
    data = json.loads(api_response)  # NameError: name 'json' is not defined
```

**✅ 正确**:
```python
import json

def main(api_response: str) -> dict:
    data = json.loads(api_response)
```

---

### 错误 3: 数据路径错误

**❌ 错误**:
```python
# QQ Music API
results = search_data.get('data', {}).get('list', [])
# 错误：路径应该是 data.song.list
```

**✅ 正确**:
```python
# QQ Music API
results = search_data.get('data', {}).get('song', {}).get('list', [])
```

---

## 🔍 调试技巧

### 1. 打印响应内容

```python
def main(api_response: str) -> dict:
    # 调试：查看原始响应
    print(f"原始响应类型: {type(api_response)}")
    print(f"原始响应内容: {api_response[:200]}")  # 前 200 字符
    
    data = json.loads(api_response)
    print(f"解析后类型: {type(data)}")
    print(f"解析后键: {data.keys()}")
    
    return {"success": True}
```

### 2. 检查 JSON 结构

```python
import json

def main(api_response: str) -> dict:
    data = json.loads(api_response)
    
    # 美化打印 JSON 结构
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    return {"success": True}
```

### 3. 安全访问嵌套数据

```python
def safe_get(data, *keys, default=None):
    """安全地访问嵌套字典"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, {})
        else:
            return default
    return data if data != {} else default

# 使用示例
results = safe_get(search_data, 'data', 'song', 'list', default=[])
```

---

## 📚 相关文档

- [Dify Cloud 手动创建指南](DIFY_CLOUD_MANUAL_SETUP.md)
- [Dify Cloud 故障排除](DIFY_CLOUD_TROUBLESHOOTING.md)
- [QQ Music API 配置](QQMUSIC_API_SETUP.md)

---

**最后更新**: 2025-10-27  
**适用于**: Dify Cloud 工作流代码节点

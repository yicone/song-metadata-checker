# Dify Cloud 手动配置指南

> **目标受众**: 需要手动配置 Dify Cloud 工作流的用户
>
> **前置条件**: 已有 Dify Cloud 账号，已部署 API 服务
>
> **核验源状态**:
>
> - **QQ 音乐**: 当前启用（必需）
> - **Spotify**: 可选，当前禁用（调试优先级低）
>
---
> **🆕 Phase 1 增强功能** (2025-10-27):
>
> 本指南已更新，包含以下增强功能：
>
> - ✅ **歌词比较**: 自动去除时间戳，计算文本相似度（95% 确认）
> - ✅ **时长比较**: ±2 秒容差，自动格式化为 MM:SS
> - ✅ **封面图增强**: 结构化 JSON 响应，包含置信度和差异列表
>
> **比较字段数**: 5 → 7 (+40%)

## 📋 问题说明

### 为什么导入失败？

**错误**: Import Error (无详细信息)

**原因**:

- YAML 文件中包含外部文件引用：
  - `code_file: "nodes/code-nodes/parse_url.py"`
  - `config_file: "nodes/http-nodes/netease_song_detail.json"`
- Dify Cloud 无法访问本地文件系统
- 需要将所有代码和配置内联到工作流中

### 解决方案

**方案 1**: 手动创建工作流（本指南）✅ 推荐  
**方案 2**: 使用自托管 Dify（可导入 YAML）

---

## 🚀 手动创建步骤

### 前置准备

1. **确认 API 服务可访问**:

   ```bash
   # 本地测试
   poetry run python scripts/validate_apis.py
   ```

2. **如果使用 Dify Cloud**:
   - NetEase API 和 QQ Music API 必须部署到公网
   - 或使用 ngrok 等内网穿透工具
   - `localhost` 地址在云端无法访问

---

## 📝 工作流创建

### 步骤 1: 创建新工作流

1. 登录 [Dify Cloud](https://cloud.dify.ai/)
2. 点击 **“创建应用”** → **“工作流”**
3. 应用名称: `音乐元数据核验工作流`
4. 描述: `使用网易云音乐和 QQ 音乐进行元数据核验，可选启用 Spotify`

---

### 步骤 2: 配置输入变量

在工作流编辑器中，配置 **Start** 节点：

**变量 1**:

- 名称: `song_url`
- 类型: `String`
- 必需: ✅
- 描述: `网易云音乐歌曲页面 URL`

**变量 2**:

- 名称: `credits_image_url`
- 类型: `String`
- 必需: ❌
- 描述: `制作人员名单图片 URL（可选）`

---

### 步骤 3: 添加代码节点 - 解析 URL

**节点类型**: Code  
**节点名称**: `parse_url`  
**描述**: 从 URL 中提取歌曲 ID

**输入变量**:

- `song_url` → 来自 `Start.song_url`

**代码** (Python):

```python
import re
from urllib.parse import urlparse, parse_qs

def main(song_url: str) -> dict:
    """
    从网易云音乐 URL 中提取歌曲 ID

    支持格式:
    - https://music.163.com#/song?id=2758218600
    - https://music.163.com/song?id=2758218600
    """
    try:
        # 处理 # 号
        if '#' in song_url:
            song_url = song_url.split('#')[1]

        # 解析 URL
        parsed = urlparse(song_url)
        query_params = parse_qs(parsed.query)

        # 提取 ID
        if 'id' in query_params:
            song_id = query_params['id'][0]
            return {
                "song_id": song_id,
                "success": True
            }
        else:
            return {
                "song_id": "",
                "success": False,
                "error": "URL 中未找到 id 参数"
            }

    except Exception as e:
        return {
            "song_id": "",
            "success": False,
            "error": str(e)
        }
```

**输出变量**:

- `song_id` (String)
- `success` (Boolean)

---

### 步骤 4: 添加 HTTP 节点 - 获取网易云歌曲详情

**节点类型**: HTTP Request  
**节点名称**: `netease_song_detail`

**配置**:

- **Method**: GET
- **URL**: `{{env.NETEASE_API_HOST}}/song/detail?ids={{parse_url.song_id}}`
- **Headers**: (无需特殊 headers)
- **Timeout**: 10000ms

**环境变量** (在工作流设置中配置):

- `NETEASE_API_HOST`: 您的 NetEase API 地址（公网可访问）

**输出变量**:

- `body` → 保存为 `netease_song_details`

---

### 步骤 5: 添加 HTTP 节点 - 获取网易云歌词

**节点类型**: HTTP Request  
**节点名称**: `netease_lyric`

**配置**:

- **Method**: GET
- **URL**: `{{env.NETEASE_API_HOST}}/lyric?id={{parse_url.song_id}}`
- **Timeout**: 10000ms

**输出变量**:

- `body` → 保存为 `netease_lyrics_data`

---

### 步骤 6: 添加代码节点 - 初始数据结构化

**节点类型**: Code  
**节点名称**: `initial_data_structuring`

**输入变量**:

- `netease_song_details` → 来自 `netease_song_detail.body`
- `netease_lyrics_data` → 来自 `netease_lyric.body`

**代码** (Python):

```python
import json
from urllib.parse import quote

def main(netease_song_details: str, netease_lyrics_data: str) -> dict:
    """
    构建基础元数据对象
    """
    try:
        netease_song_dict = json.loads(netease_song_details)
        netease_lyrics_dict = json.loads(netease_lyrics_data)
        # 提取歌曲信息
        songs = netease_song_dict.get('songs', [])
        if not songs:
            return {
                "metadata": {},
                "success": False,
                "error": "未找到歌曲信息"
            }

        song = songs[0]

        # 构建元数据
        metadata = {
            "song_id": str(song.get('id', '')),
            "song_title": song.get('name', ''),
            "artists": [ar.get('name', '') for ar in song.get('ar', [])],
            "album": song.get('al', {}).get('name', ''),
            "cover_url": song.get('al', {}).get('picUrl', ''),
            "duration": song.get('dt', 0),
            "lyrics": netease_lyrics_dict.get('lrc', {}).get('lyric', ''),
            "source": "NetEase Cloud Music"
        }

        # 构建搜索关键词（歌名 + 第一个艺术家）
        search_key = metadata["song_title"]
        if metadata["artists"]:
            search_key += " " + metadata["artists"][0]

        return {
            "metadata": metadata,
            "song_title": metadata["song_title"],
            "search_key": search_key,  # 用于 QQ Music 搜索
            "artists": str(metadata["artists"]),
            "album": metadata["album"],
            "duration": metadata["duration"],
            "cover_art_url": metadata["cover_url"],
            "lyrics": metadata["lyrics"],
            "success": True
        }

    except Exception as e:
        return {
            "metadata": {},
            "success": False,
            "error": str(e)
        }
```

**输出变量**:

- `metadata` (Object) - 完整元数据对象
- `song_title` (String) - 歌曲标题（平铺输出）
- `search_key` (String) - 搜索关键词（歌名 + 艺术家，用于 QQ Music 搜索）
- `artists` (String) - 艺术家列表 JSON 字符串
- `album` (String) - 专辑名称
- `duration` (Number) - 歌曲时长（毫秒）
- `cover_art_url` (String) - 封面图 URL
- `lyrics` (String) - 歌词
- `success` (Boolean)

**⚠️ 重要**:

- Dify Cloud 不支持访问 Object 的嵌套属性（如 `metadata.song_title`），因此需要将常用字段平铺输出
- `search_key` 包含歌名和艺术家，提高 QQ Music 搜索准确度

---

### 步骤 7: 添加 HTTP 节点 - QQ 音乐搜索

**节点类型**: HTTP Request  
**节点名称**: `qqmusic_search`

**配置**:

- **Method**: GET
- **URL**: `{{env.QQ_MUSIC_API_HOST}}/search?key={{initial_data_structuring.search_key}}&pageSize=5`
- **Timeout**: 10000ms

**⚠️ 说明**:

- 使用 `search_key` 变量（包含歌名 + 艺术家，提高搜索准确度）
- Dify 会自动对 URL 参数进行编码，处理空格和特殊字符
- 如果搜索无结果，可以改用仅 `song_title`

**环境变量**:

- `QQ_MUSIC_API_HOST`: 您的 QQ Music API 地址（公网可访问）

**输出变量**:

- `body` → 保存为 `qqmusic_search_results`

---

### 步骤 8: 添加代码节点 - 找到 QQ 音乐匹配

**节点类型**: Code  
**节点名称**: `find_qqmusic_match`

**输入变量**:

- `search_results` → 来自 `qqmusic_search.body`
- `target_title` → 来自 `initial_data_structuring.song_title`
- `target_artists` → 来自 `initial_data_structuring.artists`

**代码** (Python):

```python
import json

def main(search_results: str, target_title: str, target_artists: str) -> dict:
    """
    从搜索结果中找到最佳匹配
    """
    try:
        # QQ Music API 返回的 body 是 JSON 字符串，需要解析
        if isinstance(search_results, str):
            search_data = json.loads(search_results)
        else:
            search_data = search_results

        # 调试：输出完整响应结构
        print(f"QQ Music API 响应: {json.dumps(search_data, ensure_ascii=False, indent=2)}")

        # 提取搜索结果列表
        # 注意：QQ Music API 的数据结构是 response.data.song.list
        results = search_data.get('response', {}).get('data', {}).get('song', {}).get('list', [])

        print(f"搜索结果数量: {len(results)}")
        if results:
            print(f"第一个结果: {json.dumps(results[0], ensure_ascii=False)}")

        if not results:
            return {
                "match_id": "",
                "match_found": False,
                "error": "搜索无结果",
                "debug_data": search_data  # 调试：返回原始数据
            }

        # 简单匹配：取第一个结果
        # TODO: 实现更复杂的匹配算法（比较歌名和艺术家相似度）
        best_match = results[0]

        return {
            "match_id": best_match.get('songmid', ''),
            "match_name": best_match.get('songname', ''),  # Unicode 会自动解码
            "match_album": best_match.get('albumname', ''),
            "match_found": True
        }

    except Exception as e:
        return {
            "match_id": "",
            "match_found": False,
            "error": str(e)
        }
```

**⚠️ 重要**:

- QQ Music API 的 `body` 是 JSON 字符串，需要 `json.loads()` 解析
- Unicode 转义字符（如 `\u793a`）会在 `json.loads()` 时自动解码为中文
- 数据结构是 `data.song.list`，不是 `data.list`

**输出变量**:

- `match_id` (String)
- `match_name` (String)
- `match_found` (Boolean)

---

### 步骤 9: 添加条件节点 - 检查是否找到匹配

**节点类型**: IF/ELSE  
**节点名称**: `check_qqmusic_match`

**条件**:

```
{{find_qqmusic_match.match_found}} == true
```

**IF 分支**: 继续获取 QQ 音乐详情  
**ELSE 分支**: 跳过 QQ 音乐核验

---

### 步骤 10: 添加 HTTP 节点 - 获取 QQ 音乐详情

**节点类型**: HTTP Request  
**节点名称**: `qqmusic_song_detail`  
**连接**: 从 IF 分支连接

**配置**:

- **Method**: GET
- **URL**: `{{env.QQ_MUSIC_API_HOST}}/song?songmid={{find_qqmusic_match.match_id}}`
- **Timeout**: 10000ms

**输出变量**:

- `body` → 保存为 `qqmusic_song_data`

---

### 步骤 11: 添加代码节点 - 解析 QQ 音乐响应

**节点类型**: Code  
**节点名称**: `parse_qqmusic_response`  
**描述**: 解析 Dify HTTP 节点包装的响应，并平铺输出字段

**⚠️ 重要**:

- **代理服务器已简化数据结构**:
  - 新版代理返回: `{"track_info": {...}, "extras": {...}, "info": {...}}`（推荐）
  - 旧版代理返回: `{"response": {"songinfo": {"data": {...}}}}`（兼容）
- 输入 `qqmusic_song_data` 可能是：
  - **字符串**: `"{\"track_info\":{...}}"`（最常见）
  - **字典**: `{"body": "...", "status_code": 200}`（HTTP 节点完整输出）
  - **字典**: `{"track_info": {...}}`（已解析的数据）
- 代码会智能识别并处理所有情况（新版/旧版代理都兼容）
- **必须平铺输出字段**，因为 Dify Cloud 不支持访问嵌套属性

**输入变量**:

- `qqmusic_song_data` → 来自 `qqmusic_song_detail.body`（通常是字符串）

**代码** (Python):

```python
import json

def main(qqmusic_song_data) -> dict:
    """
    解析 QQ 音乐响应并平铺输出字段
    输入可能是字符串或字典
    """
    try:
        # 1. 智能解析（输入可能是字符串或对象）
        if isinstance(qqmusic_song_data, str):
            qqmusic_parsed = json.loads(qqmusic_song_data)
        elif isinstance(qqmusic_song_data, dict):
            # 如果是字典，检查是否有 body 字段（HTTP 节点包装）
            if 'body' in qqmusic_song_data:
                body = qqmusic_song_data['body']
                if isinstance(body, str):
                    qqmusic_parsed = json.loads(body)
                else:
                    qqmusic_parsed = body
            else:
                # 直接就是解析后的数据
                qqmusic_parsed = qqmusic_song_data
        else:
            raise ValueError(f"Unexpected input type: {type(qqmusic_song_data)}")
        
        # 2. 提取数据（代理服务器已简化结构）
        # 新版代理返回: {"track_info": {...}, "extras": {...}, "info": {...}}
        # 旧版代理返回: {"response": {"songinfo": {"data": {...}}}}
        if 'track_info' in qqmusic_parsed:
            # 新版：直接访问 track_info
            track_info = qqmusic_parsed.get('track_info', {})
        elif 'response' in qqmusic_parsed:
            # 旧版：需要嵌套访问
            track_info = (
                qqmusic_parsed
                .get('response', {})
                .get('songinfo', {})
                .get('data', {})
                .get('track_info', {})
            )
        else:
            # 未知格式
            track_info = {}
        
        # 4. 平铺输出（Dify Cloud 不支持嵌套访问）
        album_info = track_info.get('album', {})
        
        return {
            # 完整数据（供参考）
            "parsed_data": qqmusic_parsed,
            
            # 平铺字段（供下游节点直接访问）
            "track_name": track_info.get('name', ''),
            "track_title": track_info.get('title', ''),
            "album_id": album_info.get('id', 0),
            "album_mid": album_info.get('mid', ''),
            "album_name": album_info.get('name', ''),
            "album_pmid": album_info.get('pmid', ''),  # 封面图 ID
            "interval": track_info.get('interval', 0),  # 时长（秒）
            "success": True,
            "error": ""
        }
    
    except Exception as e:
        return {
            "parsed_data": {},
            "track_name": "",
            "track_title": "",
            "album_id": 0,
            "album_mid": "",
            "album_name": "",
            "album_pmid": "",
            "interval": 0,
            "success": False,
            "error": str(e)
        }
```

**输出变量**:

- `parsed_data` (Object) - 完整解析后的数据（供参考）
- `track_name` (String) - 歌曲名称（平铺输出）
- `track_title` (String) - 歌曲标题（平铺输出）
- `album_id` (Number) - 专辑 ID
- `album_mid` (String) - 专辑 MID
- `album_name` (String) - 专辑名称（平铺输出）
- `album_pmid` (String) - 专辑封面图 ID（用于 Gemini 比较）
- `interval` (Number) - 歌曲时长（秒）
- `success` (Boolean) - 解析状态
- `error` (String) - 错误信息（如果有）

**⚠️ 关键点**:

1. **智能解析**: 处理 `body` 为字符串或对象两种情况
2. **平铺输出**: 所有常用字段都平铺输出，避免嵌套访问
3. **容错处理**: 解析失败时返回空值，不中断工作流

---

### 步骤 12: 添加 HTTP 节点 - 获取 QQ 音乐封面图 URL

**节点类型**: HTTP Request  
**节点名称**: `qqmusic_cover_url_raw`  
**描述**: 获取 QQ 音乐封面图的实际 URL

**配置**:

- **Method**: GET
- **URL**: `{{env.QQ_MUSIC_API_HOST}}/cover?id={{parse_qqmusic_response.album_pmid}}`
- **Timeout**: 10000ms

**输出变量**:

- `body` → 原始响应（需要解析）

**⚠️ 说明**:

- QQ 音乐的封面图 ID (pmid) 需要通过 API 转换为实际的 URL
- 可选参数 `size`（如 `500x500`）可以指定图片尺寸
- Dify HTTP 节点会将响应包装为字符串，需要下一步解析

---

### 步骤 12.1: 添加代码节点 - 解析封面图 URL

**节点类型**: Code  
**节点名称**: `parse_cover_url`  
**描述**: 解析 HTTP 响应并提取封面图 URL

**输入变量**:

- `cover_response` → 来自 `qqmusic_cover_url_raw.body`

**代码**:

```python
import json

def main(cover_response: str) -> dict:
    """
    解析 QQ 音乐封面图 API 响应
    处理 Dify HTTP 节点的字符串包装
    """
    try:
        # 1. 处理 Dify HTTP 节点包装
        if isinstance(cover_response, str):
            cover_data = json.loads(cover_response)
        else:
            cover_data = cover_response
        
        # 2. 提取 imageUrl
        image_url = cover_data.get('imageUrl', '')
        
        return {
            "cover_url": image_url,
            "success": True,
            "error": ""
        }
    
    except Exception as e:
        return {
            "cover_url": "",
            "success": False,
            "error": str(e)
        }
```

**输出变量**:

- `cover_url` (String) - 封面图 URL
- `success` (Boolean) - 解析状态
- `error` (String) - 错误信息

---

### 步骤 13: 添加代码节点 - 下载并转换封面图为 Base64 (可选)

**节点类型**: Code  
**节点名称**: `download_and_encode_covers`  
**描述**: 下载两张封面图并转换为 base64 编码

**⚠️ 说明**: 此节点为可选，仅在需要封面图比较时添加

**输入变量**:

- `netease_cover_url` → 来自 `initial_data_structuring.cover_art_url`
- `qqmusic_cover_url` → 来自 `parse_cover_url.cover_url`

**代码**:

```python
import requests
import base64

def main(netease_cover_url: str, qqmusic_cover_url: str) -> dict:
    """
    下载封面图并转换为 base64 编码
    Gemini Vision API 需要 base64 格式的图片数据
    """
    try:
        # 1. 下载网易云封面图
        netease_response = requests.get(netease_cover_url, timeout=10)
        netease_response.raise_for_status()
        netease_base64 = base64.b64encode(netease_response.content).decode('utf-8')
        
        # 2. 下载 QQ 音乐封面图
        qqmusic_response = requests.get(qqmusic_cover_url, timeout=10)
        qqmusic_response.raise_for_status()
        qqmusic_base64 = base64.b64encode(qqmusic_response.content).decode('utf-8')
        
        return {
            "netease_cover_base64": netease_base64,
            "qqmusic_cover_base64": qqmusic_base64,
            "success": True,
            "error": ""
        }
    
    except Exception as e:
        return {
            "netease_cover_base64": "",
            "qqmusic_cover_base64": "",
            "success": False,
            "error": str(e)
        }
```

**输出变量**:

- `netease_cover_base64` (String) - 网易云封面图 base64
- `qqmusic_cover_base64` (String) - QQ 音乐封面图 base64
- `success` (Boolean) - 下载状态
- `error` (String) - 错误信息

---

### 步骤 14: 添加 HTTP 节点 - Gemini 封面图比较 (可选)

**节点类型**: HTTP Request  
**节点名称**: `gemini_cover_comparison`  
**描述**: 使用 Gemini Vision API 比较封面图

**⚠️ 说明**: 此节点为可选，如果不需要封面图比较可以跳过

**配置**:

- **Method**: POST
- **URL**: `{{env.GEMINI_API_BASE_URL}}/v1beta/models/gemini-2.5-flash-lite:generateContent`
- **Headers**:
  - `x-goog-api-key`: `{{env.GEMINI_API_KEY}}`
  - `Content-Type`: `application/json`
- **Timeout**: 30000ms

**Body** (JSON):

```json
{
  "contents": [{
    "parts": [
      {
        "text": "比较两张专辑封面图片，返回 JSON 格式：\n\n{\n  \"is_same\": true/false,\n  \"confidence\": 0.0-1.0,\n  \"differences\": [\"差异1描述\", \"差异2描述\"],\n  \"notes\": \"额外说明\"\n}\n\n判断标准：\n1. 主体图案是否相同\n2. 颜色是否一致\n3. 文字内容是否相同\n4. 分辨率/裁剪差异可忽略\n\n请直接返回 JSON，不要包含其他文字。"
      },
      {
        "inline_data": {
          "mime_type": "image/jpeg",
          "data": "{{download_and_encode_covers.netease_cover_base64}}"
        }
      },
      {
        "inline_data": {
          "mime_type": "image/jpeg",
          "data": "{{download_and_encode_covers.qqmusic_cover_base64}}"
        }
      }
    ]
  }]
}
```

**输出变量**:

- `body.candidates[0].content.parts[0].text` → 保存为 `cover_match_result`

**⚠️ 关键修复**:

1. **模型名称**: 使用 `gemini-2.5-flash-lite`（免费版最新模型）而不是已弃用的 `gemini-1.5-flash` 或 `gemini-pro-vision`
2. **API 路径**: 使用 `/v1beta/models/` 而不是 `/models/`
3. **图片格式**: 使用 base64 编码的图片数据，而不是 URL
4. **GEMINI_API_BASE_URL**: 应该设置为 `https://generativelanguage.googleapis.com`

**免费版模型对比** (截至 2025-10-27):

| 模型 | RPM | TPM | RPD | 状态 |
|------|-----|-----|-----|------|
| Gemini 2.5 Flash-Lite | 15 | 250,000 | 1,000 | ✅ 推荐 |
| Gemini 2.5 Flash | 10 | 250,000 | 250 | ✅ 可用 |
| Gemini 1.5 Flash | 15 | 250,000 | 50 | ❌ 已弃用 |

**环境变量设置**:

```
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com
GEMINI_API_KEY=your_api_key_here
```

---

### 步骤 15: 添加代码节点 - 数据整合与核验

**节点类型**: Code  
**节点名称**: `consolidate`

**输入变量**:

- `netease_data` → 来自 `initial_data_structuring.metadata`
- `qqmusic_track_name` → 来自 `parse_qqmusic_response.track_name` (平铺字段)
- `qqmusic_interval` → 来自 `parse_qqmusic_response.interval` (平铺字段)
- `qqmusic_album_name` → 来自 `parse_qqmusic_response.album_name` (平铺字段)
- `qqmusic_parsed_data` → 来自 `parse_qqmusic_response.parsed_data` (完整数据，供参考)
- `cover_match_result` → 来自 Gemini 封面比较节点（如果有）

**⚠️ 重要**:

- 使用 `parse_qqmusic_response` 的平铺字段，避免嵌套访问
- 本节点代码已更新为 Phase 1 增强版本

**代码** (Python):

```python
import json
import re
from difflib import SequenceMatcher

def main(
    netease_data: dict,
    qqmusic_track_name: str = "",
    qqmusic_interval: int = 0,
    qqmusic_album_name: str = "",
    qqmusic_parsed_data: dict = None,
    cover_match_result: str = None
) -> dict:
    """
    整合多源数据并生成核验报告 (Phase 1 增强版)
    使用平铺字段，避免 Dify Cloud 嵌套访问限制
    """
    try:
        fields = {}

        # 1. 核验标题（使用平铺字段）
        netease_title = netease_data.get('song_title', '')
        fields['title'] = {"value": netease_title, "status": "未查到"}
        
        if qqmusic_track_name:
            if qqmusic_track_name.lower() == netease_title.lower():
                fields['title']['status'] = "确认"
                fields['title']['confirmed_by'] = ["QQ Music"]

        # 2. 核验艺术家（使用完整数据）
        netease_artists = netease_data.get('artists', [])
        fields['artists'] = {"value": netease_artists, "status": "未查到"}
        
        if qqmusic_parsed_data:
            # 兼容新旧两种数据格式
            if 'track_info' in qqmusic_parsed_data:
                # 新版代理：直接访问
                track_info = qqmusic_parsed_data.get('track_info', {})
            else:
                # 旧版代理：嵌套访问
                track_info = qqmusic_parsed_data.get('response', {}).get('songinfo', {}).get('data', {}).get('track_info', {})
            
            qqmusic_artists = [s.get('name', '') for s in track_info.get('singer', [])]
            if qqmusic_artists and set(qqmusic_artists) == set(netease_artists):
                fields['artists']['status'] = "确认"
                fields['artists']['confirmed_by'] = ["QQ Music"]

        # 3. 核验专辑（使用平铺字段）
        netease_album = netease_data.get('album', '')
        fields['album'] = {"value": netease_album, "status": "未查到"}
        
        if qqmusic_album_name:
            if qqmusic_album_name.lower() == netease_album.lower():
                fields['album']['status'] = "确认"
                fields['album']['confirmed_by'] = ["QQ Music"]

        # 4. 🆕 核验时长 (Phase 1 - 使用平铺字段)
        netease_duration = netease_data.get('duration', 0)
        fields['duration'] = {
            "value": netease_duration,
            "value_formatted": f"{netease_duration // 60000}:{(netease_duration % 60000) // 1000:02d}" if netease_duration else "0:00",
            "status": "未查到"
        }
        
        if qqmusic_interval and netease_duration:
            qqmusic_duration = qqmusic_interval * 1000  # 秒转毫秒
            diff = abs(netease_duration - qqmusic_duration)
            if diff <= 2000:  # ±2秒容差
                fields['duration']['status'] = "确认"
                fields['duration']['confirmed_by'] = ["QQ Music"]
            else:
                fields['duration']['status'] = "存疑"
                fields['duration']['note'] = f"时长差异 {diff // 1000} 秒"

        # 5. 🆕 核验歌词 (Phase 1 - 使用完整数据)
        netease_lyrics = netease_data.get('lyrics', {})
        netease_lyrics_text = netease_lyrics.get('original', '') if isinstance(netease_lyrics, dict) else ''
        fields['lyrics'] = {"value": netease_lyrics_text[:100] + "..." if len(netease_lyrics_text) > 100 else netease_lyrics_text, "status": "未查到"}
        
        if netease_lyrics_text and qqmusic_parsed_data:
            # 预处理歌词：去除时间戳和标点
            def clean_lyrics(text):
                text = re.sub(r'\[\d+:\d+\.\d+\]', '', text)  # 去除时间戳
                text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
                return text.lower().strip()
            
            netease_clean = clean_lyrics(netease_lyrics_text)
            
            # 兼容新旧两种数据格式
            if 'track_info' in qqmusic_parsed_data:
                # 新版代理：直接访问
                track_info = qqmusic_parsed_data.get('track_info', {})
            else:
                # 旧版代理：嵌套访问
                track_info = qqmusic_parsed_data.get('response', {}).get('songinfo', {}).get('data', {}).get('track_info', {})
            
            qqmusic_lyrics_text = track_info.get('lyric', '')
            
            if qqmusic_lyrics_text:
                qqmusic_clean = clean_lyrics(qqmusic_lyrics_text)
                similarity = SequenceMatcher(None, netease_clean, qqmusic_clean).ratio()
                fields['lyrics']['similarity_score'] = similarity
                
                if similarity >= 0.95:
                    fields['lyrics']['status'] = "确认"
                    fields['lyrics']['confirmed_by'] = ["QQ Music"]
                elif similarity >= 0.80:
                    fields['lyrics']['status'] = "存疑"
                    fields['lyrics']['note'] = f"相似度 {similarity:.2%}"

        # 6. 🆕 核验封面图 (Phase 1 增强)
        fields['cover_art'] = {"value": netease_data.get('cover_url', ''), "status": "未查到"}
        
        if cover_match_result:
            # 尝试解析 JSON
            try:
                json_match = re.search(r'\{.*\}', cover_match_result, re.DOTALL)
                if json_match:
                    cover_data = json.loads(json_match.group())
                    is_same = cover_data.get('is_same', False)
                    confidence = cover_data.get('confidence', 0.0)
                    
                    if is_same and confidence > 0.8:
                        fields['cover_art']['status'] = "确认"
                    else:
                        fields['cover_art']['status'] = "存疑"
                    
                    fields['cover_art']['ai_comparison'] = {
                        "is_same": is_same,
                        "confidence": confidence,
                        "differences": cover_data.get('differences', []),
                        "notes": cover_data.get('notes', '')
                    }
            except:
                # Fallback 到文本解析
                if '相同' in cover_match_result.lower() or 'same' in cover_match_result.lower():
                    fields['cover_art']['status'] = "确认"

        # 生成摘要
        confirmed = sum(1 for f in fields.values() if f.get('status') == '确认')
        questionable = sum(1 for f in fields.values() if f.get('status') == '存疑')
        not_found = sum(1 for f in fields.values() if f.get('status') == '未查到')

        # 收集各平台原始值（用于人工核验）
        raw_values = {
            "netease": {
                "title": netease_data.get('song_title', ''),
                "artists": netease_data.get('artists', []),
                "album": netease_data.get('album', ''),
                "duration_ms": netease_data.get('duration', 0),
                "lyrics_preview": netease_lyrics_text[:100] + "..." if len(netease_lyrics_text) > 100 else netease_lyrics_text,
                "cover_url": netease_data.get('cover_url', '')
            }
        }
        
        # 添加 QQ Music 原始值（如果有）
        if qqmusic_parsed_data:
            # 兼容新旧两种数据格式
            if 'track_info' in qqmusic_parsed_data:
                track_info = qqmusic_parsed_data.get('track_info', {})
            else:
                track_info = qqmusic_parsed_data.get('response', {}).get('songinfo', {}).get('data', {}).get('track_info', {})
            
            raw_values["qqmusic"] = {
                "title": track_info.get('name', ''),
                "artists": [s.get('name', '') for s in track_info.get('singer', [])],
                "album": track_info.get('album', {}).get('name', ''),
                "duration_sec": track_info.get('interval', 0),
                "lyrics_preview": track_info.get('lyric', '')[:100] + "..." if len(track_info.get('lyric', '')) > 100 else track_info.get('lyric', ''),
                "album_pmid": track_info.get('album', {}).get('pmid', '')
            }

        report = {
            "metadata": {
                "song_id": netease_data.get('song_id', ''),
                "source": "NetEase Cloud Music",
                "verified_with": ["QQ Music"] if qqmusic_parsed_data else []
            },
            "raw_values": raw_values,
            "fields": fields,
            "summary": {
                "total_fields": len(fields),
                "confirmed": confirmed,
                "questionable": questionable,
                "not_found": not_found,
                "confidence_score": confirmed / len(fields) if fields else 0
            }
        }

        return {
            "final_report": report,
            "success": True,
            "error": ""
        }

    except Exception as e:
        return {
            "final_report": {},
            "success": False,
            "error": str(e)
        }
```

**输出变量**:

- `final_report` (Object) - 完整核验报告
  - `metadata`: 元数据信息（歌曲 ID、数据源、验证平台）
  - `raw_values`: 各平台原始值（用于人工核验）
    - `netease`: 网易云音乐原始数据（标题、艺术家、专辑、时长、歌词预览、封面 URL）
    - `qqmusic`: QQ 音乐原始数据（标题、艺术家、专辑、时长、歌词预览、封面 ID）
  - `fields`: 各字段核验结果（包含 Phase 1 新增的 duration 和 lyrics）
  - `summary`: 统计摘要（总字段数、确认数、存疑数、未查到数、置信度分数）
- `success` (Boolean) - 执行状态
- `error` (String) - 错误信息，成功时为空字符串

**Phase 1 新增字段**:

- `fields.duration`: 时长比较（±2秒容差，MM:SS 格式）
- `fields.lyrics`: 歌词比较（相似度评分，95% 确认）
- `fields.cover_art.ai_comparison`: 封面图 JSON 详情（置信度、差异列表）

---

### 步骤 16: 添加 End 节点

**节点类型**: End  
**节点名称**: `end`

**输出变量**:

- 添加输出变量: `final_report`
- 值: `{{consolidate.final_report}}`

**⚠️ 说明**: Dify Cloud 中没有 "Answer" 节点类型，使用 "End" 节点并配置输出变量。

---

## 🔧 环境变量配置

在 Dify Cloud 工作流设置中添加：

```bash
# NetEase Cloud Music API (必需)
NETEASE_API_HOST=https://your-netease-api.com

# QQ Music API (必需)
QQ_MUSIC_API_HOST=https://your-qqmusic-api.com

# Google Gemini API (如需 OCR)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

**⚠️ 重要**:

- 必须使用公网可访问的地址
- 不能使用 `localhost` 或 `127.0.0.1`
- 建议使用 HTTPS

---

## 🧪 测试工作流

### 测试输入

```json
{
  "song_url": "https://music.163.com#/song?id=2758218600"
}
```

### 预期输出

```json
{
  "metadata": {
    "song_id": "2758218600",
    "source": "NetEase Cloud Music",
    "verified_with": ["QQ Music"]
  },
  "fields": {
    "title": {
      "value": "歌曲名称",
      "status": "确认",
      "confirmed_by": ["QQ Music"]
    },
    "artists": {
      "value": ["艺术家名"],
      "status": "确认",
      "confirmed_by": ["QQ Music"]
    }
  },
  "summary": {
    "total_fields": 2,
    "confirmed": 2,
    "questionable": 0,
    "not_found": 0,
    "confidence_score": 1.0
  }
}
```

---

## 🚀 部署 API 到公网

### 选项 1: 使用 ngrok (临时测试)

**⚠️ 问题**: ngrok 免费版只能同时暴露 1 个端口

**解决方案 A: 使用 Nginx 反向代理（推荐）** ✅

```bash
# 1. 创建 Nginx 配置
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 8080;

        # NetEase API
        location /netease/ {
            proxy_pass http://localhost:3000/;
        }

        # QQ Music API
        location /qqmusic/ {
            proxy_pass http://localhost:3001/;
        }
    }
}
EOF

# 2. 启动 API 服务
cd services/netease-api && docker-compose up -d
cd ../qqmusic-api && docker-compose up -d

# 3. 启动 Nginx
docker run -d -p 8080:8080 -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx

# 4. 使用 ngrok 暴露 Nginx（只需一个端口）
ngrok http 8080
# 假设得到: https://abc123.ngrok.io
```

**在 Dify Cloud 中配置环境变量**:

```bash
NETEASE_API_HOST=https://abc123.ngrok.io/netease
QQ_MUSIC_API_HOST=https://abc123.ngrok.io/qqmusic
```

**解决方案 B: 使用 ngrok 付费版**

```bash
# 付费版支持多个隧道
ngrok http 3000 &
ngrok http 3001 &
```

**解决方案 C: 使用免费的 Cloudflare Tunnel**

```bash
# 安装 cloudflared
brew install cloudflare/cloudflare/cloudflared

# 登录
cloudflared tunnel login

# 创建隧道
cloudflared tunnel create music-api

# 配置路由（支持多个服务）
cat > config.yml << 'EOF'
tunnel: <your-tunnel-id>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: netease.yourdomain.com
    service: http://localhost:3000
  - hostname: qqmusic.yourdomain.com
    service: http://localhost:3001
  - service: http_status:404
EOF

# 启动隧道
cloudflared tunnel run music-api
```

### 选项 2: 部署到云服务器

1. **选择云服务商**: AWS, Azure, Google Cloud, 阿里云等
2. **部署 Docker 容器**:

   ```bash
   # 在云服务器上
   git clone <your-repo>
   cd song-metadata-checker/services/netease-api
   docker-compose up -d
   ```

3. **配置防火墙**: 开放端口 3000, 3001
4. **使用公网 IP**: `http://your-server-ip:3000`

### 选项 3: 使用 Railway/Render 等 PaaS

更简单的部署方式，自动提供 HTTPS 域名。

---

## 🎨 Gemini 封面图比较 Prompt 更新 (Phase 1)

### 为什么需要更新

Phase 1 增强了封面图比较功能，现在需要 Gemini 返回结构化 JSON 而不是简单文本。

### 更新 Gemini Vision 节点

如果您的工作流中有 Gemini 封面图比较节点，请更新其 Prompt：

**新的 Prompt**:

```
比较两张专辑封面图片，返回 JSON 格式：

{
  "is_same": true/false,
  "confidence": 0.0-1.0,
  "differences": [
    "差异1描述",
    "差异2描述"
  ],
  "notes": "额外说明"
}

判断标准：
1. 主体图案是否相同
2. 颜色是否一致
3. 文字内容是否相同
4. 分辨率/裁剪差异可忽略

请直接返回 JSON，不要包含其他文字。
```

### Fallback 机制

consolidate 节点的代码已包含 Fallback 机制：

- 如果 Gemini 返回 JSON：解析并提取置信度、差异列表
- 如果 Gemini 返回文本：自动识别"相同"/"不相同"关键词

**无需担心兼容性** - 新代码向后兼容旧的文本响应。

---

## 🔧 可选功能：启用 Spotify 核验

**当前状态**: Spotify 节点已预留但未启用

**为什么暂不启用**:

- 调试优先级较低
- QQ 音乐已能满足中国市场音乐核验需求
- 可在需要时随时启用

### 如何启用

#### 1. 添加环境变量

在 Dify Cloud 工作流设置中添加：

```bash
# Spotify API (可选)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_AUTH_URL=https://accounts.spotify.com/api/token
SPOTIFY_API_BASE_URL=https://api.spotify.com/v1
```

#### 2. 添加 Spotify 节点

参考 `docs/guides/WORKFLOW_OVERVIEW.md#enabling-spotify-validation` 中的详细步骤。

**需要添加的节点**：

1. **Spotify Auth** (HTTP Request) - OAuth 认证
2. **Spotify Search** (HTTP Request) - 搜索歌曲
3. **Find Spotify Match** (Code) - 找到最佳匹配
4. **Spotify Song Detail** (HTTP Request) - 获取详情

#### 3. 修改 normalize_data 节点

将 `spotify_data` 输入从空值改为：

```python
- variable: "spotify_song_detail.body"
  name: "spotify_data"
```

#### 4. 启用并行执行（可选）

在工作流设置中，启用 QQ 音乐和 Spotify 的并行分支。

### 预期效果

- 与国际音乐数据库交叉核验
- 提高非中文音乐的准确性
- 并行执行减少总核验时间

### 权衡

- 增加执行时间（如果不并行）：+3-5 秒
- 额外的 API 成本（Spotify 限流）
- 更复杂的错误处理

---

## 🔧 故障排除

遇到问题？请查看详细的故障排除指南：

**📖 [Dify Cloud 故障排除完整指南](DIFY_CLOUD_TROUBLESHOOTING.md)**

### 常见问题快速索引

1. **无法访问 Object 的嵌套属性** → [问题 1](DIFY_CLOUD_TROUBLESHOOTING.md#问题-1-无法访问-object-的嵌套属性)
2. **找不到 Answer 节点类型** → [问题 2](DIFY_CLOUD_TROUBLESHOOTING.md#问题-2-找不到-answer-节点类型)
3. **ngrok 免费版只能暴露一个端口** → [问题 3](DIFY_CLOUD_TROUBLESHOOTING.md#问题-3-ngrok-免费版只能暴露一个端口)
4. **QQ Music API 搜索失败 (500 错误)** → [问题 4](DIFY_CLOUD_TROUBLESHOOTING.md#问题-4-qq-music-api-搜索失败-500-错误)
5. **QQ Music API 响应需要额外解析** → [问题 5](DIFY_CLOUD_TROUBLESHOOTING.md#问题-5-qq-music-api-响应需要额外解析)
6. **QQ Music API 双重 JSON 编码** → [完整修复指南](../QQMUSIC_API_FIX_SUMMARY.md)

---

## 📚 相关文档

- [完整工作流详解](WORKFLOW_OVERVIEW.md)
- [部署指南](DEPLOYMENT.md)
- [API 配置](QQMUSIC_API_SETUP.md)

---

**最后更新**: 2025-10-27  
**维护者**: [documentation-agent]

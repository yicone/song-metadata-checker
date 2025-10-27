# Dify Cloud 手动创建工作流指南

> **重要**: 由于 Dify Cloud 无法导入包含外部文件引用的 YAML，需要手动创建工作流。

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

## 📝 工作流创建（简化版）

### 步骤 1: 创建新工作流

1. 登录 [Dify Cloud](https://cloud.dify.ai/)
2. 点击 **"创建应用"** → **"工作流"**
3. 应用名称: `音乐元数据核验工作流 (简化版)`
4. 描述: `使用网易云音乐和 QQ 音乐进行元数据核验`

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
def main(netease_song_details: dict, netease_lyrics_data: dict) -> dict:
    """
    构建基础元数据对象
    """
    try:
        # 提取歌曲信息
        songs = netease_song_details.get('songs', [])
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
            "lyrics": netease_lyrics_data.get('lrc', {}).get('lyric', ''),
            "source": "NetEase Cloud Music"
        }
        
        return {
            "metadata": metadata,
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

- `metadata` (Object)
- `success` (Boolean)

---

### 步骤 7: 添加 HTTP 节点 - QQ 音乐搜索

**节点类型**: HTTP Request  
**节点名称**: `qqmusic_search`

**配置**:

- **Method**: GET
- **URL**: `{{env.QQ_MUSIC_API_HOST}}/search?key={{initial_data_structuring.metadata.song_title}} {{initial_data_structuring.metadata.artists[0]}}&pageSize=5`
- **Timeout**: 10000ms

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
- `target_title` → 来自 `initial_data_structuring.metadata.song_title`
- `target_artists` → 来自 `initial_data_structuring.metadata.artists`

**代码** (Python):

```python
def main(search_results: dict, target_title: str, target_artists: list) -> dict:
    """
    从搜索结果中找到最佳匹配
    """
    try:
        # 提取搜索结果列表
        results = search_results.get('data', {}).get('list', [])
        
        if not results:
            return {
                "match_id": "",
                "match_found": False
            }
        
        # 简单匹配：取第一个结果
        # TODO: 实现更复杂的匹配算法
        best_match = results[0]
        
        return {
            "match_id": best_match.get('songmid', ''),
            "match_found": True
        }
    
    except Exception as e:
        return {
            "match_id": "",
            "match_found": False,
            "error": str(e)
        }
```

**输出变量**:

- `match_id` (String)
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

### 步骤 11: 添加代码节点 - 数据整合与核验

**节点类型**: Code  
**节点名称**: `consolidate`

**输入变量**:

- `netease_data` → 来自 `initial_data_structuring.metadata`
- `qqmusic_data` → 来自 `qqmusic_song_detail.body` (如果有)

**代码** (Python):

```python
def main(netease_data: dict, qqmusic_data: dict = None) -> dict:
    """
    整合多源数据并生成核验报告
    """
    try:
        fields = {}
        
        # 核验标题
        netease_title = netease_data.get('song_title', '')
        fields['title'] = {
            "value": netease_title,
            "status": "未查到",
            "source": "NetEase"
        }
        
        if qqmusic_data:
            qqmusic_title = qqmusic_data.get('data', {}).get('track_info', {}).get('name', '')
            if qqmusic_title and qqmusic_title.lower() == netease_title.lower():
                fields['title']['status'] = "确认"
                fields['title']['confirmed_by'] = ["QQ Music"]
            elif qqmusic_title:
                fields['title']['status'] = "存疑"
                fields['title']['qqmusic_value'] = qqmusic_title
        
        # 核验艺术家
        netease_artists = netease_data.get('artists', [])
        fields['artists'] = {
            "value": netease_artists,
            "status": "未查到",
            "source": "NetEase"
        }
        
        if qqmusic_data:
            qqmusic_artists = [
                s.get('name', '') 
                for s in qqmusic_data.get('data', {}).get('track_info', {}).get('singer', [])
            ]
            if qqmusic_artists and set(qqmusic_artists) == set(netease_artists):
                fields['artists']['status'] = "确认"
                fields['artists']['confirmed_by'] = ["QQ Music"]
            elif qqmusic_artists:
                fields['artists']['status'] = "存疑"
                fields['artists']['qqmusic_value'] = qqmusic_artists
        
        # 生成摘要
        confirmed = sum(1 for f in fields.values() if f.get('status') == '确认')
        questionable = sum(1 for f in fields.values() if f.get('status') == '存疑')
        not_found = sum(1 for f in fields.values() if f.get('status') == '未查到')
        
        report = {
            "metadata": {
                "song_id": netease_data.get('song_id', ''),
                "source": "NetEase Cloud Music",
                "verified_with": ["QQ Music"] if qqmusic_data else []
            },
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
            "success": True
        }
    
    except Exception as e:
        return {
            "final_report": {},
            "success": False,
            "error": str(e)
        }
```

**输出变量**:

- `final_report` (Object)
- `success` (Boolean)

---

### 步骤 12: 添加 Answer 节点

**节点类型**: Answer  
**节点名称**: `end`

**输出内容**:

```
{{consolidate.final_report}}
```

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

```bash
# 启动 NetEase API
cd services/netease-api && docker-compose up -d

# 使用 ngrok 暴露到公网
ngrok http 3000
# 复制 ngrok 提供的 HTTPS URL 到 NETEASE_API_HOST

# 对 QQ Music API 重复相同操作
ngrok http 3001
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

## 📚 相关文档

- [完整工作流详解](WORKFLOW_OVERVIEW.md)
- [部署指南](DEPLOYMENT.md)
- [API 配置](QQMUSIC_API_SETUP.md)

---

**最后更新**: 2025-10-27  
**维护者**: [documentation-agent]

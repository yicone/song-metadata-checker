# Dify Cloud 手动创建工作流 - 问题解决方案

> **快速参考**: 解决 Dify Cloud 手动创建工作流时遇到的常见问题

## 📋 问题清单

### ✅ 问题 1: 无法访问 Object 的嵌套属性

**症状**:

```
在节点输入中无法使用 {{node.output.property}}
例如: {{initial_data_structuring.metadata.song_title}} 不工作
```

**根本原因**: Dify Cloud 的变量系统不支持访问嵌套对象属性

**解决方案**: 在代码节点中平铺输出常用字段

#### 修改前（不工作）

```python
def main(...):
    return {
        "metadata": {
            "song_title": "...",
            "artists": [...]
        }
    }
```

在后续节点中使用: `{{node.metadata.song_title}}` ❌ **失败**

#### 修改后（工作）

```python
def main(...):
    metadata = {
        "song_title": "...",
        "artists": [...]
    }
    
    return {
        "metadata": metadata,           # 完整对象（供参考）
        "song_title": metadata["song_title"],  # 平铺输出
        "artists": str(metadata["artists"]),   # 平铺输出
        "album": metadata["album"]             # 平铺输出
    }
```

在后续节点中使用: `{{node.song_title}}` ✅ **成功**

#### 具体修改位置

**步骤 6: `initial_data_structuring` 节点**

添加输出变量:

- `song_title` (String)
- `artists` (String) - JSON 字符串格式
- `album` (String)

**步骤 7: `qqmusic_search` 节点**

URL 修改:

```
修改前: {{initial_data_structuring.metadata.song_title}}
修改后: {{initial_data_structuring.song_title}}
```

---

### ✅ 问题 2: 找不到 Answer 节点类型

**症状**:

```
在节点类型列表中找不到 "Answer" 节点
```

**根本原因**: Dify Cloud 使用不同的节点命名

**解决方案**: 使用 **End** 节点代替

#### 配置步骤

1. **添加 End 节点**
   - 节点类型: `End`
   - 节点名称: `end`

2. **配置输出变量**
   - 点击 End 节点
   - 添加输出变量: `final_report`
   - 变量值: `{{consolidate.final_report}}`

3. **连接节点**
   - 从 `consolidate` 节点连接到 `end` 节点

---

### ✅ 问题 3: ngrok 免费版只能暴露一个端口

**症状**:

```
需要暴露两个 API 服务:
- NetEase API (端口 3000)
- QQ Music API (端口 3001)

但 ngrok 免费版只能同时运行一个隧道
```

**解决方案**: 使用 Nginx 反向代理合并为一个端口

#### 方案 A: Nginx 反向代理（推荐）✅

**步骤 1: 创建 Nginx 配置**

```bash
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 8080;
        
        # NetEase API - 路径前缀 /netease
        location /netease/ {
            proxy_pass http://host.docker.internal:3000/;
        }
        
        # QQ Music API - 路径前缀 /qqmusic
        location /qqmusic/ {
            proxy_pass http://host.docker.internal:3001/;
        }
    }
}
EOF
```

**步骤 2: 启动服务**

```bash
# 启动 NetEase API
cd services/netease-api
docker-compose up -d

# 启动 QQ Music API
cd ../qqmusic-api
docker-compose up -d

# 启动 Nginx（Mac/Linux）
docker run -d \
  --name nginx-proxy \
  -p 8080:8080 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  --add-host=host.docker.internal:host-gateway \
  nginx

# Windows 用户
docker run -d ^
  --name nginx-proxy ^
  -p 8080:8080 ^
  -v %cd%/nginx.conf:/etc/nginx/nginx.conf:ro ^
  nginx
```

**步骤 3: 测试本地访问**

```bash
# 测试 NetEase API
curl http://localhost:8080/netease/song/detail?ids=2758218600

# 测试 QQ Music API
curl http://localhost:8080/qqmusic/search?key=test
```

**步骤 4: 使用 ngrok 暴露**

```bash
ngrok http 8080
# 输出示例: https://abc123.ngrok.io
```

**步骤 5: 在 Dify Cloud 中配置**

```bash
NETEASE_API_HOST=https://abc123.ngrok.io/netease
QQ_MUSIC_API_HOST=https://abc123.ngrok.io/qqmusic
```

**优势**:

- ✅ 免费
- ✅ 只需一个 ngrok 隧道
- ✅ 易于管理

---

#### 方案 B: Cloudflare Tunnel（免费，更稳定）

**步骤 1: 安装 cloudflared**

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Windows
# 下载: https://github.com/cloudflare/cloudflared/releases
```

**步骤 2: 登录并创建隧道**

```bash
# 登录 Cloudflare（会打开浏览器）
cloudflared tunnel login

# 创建隧道
cloudflared tunnel create music-api
# 记录输出的 Tunnel ID
```

**步骤 3: 配置路由**

```bash
cat > cloudflare-config.yml << 'EOF'
tunnel: <your-tunnel-id>
credentials-file: ~/.cloudflared/<your-tunnel-id>.json

ingress:
  # NetEase API
  - hostname: netease-api.yourdomain.com
    service: http://localhost:3000
  
  # QQ Music API
  - hostname: qqmusic-api.yourdomain.com
    service: http://localhost:3001
  
  # 默认规则（必需）
  - service: http_status:404
EOF
```

**步骤 4: 配置 DNS**

在 Cloudflare 控制台添加 CNAME 记录:

```
netease-api.yourdomain.com -> <tunnel-id>.cfargotunnel.com
qqmusic-api.yourdomain.com -> <tunnel-id>.cfargotunnel.com
```

**步骤 5: 启动隧道**

```bash
cloudflared tunnel --config cloudflare-config.yml run music-api
```

**步骤 6: 在 Dify Cloud 中配置**

```bash
NETEASE_API_HOST=https://netease-api.yourdomain.com
QQ_MUSIC_API_HOST=https://qqmusic-api.yourdomain.com
```

**优势**:

- ✅ 完全免费
- ✅ 更稳定（不会像 ngrok 免费版那样 2 小时断开）
- ✅ 自定义域名
- ✅ 自动 HTTPS

**劣势**:

- ❌ 需要拥有域名
- ❌ 配置稍复杂

---

#### 方案 C: ngrok 付费版

```bash
# 升级到付费版（$8/月起）
# 支持多个隧道同时运行

ngrok http 3000 --subdomain=netease-api &
ngrok http 3001 --subdomain=qqmusic-api &
```

---

## 🎯 推荐方案总结

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| **快速测试（1-2 天）** | Nginx + ngrok 免费版 | 最快，零成本 |
| **短期开发（1-2 周）** | Nginx + ngrok 免费版 | 够用，手动重启可接受 |
| **长期开发（1+ 月）** | Cloudflare Tunnel | 稳定，免费，不断线 |
| **生产环境** | 云服务器部署 | 完全控制，高可用 |

---

## 🔧 完整工作流程示例

### 使用 Nginx + ngrok 的完整步骤

```bash
# 1. 启动 API 服务
cd /Users/tr/Workspace/song-metadata-checker
cd services/netease-api && docker-compose up -d
cd ../qqmusic-api && docker-compose up -d

# 2. 创建并启动 Nginx
cd ../..
cat > nginx.conf << 'EOF'
events { worker_connections 1024; }
http {
    server {
        listen 8080;
        location /netease/ { proxy_pass http://host.docker.internal:3000/; }
        location /qqmusic/ { proxy_pass http://host.docker.internal:3001/; }
    }
}
EOF

docker run -d --name nginx-proxy -p 8080:8080 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  --add-host=host.docker.internal:host-gateway nginx

# 3. 测试
curl http://localhost:8080/netease/song/detail?ids=2758218600
curl http://localhost:8080/qqmusic/search?key=test

# 4. 启动 ngrok
ngrok http 8080
# 复制 HTTPS URL，例如: https://abc123.ngrok.io

# 5. 在 Dify Cloud 配置环境变量
# NETEASE_API_HOST=https://abc123.ngrok.io/netease
# QQ_MUSIC_API_HOST=https://abc123.ngrok.io/qqmusic
```

---

### ✅ 问题 4: QQ Music API 搜索失败 (500 错误)

**症状**:

```
Reached maximum retries for URL .../qqmusic/search?key=顽疾 (Live)&pageSize=5`
QQ Music API 日志: "GET /search?key=顽疾%20(Live)&pageSize=5` HTTP/1.0" 500 -
```

**根本原因**:

1. **URL 中有非法字符**: 反引号 `` ` `` 在 URL 末尾
2. **特殊字符未正确处理**: 空格、括号等特殊字符
3. **搜索关键词不准确**: 仅使用歌名可能匹配不到

**解决方案**:

#### 1. 修改 `initial_data_structuring` 节点

添加 `search_key` 输出变量（歌名 + 艺术家）:

```python
import json

def main(netease_song_details: str, netease_lyrics_data: str) -> dict:
    try:
        netease_song_dict = json.loads(netease_song_details)
        netease_lyrics_dict = json.loads(netease_lyrics_data)
        
        songs = netease_song_dict.get('songs', [])
        if not songs:
            return {"metadata": {}, "success": False, "error": "未找到歌曲信息"}
        
        song = songs[0]
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
            "search_key": search_key,  # ← 新增：用于 QQ Music 搜索
            "artists": str(metadata["artists"]),
            "album": metadata["album"],
            "success": True
        }
    
    except Exception as e:
        return {"metadata": {}, "success": False, "error": str(e)}
```

#### 2. 修改 `qqmusic_search` 节点 URL

**修改前**:

```
{{env.QQ_MUSIC_API_HOST}}/search?key={{initial_data_structuring.song_title}}&pageSize=5
```

**修改后**:

```
{{env.QQ_MUSIC_API_HOST}}/search?key={{initial_data_structuring.search_key}}&pageSize=5
```

**说明**:

- ✅ Dify 会自动对 URL 参数进行编码
- ✅ `search_key` 包含歌名和艺术家，提高搜索准确度
- ✅ 空格会被编码为 `%20`，括号会被正确编码

#### 3. 检查 URL 配置

确保 URL 中**没有多余的反引号或特殊字符**:

```
# ✅ 正确
{{env.QQ_MUSIC_API_HOST}}/search?key={{initial_data_structuring.search_key}}&pageSize=5

# ❌ 错误 - 末尾有反引号
{{env.QQ_MUSIC_API_HOST}}/search?key={{initial_data_structuring.search_key}}&pageSize=5`
```

#### 4. 测试 QQ Music API

在更新节点后，先测试 API 是否正常:

```bash
# 测试 URL 编码
curl "http://localhost:8888/qqmusic/search?key=顽疾%20Live&pageSize=5"

# 或使用 curl 自动编码
curl -G "http://localhost:8888/qqmusic/search" \
  --data-urlencode "key=顽疾 Live" \
  --data-urlencode "pageSize=5"
```

**预期结果**: 返回搜索结果 JSON，状态码 200

---

### ✅ 问题 5: QQ Music API 响应需要额外解析

**症状**:

代码节点报错，无法访问 `search_results.data`

**响应示例**:
```json
{
  "body": "{\"code\":0,\"data\":{\"song\":{\"list\":[...]}}}\n",
  "status_code": 200
}
```

**根本原因**:

**解决方案**:

在 `find_qqmusic_match` 节点中：

```python
import json

def main(search_results: str, target_title: str, target_artists: str) -> dict:
    try:
        # 第一步：解析 JSON 字符串
        if isinstance(search_results, str):
            search_data = json.loads(search_results)
        else:
            search_data = search_results
        
        # 第二步：提取数据（注意路径是 data.song.list）
        results = search_data.get('data', {}).get('song', {}).get('list', [])
        
        if not results:
            return {
                "match_id": "",
                "match_found": False,
                "error": "搜索无结果"
            }
        
        best_match = results[0]
        
        return {
            "match_id": best_match.get('songmid', ''),
            "match_name": best_match.get('songname', ''),  # Unicode 自动解码
            "match_found": True
        }
    
    except Exception as e:
        return {
            "match_id": "",
            "match_found": False,
            "error": str(e)
        }
```

**关键点**:
- ✅ 参数类型改为 `str`（不是 `dict`）
- ✅ 使用 `json.loads()` 解析字符串
- ✅ 数据路径是 `data.song.list`（不是 `data.list`）
- ✅ Unicode 转义字符会自动解码为中文

---

## 📚 相关文档

- [完整手动创建指南](DIFY_CLOUD_MANUAL_SETUP.md)
- [Dify 工作流设置](DIFY_WORKFLOW_SETUP.md)
- [QQ Music API 配置](QQMUSIC_API_SETUP.md)

---

**最后更新**: 2025-10-27  
**维护者**: [documentation-agent]

# Dify Cloud 快速开始指南

> **目标**: 30 分钟内在 Dify Cloud 上运行音乐元数据核验工作流

## 📋 前置条件

- ✅ Dify Cloud 账号（免费）
- ✅ 本地已启动 NetEase API 和 QQ Music API
- ✅ ngrok 账号（免费）

---

## 🚀 快速步骤

### 第 1 步: 设置 API 网关（5 分钟）

使用 Nginx 将两个 API 合并到一个端口：

```bash
# 1. 创建 Nginx 配置
cd /Users/tr/Workspace/song-metadata-checker
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

# 2. 启动 Nginx
docker run -d --name nginx-proxy -p 8080:8080 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  --add-host=host.docker.internal:host-gateway nginx

# 3. 测试
curl http://localhost:8080/netease/song/detail?ids=2758218600
```

### 第 2 步: 暴露到公网（2 分钟）

```bash
# 启动 ngrok
ngrok http 8080

# 复制 HTTPS URL（例如: https://abc123.ngrok.io）
```

### 第 3 步: 在 Dify Cloud 创建工作流（20 分钟）

#### 3.1 创建应用

1. 登录 [Dify Cloud](https://cloud.dify.ai/)
2. 创建新应用 → 选择 "工作流"
3. 应用名称: `音乐元数据核验`

#### 3.2 配置环境变量

在工作流设置中添加：

```
NETEASE_API_HOST=https://abc123.ngrok.io/netease
QQ_MUSIC_API_HOST=https://abc123.ngrok.io/qqmusic
```

**⚠️ 注意**: 替换 `abc123.ngrok.io` 为你的实际 ngrok URL

#### 3.3 创建节点

按照 [完整手动创建指南](../../dify-workflow/BUILD_GUIDE.md) 创建以下节点：

**简化版流程**（推荐首次使用）:

1. **Start** - 输入 `song_url`
2. **parse_url** (Code) - 提取歌曲 ID
3. **netease_song_detail** (HTTP) - 获取歌曲详情
4. **initial_data_structuring** (Code) - 结构化数据
5. **qqmusic_search** (HTTP) - QQ 音乐搜索
6. **consolidate** (Code) - 整合结果
7. **End** - 输出结果

**预计时间**: 15-20 分钟

### 第 4 步: 测试工作流（3 分钟）

测试输入:

```json
{
  "song_url": "https://music.163.com#/song?id=2758218600"
}
```

点击 "运行" 查看结果。

---

## ⚠️ 常见问题

### 问题 1: 无法访问 `metadata.song_title`

**解决**: 使用平铺输出变量

```python
# ✅ 正确
return {
    "song_title": "...",  # 平铺输出
    "metadata": {...}
}

# 后续节点使用: {{node.song_title}}
```

详见: [问题解决方案](DIFY_CLOUD_TROUBLESHOOTING.md#问题-1-无法访问-object-的嵌套属性)

### 问题 2: 找不到 Answer 节点

**解决**: 使用 End 节点

详见: [问题解决方案](DIFY_CLOUD_TROUBLESHOOTING.md#问题-2-找不到-answer-节点类型)

### 问题 3: API 请求失败

**检查清单**:

- ✅ ngrok 隧道是否在运行
- ✅ 环境变量 URL 是否正确
- ✅ 本地 API 服务是否启动

---

## 📚 下一步

- **完整功能**: 参考 [完整手动创建指南](../../dify-workflow/BUILD_GUIDE.md) 添加 OCR 等功能
- **问题排查**: 查看 [故障排除指南](DIFY_CLOUD_TROUBLESHOOTING.md)
- **生产部署**: 考虑 [云服务器部署](DEPLOYMENT.md)

---

## 💡 提示

**ngrok 免费版限制**:

- 每 2 小时断开一次
- 每次重启 URL 会变化
- 需要更新 Dify Cloud 环境变量

**长期使用建议**:

- 使用 Cloudflare Tunnel（免费，稳定）
- 或部署到云服务器

---

**最后更新**: 2025-10-27  
**预计完成时间**: 30 分钟

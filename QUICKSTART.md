# 快速开始指南

5 分钟快速部署和测试音乐元数据核验系统。

## 步骤 1: 准备 API 密钥

获取以下 API 密钥：

- **Gemini API**: https://aistudio.google.com/
- **Spotify API**: https://developer.spotify.com/dashboard

## 步骤 2: 配置环境

```bash
# 克隆项目
cd song-metadata-checker

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
nano .env
```

## 步骤 3: 启动服务

```bash
# 启动网易云音乐 API 服务
cd services/netease-api
docker-compose up -d
cd ../..

# 安装 Python 依赖
pip install -r requirements.txt
```

## 步骤 4: 测试 API

```bash
# 验证所有 API 连通性
python scripts/validate_apis.py
```

预期输出：
```
✅ 网易云音乐 API 连接成功
✅ Spotify API 测试成功
✅ Gemini API 测试成功
🎉 所有 API 测试通过！
```

## 步骤 5: 导入 Dify 工作流

### 使用 Dify Cloud

1. 访问 https://cloud.dify.ai/
2. 创建新的 Workflow 应用
3. 导入 `dify-workflow/music-metadata-checker.yml`
4. 在设置中配置环境变量

### 使用自托管 Dify

```bash
# 克隆 Dify
git clone https://github.com/langgenius/dify.git
cd dify/docker

# 启动服务
docker-compose up -d

# 访问 http://localhost/install 完成初始化
```

## 步骤 6: 测试工作流

在 Dify 界面测试：

**输入：**
- `song_url`: `https://music.163.com#/song?id=2758218600`

**或使用命令行：**

```bash
python scripts/test_workflow.py --url "https://music.163.com#/song?id=2758218600"
```

## 成功！

你现在可以：

1. 在 Dify 界面运行工作流
2. 通过 API 调用工作流
3. 自定义工作流节点
4. 集成到你的应用中

## 下一步

- 阅读完整 [README.md](README.md)
- 查看 [部署指南](DEPLOYMENT.md)
- 了解[技术方案](docs/音乐网站歌曲信息核验流程.md)

## 常见问题

**Q: 网易云 API 无法访问？**

A: 确保 Docker 服务运行：
```bash
docker ps | grep netease
```

**Q: Spotify 认证失败？**

A: 检查 Client ID 和 Secret 是否正确，确认应用状态正常。

**Q: Gemini API 超时？**

A: 检查网络连接和 API 密钥有效性。

## 获取帮助

遇到问题？查看 [故障排除](DEPLOYMENT.md#故障排除) 或提交 Issue。

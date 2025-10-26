# Dify 工作流配置

本目录包含音乐元数据核验工作流的 Dify 配置文件。

## 文件结构

- `music-metadata-checker.yml` - 主工作流定义文件
- `nodes/code-nodes/` - 代码节点 Python 脚本
- `nodes/http-nodes/` - HTTP 请求节点配置

## 导入工作流

1. 登录 Dify 平台
2. 创建新的 Workflow 应用
3. 导入 `music-metadata-checker.yml` 文件
4. 配置环境变量
5. 测试工作流

## 环境变量配置

在 Dify 工作流设置中配置以下环境变量：

- `GEMINI_API_KEY`
- `GEMINI_API_BASE_URL`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_AUTH_URL`
- `SPOTIFY_API_BASE_URL`
- `NETEASE_API_HOST`

## 节点说明

详见主 README.md 文件。

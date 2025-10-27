# QQ Music API 快速开始

## ✅ 完整容器化方案已创建

我已经为您创建了完整的容器化配置，但 Rain120 API 需要一些额外的设置。

## 📁 创建的文件

1. **docker-compose-with-upstream.yml** - 完整的 Docker Compose 配置
2. **setup-upstream.sh** - 自动克隆 Rain120 API 的脚本 ✅ 已执行
3. **CONTAINER_SETUP.md** - 完整的容器化设置文档
4. **.gitignore** - 忽略 volumes 目录

## 🎯 当前状态

- ✅ Rain120 API 已克隆到 `./volumes/qq-music-api/`
- ✅ Docker Compose 配置已创建
- ⚠️ npm 依赖安装需要调整

## 🚀 推荐的快速方案

由于 Rain120 API 在容器内安装依赖遇到问题，推荐以下方案：

### 方案 1: 本地运行 Rain120 API（最简单）⭐

```bash
# 1. 进入克隆的目录
cd volumes/qq-music-api

# 2. 安装依赖
npm install

# 3. 启动服务
npm start
```

然后使用简化的 Docker Compose（仅代理层）：

```bash
# 返回 qqmusic-api 目录
cd ../..

# 启动代理（连接到本地 3300 端口）
docker-compose up -d
```

### 方案 2: 修复容器内的 npm install

需要在容器内手动安装依赖：

```bash
# 停止当前容器
docker-compose -f docker-compose-with-upstream.yml down

# 手动安装依赖
cd volumes/qq-music-api
npm install
cd ../..

# 重新启动（跳过 npm install）
docker-compose -f docker-compose-with-upstream.yml up -d
```

### 方案 3: 暂时使用 Mock 数据

如果只是测试 Dify 工作流逻辑：

```bash
# 使用默认的 server.py（返回 mock 数据）
docker-compose up -d
```

在 Dify 工作流中标记结果为"未核验"。

## 📚 完整文档

查看 [CONTAINER_SETUP.md](CONTAINER_SETUP.md) 了解：
- 完整的架构说明
- 详细的故障排除
- 管理命令
- 测试步骤

## 🎯 我的建议

**对于您的情况**，推荐使用**方案 1**（本地运行 Rain120 API）：

1. **简单快速** - 直接 `npm start` 即可
2. **易于调试** - 可以直接查看日志
3. **无容器问题** - 避免 Docker 内的 npm 问题

然后通过 Nginx 代理统一访问：

```bash
# Nginx 配置已经设置好
# 只需确保 Rain120 API 在 localhost:3300 运行
# 通过 http://localhost:8888/qqmusic/ 访问
```

---

**创建时间**: 2025-10-27  
**状态**: Rain120 API 已克隆，推荐本地运行

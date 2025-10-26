# NeteaseCloudMusicApi 服务

## 简介

本服务使用社区维护的 [NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi) 项目，提供网易云音乐的非官方 API 接口。

## 快速启动

```bash
docker-compose up -d
```

服务将在 `http://localhost:3000` 启动。

## 健康检查

```bash
curl http://localhost:3000
```

## 主要接口

### 获取歌曲详情

```bash
GET /song/detail?ids=2758218600
```

### 获取歌词

```bash
GET /lyric?id=2758218600
```

## 停止服务

```bash
docker-compose down
```

## 注意事项

- 这是一个非官方 API，可能随时失效
- 建议在生产环境中实现错误处理和降级策略
- 定期检查项目更新以获取最新功能和修复

## 参考文档

- [NeteaseCloudMusicApi GitHub](https://github.com/Binaryify/NeteaseCloudMusicApi)
- [API 文档](https://neteasecloudmusicapi.js.org/)

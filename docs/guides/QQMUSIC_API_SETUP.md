# QQ Music API Setup Guide

> **⚠️ 文档已过时 / DEPRECATED**  
> 本文档已被更完整的容器化部署指南取代。  
> 请参考最新文档：[services/qqmusic-api/CONTAINER_SETUP.md](../../services/qqmusic-api/CONTAINER_SETUP.md)
>
> **为什么弃用**：
>
> - 本文档描述的是手动部署方式，不包含代理层配置
> - 端点路径和端口配置可能已过时
> - 新的容器化方案提供更好的隔离和管理
>
> **迁移指南**：使用 `./services/qqmusic-api/setup-upstream.sh` 一键部署完整方案

---

Complete guide for configuring QQ Music API integration.

> **Note**: This guide is based on the community-maintained QQ Music API project.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Alternative Solutions](#alternative-solutions)

---

## Overview

QQ Music API is required as a primary validation source for the metadata verification system. This guide covers setup using the community-maintained API project.

**Why QQ Music?**

- Large music catalog in Chinese market
- Independent validation source
- Community-maintained API available

**Status**: Required for verification workflow

---

## Prerequisites

- Node.js 14+ and npm
- Git
- Docker (optional, for containerized deployment)
- Network access to QQ Music services

---

## Installation Methods

### Method 1: Using Rain120/qq-music-api (Recommended)

1. **Clone Repository**:

```bash
cd ..  # Go to parent directory
git clone https://github.com/Rain120/qq-music-api.git
cd qq-music-api
```

2. **Install Dependencies**:

```bash
npm install
```

3. **Start Service**:

```bash
npm start
```

Service will run on `http://localhost:3300` by default.

4. **Verify**:

```bash
curl http://localhost:3300
# Should return API information
```

### Method 2: Docker Deployment

1. **Create Dockerfile** (if not provided):

```dockerfile
FROM node:14-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3300

CMD ["npm", "start"]
```

2. **Build and Run**:

```bash
docker build -t qqmusic-api .
docker run -d -p 3300:3300 --name qqmusic-api qqmusic-api
```

### Method 3: Using Proxy Server

If direct API access is unavailable, use the provided proxy server:

```bash
cd services/qqmusic-api
python server-proxy.py
```

**Note**: This is a fallback solution and may have limitations.

---

## Configuration

### Update Environment Variables

Edit `.env` in the main project:

```env
# QQ Music API Configuration
QQ_MUSIC_API_HOST=http://localhost:3300
```

### Custom Port Configuration

If using a different port:

1. **Update API Service**:

```bash
# For Rain120/qq-music-api
PORT=3301 npm start
```

2. **Update .env**:

```env
QQ_MUSIC_API_HOST=http://localhost:3301
```

### Network Configuration

For remote deployment:

```env
QQ_MUSIC_API_HOST=http://your-server-ip:3300
```

**Security Note**: Ensure proper firewall rules and access controls.

---

## Testing

### Test API Connectivity

```bash
# From main project directory
poetry run python scripts/validate_apis.py
```

Expected output:

```
Testing QQ Music API...
✅ QQ Music API: Connected
```

### Test Search Functionality

```bash
curl "http://localhost:3300/search?key=周杰伦"
```

Expected response:

```json
{
  "result": 100,
  "data": {
    "list": [
      {
        "songmid": "...",
        "songname": "...",
        "singer": [...]
      }
    ]
  }
}
```

### Test Song Details

```bash
curl "http://localhost:3300/song?songmid=<songmid>"
```

---

## Troubleshooting

### Issue: API Service Won't Start

**Symptom**: `npm start` fails or exits immediately

**Solutions**:

1. **Check Node.js version**:

```bash
node --version  # Should be 14+
```

2. **Clear npm cache**:

```bash
npm cache clean --force
rm -rf node_modules
npm install
```

3. **Check port availability**:

```bash
lsof -i :3300  # Check if port is in use
```

### Issue: Search Returns Empty Results

**Symptom**: API responds but returns no results

**Solutions**:

1. **Verify query encoding**:

```bash
# Use URL encoding for Chinese characters
curl "http://localhost:3300/search?key=%E5%91%A8%E6%9D%B0%E4%BC%A6"
```

2. **Check API rate limiting**: Wait a few seconds and retry

3. **Verify network connectivity**: Ensure API can reach QQ Music servers

### Issue: Connection Timeout

**Symptom**: Requests to API timeout

**Solutions**:

1. **Increase timeout in workflow**: Adjust HTTP node timeout settings

2. **Check firewall**: Ensure no blocking of outbound connections

3. **Use proxy**: If direct access is blocked, configure HTTP proxy

### Issue: Invalid Response Format

**Symptom**: API returns unexpected data structure

**Solutions**:

1. **Check API version**: Ensure using compatible version

2. **Update parsing logic**: Adjust code nodes to match current API format

3. **Report issue**: If API changed, report to community project

---

## Alternative Solutions

### Option 1: Mock Service (Development Only)

For testing without real API:

```bash
cd services/qqmusic-api
docker-compose up -d  # Starts mock service
```

**Note**: Returns sample data only, not suitable for production.

### Option 2: Different API Project

Alternative community projects:

- [jsososo/QQMusicApi](https://github.com/jsososo/QQMusicApi)
- Other community-maintained APIs

**Note**: May require code adjustments in workflow.

### Option 3: Direct API Calls

For advanced users, implement direct calls to QQ Music web API:

**Risks**:

- No official API documentation
- Frequent changes to endpoints
- Rate limiting and blocking
- Legal considerations

**Not recommended** for production use.

---

## API Endpoints Reference

### Search

```
GET /search?key={query}&pageSize={size}&page={page}
```

**Parameters**:

- `key`: Search query (URL encoded)
- `pageSize`: Results per page (default: 10)
- `page`: Page number (default: 1)

### Song Details

```
GET /song?songmid={songmid}
```

**Parameters**:

- `songmid`: Song ID from search results

### Lyrics

```
GET /lyric?songmid={songmid}
```

**Parameters**:

- `songmid`: Song ID

---

## Best Practices

1. **Implement Caching**: Cache search results to reduce API calls

2. **Rate Limiting**: Implement request throttling to avoid blocking

3. **Error Handling**: Gracefully handle API failures

4. **Monitoring**: Set up health checks for API availability

5. **Fallback**: Have backup validation sources (e.g., Spotify)

---

## Security Considerations

1. **API Key Management**: If API requires keys, store securely

2. **Access Control**: Restrict API access to authorized services only

3. **HTTPS**: Use HTTPS for production deployments

4. **Logging**: Log API usage but avoid sensitive data

---

## Related Documentation

- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions
- [Functional Specification](../FUNCTIONAL_SPEC.md) - System features
- [Workflow Overview](WORKFLOW_OVERVIEW.md) - Technical architecture

---

## Support

For QQ Music API specific issues:

1. Check [Rain120/qq-music-api Issues](https://github.com/Rain120/qq-music-api/issues)
2. Review community discussions
3. Report bugs to the API project maintainers

For integration issues:

1. Check [Fixes Index](../FIXES_INDEX.md)
2. Review [Troubleshooting](#troubleshooting) section
3. Create issue in main project repository

---

**Last Updated**: 2025-10-26  
**Maintained By**: [documentation-agent]  
**Review Frequency**: Monthly

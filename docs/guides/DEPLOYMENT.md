# Deployment Guide

Complete deployment instructions for the Music Metadata Verification System.

> **Authority**: This is the authoritative guide for deployment procedures.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Deployment Steps](#deployment-steps)
- [Service Configuration](#service-configuration)
- [Dify Setup](#dify-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

---

## Prerequisites

### System Requirements

- Docker and Docker Compose
- Python 3.8+
- Stable internet connection
- Minimum 2GB RAM
- 10GB available disk space

### API Keys Required

Before deployment, obtain the following API keys:

1. **Google Gemini API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Note: Free tier available with rate limits

2. **Spotify API Credentials** (Optional)
   - Visit [Spotify for Developers](https://developer.spotify.com/dashboard)
   - Create an application
   - Obtain Client ID and Client Secret

3. **Dify Platform Access**
   - Option A: Self-hosted - See [Dify Deployment Docs](https://docs.dify.ai/)
   - Option B: Cloud service - Register at [Dify Cloud](https://dify.ai/)

---

## Deployment Steps

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd song-metadata-checker
```

### Step 2: Configure Environment

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` file with your API keys:

```env
# Google Gemini API (Required)
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# Spotify API (Optional)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_AUTH_URL=https://accounts.spotify.com/api/token
SPOTIFY_API_BASE_URL=https://api.spotify.com/v1

# NeteaseCloudMusicApi (Required)
NETEASE_API_HOST=http://localhost:3000

# QQ Music API (Required)
QQ_MUSIC_API_HOST=http://localhost:3300
```

### Step 3: Deploy NetEase Cloud Music API

```bash
cd services/netease-api
docker-compose up -d
cd ../..
```

Verify service is running:

```bash
curl http://localhost:3000
# Should return API information
```

### Step 4: Deploy QQ Music API

Follow the [QQ Music API Setup Guide](QQMUSIC_API_SETUP.md) for detailed instructions.

Quick start:

```bash
cd services/qqmusic-api
docker-compose up -d
cd ../..
```

### Step 5: Install Python Dependencies

Using Poetry (recommended):

```bash
poetry install
```

Or using pip:

```bash
pip install -r requirements.txt
```

### Step 6: Validate API Connections

```bash
poetry run python scripts/validate_apis.py
```

Expected output:

```
✅ NetEase Cloud Music API: Connected
✅ QQ Music API: Connected
✅ Gemini API: Connected
⏭️ Spotify API: Skipped (optional)
🎉 All required APIs are operational!
```

---

## Service Configuration

### NetEase Cloud Music API

**Default Port**: 3000  
**Configuration**: `services/netease-api/docker-compose.yml`

**Custom Port**:

```yaml
ports:
  - "3001:3000"  # Change 3001 to your preferred port
```

Update `.env`:

```env
NETEASE_API_HOST=http://localhost:3001
```

### QQ Music API

**Default Port**: 3300  
**Configuration**: See [QQ Music API Setup Guide](QQMUSIC_API_SETUP.md)

---

## Dify Setup

### Option A: Self-Hosted Dify

1. **Clone Dify Repository**:

```bash
git clone https://github.com/langgenius/dify.git
cd dify/docker
```

2. **Start Services**:

```bash
docker-compose up -d
```

3. **Initialize**:

Visit `http://localhost/install` and complete setup.

### Option B: Dify Cloud

1. Visit [Dify Cloud](https://cloud.dify.ai/)
2. Sign up for an account
3. Create a new workspace

### Import Workflow

1. Log in to Dify platform
2. Click "Create Application" → "Workflow"
3. Select "Import DSL"
4. Upload `dify-workflow/music-metadata-checker.yml`
5. Configure environment variables in workflow settings

### Configure Workflow Variables

Configure environment variables in Dify workflow settings.

[📖 See complete Dify variable configuration →](DIFY_WORKFLOW_SETUP.md#配置环境变量)

---

## Verification

### Test Workflow

In Dify interface, test with:

**Input**:

- `song_url`: `https://music.163.com#/song?id=2758218600`
- `credits_image_url`: (optional) URL to credits image

Click "Run" and verify output.

### Command Line Test

```bash
poetry run python scripts/test_workflow.py \
  --url "https://music.163.com#/song?id=2758218600"
```

### Expected Output

```json
{
  "metadata": {
    "song_id": "2758218600",
    "source": "NetEase Cloud Music"
  },
  "fields": {
    "title": {
      "value": "歌曲名称",
      "status": "确认",
      "confirmed_by": ["QQ Music"]
    }
  },
  "summary": {
    "total_fields": 10,
    "confirmed": 7,
    "questionable": 2,
    "not_found": 1,
    "confidence_score": 0.7
  }
}
```

---

## Troubleshooting

### NetEase API Not Accessible

**Symptom**: `curl http://localhost:3000` fails

**Solutions**:

```bash
# Check container status
docker ps | grep netease

# View logs
docker logs netease-music-api

# Restart service
cd services/netease-api
docker-compose restart
```

### Spotify Authentication Failed

**Symptom**: `❌ Spotify OAuth failed: 401`

**Solutions**:

1. Verify Client ID and Secret are correct
2. Check Spotify app status (not suspended)
3. Ensure Base64 encoding is correct
4. Try regenerating credentials

### Gemini API Timeout

**Symptom**: `❌ Gemini API failed: timeout`

**Solutions**:

1. Check network connectivity to Google services
2. Verify API key is valid and active
3. Check API quota limits
4. Increase timeout in HTTP node configuration

### Dify Workflow Import Failed

**Symptom**: YAML import error

**Solutions**:

1. Verify Dify version compatibility (recommend 0.8.0+)
2. Check YAML syntax validity
3. Try manual node creation if import fails
4. Ensure all required node types are available

### QQ Music API Issues

See [QQ Music API Setup Guide](QQMUSIC_API_SETUP.md) for detailed troubleshooting.

---

## Production Considerations

### Performance Optimization

1. **Enable Caching**:

```bash
# Start Redis
docker run -d -p 6379:6379 redis:alpine

# Update .env
REDIS_HOST=localhost
REDIS_PORT=6379
```

2. **Parallel Processing**:

Implement async API calls in code nodes for better performance.

3. **Rate Limiting**:

Implement request queuing to avoid API throttling.

### Monitoring

1. **Configure Logging**:

```env
LOG_LEVEL=INFO
LOG_FILE=logs/workflow.log
```

2. **API Health Checks**:

```bash
# Add to crontab
*/5 * * * * /path/to/python /path/to/scripts/validate_apis.py >> /var/log/api-health.log 2>&1
```

3. **Alerting**:

Set up notifications for API failures (e.g., DingTalk, Slack).

### Security

1. **Never commit `.env` to version control**
2. **Use environment variables or secrets management**
3. **Rotate API keys regularly**
4. **Restrict API access with IP whitelisting**
5. **Enable HTTPS for all communications**

### Scaling

1. **Load Balancing**: Distribute requests across multiple instances
2. **Multiple API Instances**: Deploy multiple NetEase/QQ Music API containers
3. **Circuit Breaker**: Implement circuit breaker pattern for API failures
4. **Monitoring & Alerting**: Set up comprehensive monitoring

### Backup & Recovery

```bash
# Backup environment variables
cp .env .env.backup.$(date +%Y%m%d)

# Export Dify workflow
# Use Dify interface to export DSL file regularly
```

---

## Update & Maintenance

### Update NetEase API

```bash
cd services/netease-api
docker-compose pull
docker-compose up -d
```

### Update Workflow

1. Modify `dify-workflow/music-metadata-checker.yml`
2. Re-import in Dify interface
3. Test updated workflow thoroughly

### Regular Maintenance

- **Weekly**: Check API health, review logs
- **Monthly**: Update dependencies, review performance
- **Quarterly**: Security audit, capacity planning

---

## Next Steps

- Read [Functional Specification](../FUNCTIONAL_SPEC.md) for feature details
- Review [Workflow Overview](WORKFLOW_OVERVIEW.md) for technical architecture
- Check [Roadmap](../ROADMAP.md) for future plans

---

## Support

For issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [Fixes Index](../FIXES_INDEX.md)
3. Search existing [Issues](https://github.com/your-repo/issues)
4. Create new issue with detailed logs

---

**Last Updated**: 2025-10-26  
**Maintained By**: [documentation-agent]  
**Review Frequency**: Monthly

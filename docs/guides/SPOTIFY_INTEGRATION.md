# Spotify 集成指南

> **Authority**: This is the authoritative guide for Spotify integration.  
> **Status**: Optional feature - Currently disabled by default  
> **Audience**: Developers who want to enable Spotify validation

---

## 📋 Table of Contents

- [Overview](#overview)
- [Why Spotify?](#why-spotify)
- [Prerequisites](#prerequisites)
- [Integration Steps](#integration-steps)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Overview

Spotify integration provides an additional music metadata validation source, particularly useful for:

- **International music** - Better coverage for non-Chinese artists
- **Cross-platform verification** - Additional data point for confidence scoring
- **Metadata enrichment** - Access to Spotify's comprehensive music database

### Current Status

- **Default**: ⚠️ Disabled (not included in bundle)
- **Architecture**: ✅ Supported (workflow designed for easy enablement)
- **Priority**: 🟡 Medium (QQ Music provides primary validation for Chinese market)

---

## Why Spotify?

### Advantages

1. **Global Coverage** ✅
   - Extensive international music catalog
   - Strong metadata quality
   - Regular updates

2. **API Quality** ✅
   - Well-documented REST API
   - Reliable performance
   - Good rate limits (free tier available)

3. **Metadata Richness** ✅
   - Detailed artist information
   - Album data
   - Audio features

### Trade-offs

1. **Additional Complexity** ⚠️
   - OAuth authentication required
   - More API calls
   - Extra error handling

2. **Performance Impact** ⚠️
   - +3-5 seconds execution time (if sequential)
   - Can be mitigated with parallel execution

3. **Cost Considerations** ⚠️
   - API rate limits
   - Potential quota costs

---

## Prerequisites

### 1. Spotify Developer Account

1. Visit [Spotify for Developers](https://developer.spotify.com/dashboard)
2. Log in or create account
3. Create a new application
4. Note your **Client ID** and **Client Secret**

### 2. API Credentials

You will need:

- `SPOTIFY_CLIENT_ID` - Your application's client ID
- `SPOTIFY_CLIENT_SECRET` - Your application's client secret
- `SPOTIFY_AUTH_URL` - OAuth token endpoint (default: `https://accounts.spotify.com/api/token`)
- `SPOTIFY_API_BASE_URL` - API base URL (default: `https://api.spotify.com/v1`)

---

## Integration Steps

### Step 1: Update Environment Variables

Add to your Dify workflow environment:

```bash
# Spotify API (Optional)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_AUTH_URL=https://accounts.spotify.com/api/token
SPOTIFY_API_BASE_URL=https://api.spotify.com/v1
```

**Where to add**:

- Dify Cloud: Workflow Settings → Environment Variables
- Self-hosted: `.env` file or environment configuration

---

### Step 2: Add Spotify Nodes to Workflow

You need to add 4 nodes to `music-metadata-checker.yml`:

#### 2.1 Spotify Auth Node (HTTP Request)

```yaml
- id: 'spotify_auth'
  type: 'http-request'
  title: 'Spotify OAuth Authentication'
  config:
    method: 'POST'
    url: '{{SPOTIFY_AUTH_URL}}'
    headers:
      Content-Type: 'application/x-www-form-urlencoded'
    body:
      grant_type: 'client_credentials'
      client_id: '{{SPOTIFY_CLIENT_ID}}'
      client_secret: '{{SPOTIFY_CLIENT_SECRET}}'
  dependencies: ['initial_data_structuring']
```

#### 2.2 Spotify Search Node (HTTP Request)

```yaml
- id: 'spotify_search'
  type: 'http-request'
  title: 'Spotify Search'
  config:
    method: 'GET'
    url: '{{SPOTIFY_API_BASE_URL}}/search'
    headers:
      Authorization: 'Bearer {{spotify_auth.access_token}}'
    params:
      q: '{{initial_data_structuring.metadata.song_title}} {{initial_data_structuring.metadata.artists[0]}}'
      type: 'track'
      limit: '10'
  dependencies: ['spotify_auth']
```

#### 2.3 Find Spotify Match Node (Code)

```yaml
- id: 'find_spotify_match'
  type: 'code'
  title: 'Find Spotify Match'
  config:
    code_language: 'python3'
    code_file: 'nodes/code-nodes/find_spotify_match.py'
    inputs:
      - variable: 'spotify_search.tracks.items'
        name: 'search_results'
      - variable: 'initial_data_structuring.metadata.song_title'
        name: 'target_title'
      - variable: 'initial_data_structuring.metadata.artists'
        name: 'target_artists'
  dependencies: ['spotify_search']
```

#### 2.4 Spotify Track Detail Node (HTTP Request)

```yaml
- id: 'spotify_track_detail'
  type: 'http-request'
  title: 'Get Spotify Track Details'
  config:
    method: 'GET'
    url: '{{SPOTIFY_API_BASE_URL}}/tracks/{{find_spotify_match.match_id}}'
    headers:
      Authorization: 'Bearer {{spotify_auth.access_token}}'
  dependencies: ['find_spotify_match']
  condition:
    type: 'if'
    expression: '{{find_spotify_match.match_found}} == true'
```

---

### Step 3: Update Consolidate Node

Modify the `consolidate` node to accept Spotify data:

```yaml
- id: 'consolidate'
  type: 'code'
  title: '数据整合与核验'
  config:
    inputs:
      - variable: 'initial_data_structuring.metadata'
        name: 'netease_data'
      - variable: 'qqmusic_song_detail.qqmusic_song_data'
        name: 'qqmusic_data'
      - variable: 'spotify_track_detail.body'  # ← Add this
        name: 'spotify_data'
```

---

### Step 4: Create find_spotify_match.py

Create `dify-workflow/nodes/code-nodes/find_spotify_match.py`:

```python
from typing import TypedDict, Optional, List
from difflib import SequenceMatcher

class FindSpotifyMatchOutput(TypedDict):
    """Spotify 匹配输出"""
    match_id: Optional[str]
    match_name: str
    match_artist: str
    match_found: bool
    success: bool
    error: str

def similarity(a: str, b: str) -> float:
    """计算字符串相似度"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def main(search_results: list, target_title: str, target_artists: List[str]) -> FindSpotifyMatchOutput:
    """
    从 Spotify 搜索结果中找到最佳匹配
    """
    try:
        if not search_results:
            return {
                "match_id": None,
                "match_name": "",
                "match_artist": "",
                "match_found": False,
                "success": True,
                "error": "No search results"
            }
        
        best_match = None
        best_score = 0.0
        
        target_artist = target_artists[0] if target_artists else ""
        
        for track in search_results:
            track_name = track.get('name', '')
            track_artists = track.get('artists', [])
            track_artist = track_artists[0].get('name', '') if track_artists else ''
            
            # 计算相似度
            title_score = similarity(track_name, target_title)
            artist_score = similarity(track_artist, target_artist)
            combined_score = (title_score + artist_score) / 2
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = track
        
        # 阈值：70% 相似度
        if best_score >= 0.7 and best_match:
            return {
                "match_id": best_match.get('id'),
                "match_name": best_match.get('name', ''),
                "match_artist": best_match.get('artists', [{}])[0].get('name', ''),
                "match_found": True,
                "success": True,
                "error": ""
            }
        else:
            return {
                "match_id": None,
                "match_name": "",
                "match_artist": "",
                "match_found": False,
                "success": True,
                "error": f"No match found (best score: {best_score:.2f})"
            }
    
    except Exception as e:
        return {
            "match_id": None,
            "match_name": "",
            "match_artist": "",
            "match_found": False,
            "success": False,
            "error": str(e)
        }
```

---

### Step 5: Rebuild Bundle

After making changes:

```bash
poetry run python scripts/build_dify_bundle.py
```

---

## Configuration

### Parallel Execution (Optional)

To reduce execution time, enable parallel execution for QQ Music and Spotify branches:

1. Both branches depend on `initial_data_structuring`
2. `consolidate` waits for both to complete
3. Total time = max(qqmusic_time, spotify_time) instead of sum

**Workflow structure**:

```
initial_data_structuring
    ├─→ qqmusic_search → ... → qqmusic_song_detail ─┐
    │                                                ├─→ consolidate
    └─→ spotify_auth → ... → spotify_track_detail ──┘
```

---

## Testing

### Test Input

```json
{
  "song_url": "https://music.163.com#/song?id=2758218600"
}
```

### Expected Behavior

1. **Spotify Auth** succeeds and returns access token
2. **Spotify Search** finds matching tracks
3. **Find Match** identifies best match (if similarity >= 70%)
4. **Track Detail** fetches full metadata
5. **Consolidate** includes Spotify data in verification

### Verification

Check consolidate output includes:

```json
{
  "metadata": {
    "verified_with": ["QQ Music", "Spotify"]
  },
  "fields": {
    "title": {
      "confirmed_by": ["QQ Music", "Spotify"]
    }
  }
}
```

---

## Troubleshooting

### Authentication Fails

**Symptom**: `spotify_auth` returns 401 or 403

**Solutions**:

1. Verify `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are correct
2. Check credentials haven't expired
3. Ensure application is not rate-limited

### No Matches Found

**Symptom**: `find_spotify_match.match_found` is always false

**Solutions**:

1. Lower similarity threshold (currently 0.7)
2. Check search query format
3. Verify artist name matching logic

### Rate Limiting

**Symptom**: 429 Too Many Requests

**Solutions**:

1. Implement retry logic with exponential backoff
2. Cache authentication tokens (valid for 1 hour)
3. Consider upgrading Spotify API tier

---

## Performance Impact

### Sequential Execution

- **Before**: ~8-10 seconds (NetEase + QQ Music)
- **After**: ~13-15 seconds (+ Spotify)
- **Impact**: +50% execution time

### Parallel Execution

- **Before**: ~8-10 seconds
- **After**: ~10-12 seconds (max of both branches)
- **Impact**: +20% execution time

---

## Related Documentation

- [Deployment Guide](DEPLOYMENT.md) - Environment setup
- [Workflow Overview](WORKFLOW_OVERVIEW.md) - Architecture details
- [Build Guide](../../dify-workflow/BUILD_GUIDE.md) - Bundle creation

---

**Last Updated**: 2025-10-27  
**Maintained By**: [documentation-agent]  
**Status**: Optional feature - Ready for enablement

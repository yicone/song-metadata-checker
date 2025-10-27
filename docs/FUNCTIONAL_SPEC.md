# Functional Specification

> **Authority**: This is the authoritative documentation for all system features and capabilities.

## 📋 Table of Contents

- [Overview](#overview)
- [Core Features](#core-features)
- [Workflow Stages](#workflow-stages)
- [Data Models](#data-models)
- [API Integrations](#api-integrations)
- [Status Determination Logic](#status-determination-logic)
- [Configuration](#configuration)
- [Limitations](#limitations)

---

## Overview

The Music Metadata Verification System is an automated workflow built on the Dify platform that extracts, validates, and cross-references music metadata from multiple sources.

**Primary Goal**: Verify the accuracy of music metadata from NetEase Cloud Music by cross-referencing with QQ Music, Spotify, and AI-powered analysis.

**Key Principle**: Multi-source cross-validation ensures data accuracy and identifies inconsistencies.

---

## Core Features

### 1. Automated Data Extraction

**Description**: Automatically extracts comprehensive metadata from NetEase Cloud Music.

**Extracted Fields**:

- Song title
- Artist(s)
- Album name
- Release date
- Duration
- Album cover URL
- Lyrics (if available)
- Production credits (via OCR)

**Input**: NetEase Cloud Music song URL  
**Output**: Structured JSON metadata

**Example**:

```json
{
  "song_id": "2758218600",
  "title": "歌曲名称",
  "artists": ["艺术家1", "艺术家2"],
  "album": "专辑名称",
  "release_date": "2024-01-01",
  "duration": 240000,
  "cover_url": "https://...",
  "lyrics": "歌词内容..."
}
```

---

### 2. OCR Production Credits Extraction

**Description**: Uses Google Gemini 2.5 Flash to extract production credits from images.

**Capabilities**:

- Multi-language text recognition
- Structured data extraction
- Role identification (Producer, Composer, Lyricist, etc.)

**Input**: Image URL containing production credits  
**Output**: Structured credits data

**Example**:

```json
{
  "credits": {
    "producer": ["制作人A"],
    "composer": ["作曲者B"],
    "lyricist": ["作词者C"],
    "arranger": ["编曲者D"]
  }
}
```

**Status**: ✅ Implemented

---

### 3. Multi-Source Cross-Validation

**Description**: Validates metadata by comparing with multiple independent sources.

**Validation Sources**:

1. **QQ Music** (Required) - Primary validation source
2. **Spotify** (Optional) - Additional validation source

**Validation Process**:

1. Search for matching song on each platform
2. Extract metadata from each source
3. Compare fields across sources
4. Determine status for each field

**Status**: ✅ Implemented

---

### 4. Album Cover Comparison

**Description**: Uses AI vision to compare album covers from different sources.

**Capabilities**:

- Visual similarity detection
- Identifies identical, similar, or different covers
- Handles different image sizes and formats

**Input**: Multiple album cover URLs  
**Output**: Similarity assessment

**Example**:

```json
{
  "cover_comparison": {
    "netease_vs_qqmusic": "identical",
    "netease_vs_spotify": "similar",
    "confidence": 0.95
  }
}
```

**Status**: ✅ Implemented

---

### 5. Intelligent Status Determination

**Description**: Automatically assigns status to each metadata field based on validation results.

**Status Types**:

- **确认 (Confirmed)**: Data matches across sources
- **存疑 (Questionable)**: Data exists but has discrepancies
- **未查到 (Not Found)**: Data not found in validation sources

**Logic**: See [Status Determination Logic](#status-determination-logic)

**Status**: ✅ Implemented

---

## Workflow Stages

### Stage 1: Data Extraction

**Nodes**:

1. **Start** - Accepts `song_url` input
2. **Parse URL** - Extracts `song_id` from URL
3. **Fetch Song Details** - Calls NetEase API `/song/detail`
4. **Fetch Lyrics** - Calls NetEase API `/lyric`
5. **Build Initial Data** - Constructs base metadata object

**Duration**: ~2-3 seconds  
**Failure Handling**: Workflow stops if NetEase API fails

---

### Stage 2: OCR Extraction (Optional)

**Nodes**:

1. **Gemini OCR** - Extracts credits from image
2. **Parse OCR Results** - Structures extracted data
3. **Merge Credits** - Adds credits to metadata

**Duration**: ~3-5 seconds  
**Failure Handling**: Continues without credits if OCR fails

---

### Stage 3: Multi-Source Validation

**Nodes**:

1. **Spotify Auth** - OAuth authentication (if enabled)
2. **Spotify Search** - Find matching track
3. **Spotify Details** - Get full metadata
4. **QQ Music Search** - Find matching song
5. **QQ Music Details** - Get full metadata
6. **Cover Comparison** - Compare album covers

**Duration**: ~5-8 seconds  
**Failure Handling**: Continues with available sources

---

### Stage 4: Data Consolidation

**Nodes**:

1. **Normalize Data** - Standardize formats
2. **Compare & Determine Status** - Apply validation logic
3. **Generate Report** - Create final JSON output
4. **Answer** - Return results

**Duration**: ~1-2 seconds  
**Failure Handling**: Returns partial results if available

---

## Data Models

### Input Model

```typescript
interface WorkflowInput {
  song_url: string; // Required: NetEase Cloud Music URL
  credits_image_url?: string; // Optional: Production credits image
}
```

### Output Model

```typescript
interface VerificationReport {
  metadata: {
    song_id: string;
    source: string;
    timestamp: string;
  };
  fields: {
    [fieldName: string]: {
      value: any;
      status: "确认" | "存疑" | "未查到";
      confirmed_by?: string[];
      notes?: string;
    };
  };
  summary: {
    total_fields: number;
    confirmed: number;
    questionable: number;
    not_found: number;
    confidence_score: number;
  };
}
```

---

## API Integrations

### NetEase Cloud Music API

**Base URL**: `http://localhost:3000` (configurable)

**Endpoints**:

- `GET /song/detail?ids={song_id}` - Song details
- `GET /lyric?id={song_id}` - Lyrics

**Status**: ✅ Required

---

### QQ Music API

**Base URL**: `http://localhost:3001` (代理层，推荐)

**Endpoints** (代理层):

- `GET /search?key={query}` - Search songs
- `GET /song?songmid={song_mid}` - Song details

**Architecture**: 使用双层架构（代理层 + Rain120 上游 API）

**详细配置**: 参见 [services/qqmusic-api/README.md](../services/qqmusic-api/README.md)

**Status**: ✅ Required

---

### Spotify API

**Base URL**: `https://api.spotify.com/v1`

**Endpoints**:

- `POST /api/token` - OAuth authentication
- `GET /search?q={query}&type=track` - Search tracks
- `GET /tracks/{id}` - Track details

**Status**: ⏭️ Optional

---

### Google Gemini API

**Base URL**: `https://generativelanguage.googleapis.com/v1beta`

**Endpoints**:

- `POST /models/gemini-2.5-flash:generateContent` - OCR & image comparison

**Status**: ✅ Required

---

## Status Determination Logic

### Confirmed (确认)

**Criteria**:

- Field value matches in NetEase AND at least one validation source
- Exact match or semantically equivalent

**Example**:

```
NetEase: "周杰伦"
QQ Music: "周杰伦"
→ Status: 确认
```

---

### Questionable (存疑)

**Criteria**:

- Field exists but values differ across sources
- Partial matches or conflicting information

**Example**:

```
NetEase: "周杰伦, 方文山"
QQ Music: "周杰伦"
Spotify: "Jay Chou, Vincent Fang"
→ Status: 存疑
```

---

### Not Found (未查到)

**Criteria**:

- Field not found in any validation source
- Search returned no results

**Example**:

```
NetEase: "独立音乐人作品"
QQ Music: Not found
Spotify: Not found
→ Status: 未查到
```

---

## Configuration

### Required Environment Variables

```bash
# NetEase Cloud Music API (Required)
NETEASE_API_HOST=http://localhost:3000

# QQ Music API (Required) - 使用代理层
QQ_MUSIC_API_HOST=http://localhost:3001

# Google Gemini API (Required)
GEMINI_API_KEY=your_api_key
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# Spotify API (Optional)
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### Optional Configuration

```bash
# Workflow Settings
WORKFLOW_TIMEOUT=60000          # Timeout in milliseconds
ENABLE_SPOTIFY=false            # Enable/disable Spotify validation
ENABLE_OCR=true                 # Enable/disable OCR extraction

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/workflow.log
```

---

## Limitations

See [Roadmap & Known Limitations](ROADMAP.md) for detailed information.

**Key Limitations**:

1. Unofficial API dependencies (NetEase, QQ Music)
2. No caching mechanism
3. Limited error recovery
4. Manual Dify configuration required
5. Single language support (primarily Chinese)

---

## Related Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started quickly
- [Deployment Guide](guides/DEPLOYMENT.md) - Detailed deployment
- [Roadmap](ROADMAP.md) - Future plans and limitations
- [Workflow Overview](guides/WORKFLOW_OVERVIEW.md) - Technical details

---

**Last Updated**: 2025-10-26  
**Maintained By**: [documentation-agent]  
**Review Frequency**: Monthly

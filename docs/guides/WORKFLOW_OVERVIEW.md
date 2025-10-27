# Workflow Overview

Technical architecture and workflow details for the Music Metadata Verification System.

> **Authority**: This is the authoritative technical documentation for system architecture.
>
> **📌 Validation Sources**:
>
> - **QQ Music**: Active (required)
> - **Spotify**: Optional, currently disabled (debugging priority: low)
> - Architecture supports enabling Spotify for parallel validation when needed

## 📋 Table of Contents

- [System Architecture](#system-architecture)
- [Workflow Stages](#workflow-stages)
- [Node Details](#node-details)
- [Data Flow](#data-flow)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   User Input    │
│   (Song URL)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Dify Workflow Engine                       │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Data Extract │→ │  OCR Extract │→ │ Multi-Source │ │
│  │    Stage     │  │    Stage     │  │  Validation  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                           │            │
│                                           ▼            │
│                                  ┌──────────────┐     │
│                                  │ Consolidate  │     │
│                                  │   & Report   │     │
│                                  └──────────────┘     │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Verification    │
│    Report       │
│    (JSON)       │
└─────────────────┘
```

### Component Architecture

```
External APIs                Workflow Engine           Data Processing
─────────────               ─────────────────          ───────────────

NetEase API    ────────┐
                       │
QQ Music API   ────────┼──→  HTTP Nodes  ──→  Code Nodes  ──→  Output
(Active)               │
                       │
Spotify API    ────────┤  [Optional, Currently Disabled]
(Disabled)             │
                       │
Gemini API     ────────┘
```

---

## Workflow Stages

### Stage 1: Data Extraction (2-3 seconds)

**Purpose**: Extract base metadata from NetEase Cloud Music

**Nodes**:

1. **Start** - Accept input parameters
2. **Parse URL** - Extract song ID from URL
3. **Fetch Song Details** - Get song metadata
4. **Fetch Lyrics** - Get lyrics data
5. **Build Initial Data** - Construct base object

**Output**: Structured metadata object with NetEase data

**Error Handling**: Workflow stops if NetEase API fails (required data source)

---

### Stage 2: OCR Extraction (3-5 seconds, Optional)

**Purpose**: Extract production credits from images using AI

**Nodes**:

1. **Gemini OCR** - Send image to Gemini API
2. **Parse OCR Results** - Extract structured data
3. **Merge Credits** - Add to metadata object

**Output**: Enhanced metadata with production credits

**Error Handling**: Continues without credits if OCR fails

---

### Stage 3: Multi-Source Validation (2-5 seconds)

**Purpose**: Cross-validate metadata with independent sources

**Active Validation Sources**:

**QQ Music** (Required, Active)

1. **QQ Music Search** - Find matching song using combined search key
2. **Find Best Match** - Select most relevant result from search results
3. **QQ Music Details** - Get full song metadata (conditional on match found)

**Optional Validation Sources** (Currently Disabled):

**Spotify** (Optional, Disabled)

1. **Spotify Auth** - OAuth token acquisition
2. **Spotify Search** - Find matching track
3. **Find Best Match** - Select most relevant result
4. **Spotify Details** - Get full track metadata

**Status**: Spotify nodes are architecturally supported but currently disabled (debugging priority: low)

**When Enabled**: Can run in parallel with QQ Music validation

**Output**: Validation data from active sources (currently QQ Music only)

**Error Handling**: Continues with available sources

---

### Stage 4: Data Consolidation (1-2 seconds)

**Purpose**: Compare data and generate final report

**Nodes**:

1. **Normalize Data** - Standardize formats across sources
2. **Compare & Determine Status** - Apply validation logic
3. **Generate Report** - Create structured JSON output
4. **Answer** - Return final result

**Output**: Complete verification report with status for each field

**Error Handling**: Returns partial results if some validations failed

---

## Node Details

### Code Nodes

#### 1. Parse URL (`parse_url.py`)

**Input**: `song_url` (string)

**Logic**:

```python
# Extract song ID from various URL formats
# Supports: music.163.com#/song?id=xxx
#           music.163.com/song?id=xxx
```

**Output**: `song_id` (string)

**Error**: Returns error if URL format invalid

---

#### 2. Normalize Data (`normalize_data.py`)

**Input**: Raw data from multiple sources

**Logic**:

- Standardize date formats (ISO 8601)
- Normalize artist names (trim, lowercase comparison)
- Convert duration to milliseconds
- Clean text fields (remove extra spaces)

**Output**: Normalized data objects

---

#### 3. Find Match (`find_match.py`)

**Input**: Search results array

**Logic**:

- Calculate similarity scores for each result
- Consider: title match, artist match, album match
- Weight factors: title (40%), artist (40%), album (20%)
- Return highest scoring match

**Output**: Best matching item or null

---

#### 4. Consolidate (`consolidate.py`)

**Input**: Normalized data from all sources

**Logic**:

- Compare each field across sources
- Apply status determination rules
- Calculate confidence score
- Generate summary statistics

**Output**: Final verification report

---

### HTTP Nodes

#### NetEase Cloud Music

**Endpoint**: `/song/detail?ids={song_id}`

**Method**: GET

**Headers**: None required

**Response**: Song metadata including title, artists, album, duration, cover

---

**Endpoint**: `/lyric?id={song_id}`

**Method**: GET

**Response**: Lyrics in multiple formats (original, translated)

---

#### QQ Music

**Endpoint**: `/search?key={query}`

**Method**: GET

**Parameters**:

- `key`: Search query (URL encoded)
- `pageSize`: Results per page (default: 10)

**Response**: Array of matching songs

---

**Endpoint**: `/song?songmid={songmid}`

**Method**: GET

**Response**: Complete song metadata

---

#### Spotify (Optional, Currently Disabled)

> **Status**: Spotify integration is architecturally supported but currently disabled.
> **Reason**: Debugging priority is low; QQ Music provides sufficient validation for current needs.
> **Enable**: See "Enabling Spotify Validation" section below.

**Endpoint**: `/api/token`

**Method**: POST

**Headers**:

- `Authorization`: Basic {base64(client_id:client_secret)}
- `Content-Type`: application/x-www-form-urlencoded

**Body**: `grant_type=client_credentials`

**Response**: Access token

---

**Endpoint**: `/v1/search`

**Method**: GET

**Headers**:

- `Authorization`: Bearer {access_token}

**Parameters**:

- `q`: Search query
- `type`: track
- `limit`: 10

**Response**: Search results

---

**Endpoint**: `/v1/tracks/{id}`

**Method**: GET

**Headers**:

- `Authorization`: Bearer {access_token}

**Response**: Track details

---

#### Google Gemini

**Endpoint**: `/v1beta/models/gemini-2.5-flash:generateContent`

**Method**: POST

**Headers**:

- `Content-Type`: application/json
- `x-goog-api-key`: {api_key}

**Body**: Multimodal content (text + image)

**Response**: Generated text or analysis

---

## Data Flow

### Input Data Model

```typescript
interface WorkflowInput {
  song_url: string; // Required
  credits_image_url?: string; // Optional
}
```

### Intermediate Data Model

```typescript
interface SongMetadata {
  song_id: string;
  title: string;
  artists: string[];
  album: string;
  release_date: string;
  duration: number;
  cover_url: string;
  lyrics?: string;
  credits?: {
    producer?: string[];
    composer?: string[];
    lyricist?: string[];
    arranger?: string[];
  };
}
```

### Output Data Model

```typescript
interface VerificationReport {
  metadata: {
    song_id: string;
    source: string;
    timestamp: string;
    workflow_version: string;
  };
  fields: {
    [fieldName: string]: FieldVerification;
  };
  summary: ReportSummary;
}

interface FieldVerification {
  value: any;
  status: "确认" | "存疑" | "未查到";
  confirmed_by?: string[];
  conflicts?: Conflict[];
  notes?: string;
}

interface ReportSummary {
  total_fields: number;
  confirmed: number;
  questionable: number;
  not_found: number;
  confidence_score: number;
}
```

---

## Error Handling

### Error Categories

#### 1. Network Errors

**Causes**: API timeout, connection refused, DNS failure

**Handling**:

- Retry with exponential backoff (not yet implemented)
- Continue with available sources
- Log error details

**User Impact**: Partial results, lower confidence score

---

#### 2. API Errors

**Causes**: Invalid response, rate limiting, authentication failure

**Handling**:

- Parse error response
- Skip failed source
- Continue workflow

**User Impact**: Missing validation from failed source

---

#### 3. Data Parsing Errors

**Causes**: Unexpected response format, missing fields

**Handling**:

- Use default values
- Log parsing errors
- Continue with partial data

**User Impact**: Some fields may be marked as "未查到"

---

#### 4. Validation Errors

**Causes**: Invalid input URL, missing required parameters

**Handling**:

- Return clear error message
- Stop workflow early
- Provide correction guidance

**User Impact**: Workflow fails with actionable error

---

### Error Recovery Strategy

```
Error Occurs
    │
    ▼
Is it critical? ──Yes──> Stop workflow, return error
    │
    No
    │
    ▼
Log error details
    │
    ▼
Continue with available data
    │
    ▼
Mark affected fields as "未查到"
    │
    ▼
Complete workflow with partial results
```

---

## Performance Considerations

### Execution Time

**Current Configuration** (QQ Music only): 8-12 seconds

**Breakdown**:

- Data Extraction: 2-3s
- OCR (if enabled): 3-5s
- QQ Music Validation: 2-3s
- Consolidation: 1-2s

**With Spotify Enabled** (parallel execution): 10-15 seconds

**Breakdown**:

- Data Extraction: 2-3s
- OCR (if enabled): 3-5s
- Parallel Validation (QQ Music + Spotify): 5-8s
- Consolidation: 1-2s

### Optimization Opportunities

1. **Enable Spotify Validation**: Add Spotify as parallel validation source for international music
2. **Parallel API Calls**: When Spotify is enabled, execute Spotify and QQ Music searches simultaneously
3. **Caching**: Cache search results for frequently queried songs
4. **Lazy Loading**: Skip optional validations if confidence is already high
5. **Request Batching**: Batch multiple song queries if supported by APIs

### Resource Usage

**Memory**: ~50-100MB per workflow execution

**Network**: ~1-2MB data transfer per execution

**CPU**: Minimal (mostly I/O bound)

---

## Enabling Spotify Validation

**Current Status**: Spotify validation is architecturally supported but disabled.

**Why Disabled**: Debugging priority is low; QQ Music provides sufficient validation for Chinese market music.

### Steps to Enable

1. **Add Environment Variables** (in Dify workflow settings):

   ```bash
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_AUTH_URL=https://accounts.spotify.com/api/token
   SPOTIFY_API_BASE_URL=https://api.spotify.com/v1
   ```

2. **Add Spotify Nodes** to workflow:
   - Spotify Auth node (HTTP Request)
   - Spotify Search node (HTTP Request)
   - Find Spotify Match node (Code)
   - Spotify Song Detail node (HTTP Request)

3. **Update normalize_data Node**:
   - Change `spotify_data` input from empty value to `spotify_song_detail.body`

4. **Enable Parallel Execution** (optional):
   - In workflow settings, enable parallel branches for QQ Music and Spotify

5. **Test**:
   - Verify Spotify API credentials
   - Test with international music tracks
   - Validate parallel execution performance

### Expected Benefits

- Cross-validation with international music database
- Better accuracy for non-Chinese music
- Parallel execution reduces total validation time

### Trade-offs

- Increased execution time (if not parallel): +3-5 seconds
- Additional API costs (Spotify rate limits)
- More complex error handling

---

## Related Documentation

- [Functional Specification](../FUNCTIONAL_SPEC.md) - Feature details
- [Deployment Guide](DEPLOYMENT.md) - Setup instructions
- [API Integration](QQMUSIC_API_SETUP.md) - API configuration
- [Dify Cloud Manual Setup](DIFY_CLOUD_MANUAL_SETUP.md) - Cloud deployment guide

---

**Last Updated**: 2025-10-27  
**Maintained By**: [documentation-agent]  
**Review Frequency**: Monthly

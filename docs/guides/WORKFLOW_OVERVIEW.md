# Workflow Overview

Technical architecture and workflow details for the Music Metadata Verification System.

> **Authority**: This is the authoritative technical documentation for system architecture.

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
                       │
Spotify API    ────────┤
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

### Stage 3: Multi-Source Validation (5-8 seconds)

**Purpose**: Cross-validate metadata with independent sources

**Parallel Branches**:

**Branch A: Spotify** (Optional)

1. **Spotify Auth** - OAuth token acquisition
2. **Spotify Search** - Find matching track
3. **Find Best Match** - Select most relevant result
4. **Spotify Details** - Get full track metadata

**Branch B: QQ Music** (Required)

1. **QQ Music Search** - Find matching song
2. **Find Best Match** - Select most relevant result
3. **QQ Music Details** - Get full song metadata

**Branch C: Cover Comparison**

1. **Gemini Vision** - Compare album covers
2. **Parse Comparison** - Extract similarity score

**Output**: Validation data from multiple sources

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

#### Spotify

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

**Typical Execution**: 10-15 seconds

**Breakdown**:

- Data Extraction: 2-3s
- OCR (if enabled): 3-5s
- Validation: 5-8s
- Consolidation: 1-2s

### Optimization Opportunities

1. **Parallel API Calls**: Execute Spotify and QQ Music searches simultaneously
2. **Caching**: Cache search results for frequently queried songs
3. **Lazy Loading**: Skip optional validations if confidence is already high
4. **Request Batching**: Batch multiple song queries if supported by APIs

### Resource Usage

**Memory**: ~50-100MB per workflow execution

**Network**: ~1-2MB data transfer per execution

**CPU**: Minimal (mostly I/O bound)

---

## Related Documentation

- [Functional Specification](../FUNCTIONAL_SPEC.md) - Feature details
- [Deployment Guide](DEPLOYMENT.md) - Setup instructions
- [API Integration](QQMUSIC_API_SETUP.md) - API configuration

---

**Last Updated**: 2025-10-26  
**Maintained By**: [documentation-agent]  
**Review Frequency**: Monthly

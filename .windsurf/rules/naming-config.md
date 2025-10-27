# Naming Conventions - Project Configuration

> **Project**: song-metadata-checker  
> **Last Updated**: 2025-10-27
> **Referenced By**: `docs/NAMING_CONVENTIONS.md`

## Project-Specific File Names

### Services Directory

| Service      | Directory               | Key Files                                           |
| ------------ | ----------------------- | --------------------------------------------------- |
| QQ Music API | `services/qqmusic-api/` | `README.md`, `CONTAINER_SETUP.md`, `QUICK_START.md` |
| NetEase API  | `services/netease-api/` | `README.md`, `docker-compose.yml`                   |

### Documentation Structure

```
docs/
├── README.md                          # Documentation index
├── QUICKSTART.md                      # Getting started
├── FUNCTIONAL_SPEC.md                 # Feature specifications
├── DOCUMENTATION_MANAGEMENT.md        # Documentation guide
├── NAMING_CONVENTIONS.md              # This guide
├── FIXES_INDEX.md                     # Bug fixes index
├── fixes/                             # Detailed fix documentation
│   └── YYYY-MM-DD-description.md
├── guides/                            # How-to guides
│   ├── DEPLOYMENT.md
│   ├── DIFY_CLOUD_MANUAL_SETUP.md
│   └── QQMUSIC_API_SETUP.md
└── archive/                           # Deprecated documentation
    └── *.md (with deprecation warnings)
```

### Code Structure

| Component      | Location   | Naming Pattern                   |
| -------------- | ---------- | -------------------------------- |
| Python modules | `src/`     | `snake_case.py`                  |
| Test files     | `tests/`   | `test_*.py`                      |
| Scripts        | `scripts/` | `snake_case.py`                  |
| Config files   | Root       | `pyproject.toml`, `.env.example` |

## Project-Specific Terminology

| Term                    | Usage                                   | Example                            |
| ----------------------- | --------------------------------------- | ---------------------------------- |
| "QQ Music API"          | Refers to the dual-layer architecture   | "Configure QQ Music API proxy"     |
| "Rain120 API"           | Refers to the upstream API specifically | "Rain120 API runs on port 3200"    |
| "Proxy layer"           | Refers to the custom proxy service      | "Proxy layer exposes port 3001"    |
| "NetEase API"           | Refers to NeteaseCloudMusicApi service  | "NetEase API provides data source" |
| "Metadata verification" | Core feature                            | "Metadata verification workflow"   |

## Abbreviations and Acronyms

| Abbreviation | Full Form                         | Usage                   |
| ------------ | --------------------------------- | ----------------------- |
| API          | Application Programming Interface | Always capitalized      |
| SSOT         | Single Source of Truth            | Documentation principle |
| OCR          | Optical Character Recognition     | Gemini API feature      |
| QQ           | QQ Music                          | Chinese music platform  |

## Version Control

### Branch Naming

- Feature: `feature/description`
- Fix: `fix/description`
- Docs: `docs/description`
- Refactor: `refactor/description`

### Commit Messages

Follow conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## Examples from This Project

### Good Examples

✅ `services/qqmusic-api/CONTAINER_SETUP.md` - Clear, descriptive, follows pattern  
✅ `docs/fixes/2025-01-27-port-documentation-inconsistency.md` - Dated fix doc  
✅ `docs/FIXES_INDEX.md` - Clear index file  
✅ `.windsurf/workflows/doc-review.md` - Workflow in correct location

### Avoid

❌ `qqmusic_setup.md` - Use SCREAMING_SNAKE_CASE for docs  
❌ `fix.md` - Too generic, no date  
❌ `temp-file.md` - Temporary files should not be committed  
❌ `old_README.md` - Move to archive/ with deprecation warning

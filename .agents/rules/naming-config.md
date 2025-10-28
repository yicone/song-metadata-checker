# Naming Conventions - Project Configuration

> **Referenced By**: `docs/NAMING_CONVENTIONS.md`

## Project-Specific File Names

<!-- 
Instructions: Document the naming conventions for your project's key directories and files.
-->

### Services / Modules

| Service      | Directory               | Key Files                                           |
| ------------ | ----------------------- | --------------------------------------------------- |
| QQ Music API | `services/qqmusic-api/` | `README.md`, `CONTAINER_SETUP.md`, `QUICK_START.md` |
| NetEase API  | `services/netease-api/` | `README.md`, `docker-compose.yml`                   |

### Documentation Structure

<!-- This should reflect the structure defined in docs/DOCUMENTATION_MANAGEMENT.md -->

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

<!-- Adapt this table to your project's language and framework -->

| Component      | Location   | Naming Pattern                   |
| -------------- | ---------- | -------------------------------- |
| Python modules | `src/`     | `snake_case.py`                  |
| Test files     | `tests/`   | `test_*.py`                      |
| Scripts        | `scripts/` | `snake_case.py`                  |
| Config files   | Root       | `pyproject.toml`, `.env.example` |

## Project-Specific Terminology

<!-- 
Instructions: Define terms, codenames, or concepts that are unique to your project. 
This helps everyone (especially AI agents) use consistent language.
-->

| Term                    | Usage                                   | Example                            |
| ----------------------- | --------------------------------------- | ---------------------------------- |
| "QQ Music API"          | Refers to the dual-layer architecture   | "Configure QQ Music API proxy"     |
| "Rain120 API"           | Refers to the upstream API specifically | "Rain120 API runs on port 3200"    |
| "Proxy layer"           | Refers to the custom proxy service      | "Proxy layer exposes port 3001"    |
| "NetEase API"           | Refers to NeteaseCloudMusicApi service  | "NetEase API provides data source" |
| "Metadata verification" | Core feature                            | "Metadata verification workflow"   |

## Abbreviations and Acronyms

<!-- Instructions: List common abbreviations to ensure consistency. -->

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

<!-- Instructions: Provide good and bad examples of names from your project to make the rules concrete. -->

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

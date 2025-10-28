# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project setup with Dify workflow integration
- NeteaseCloudMusicApi integration for music metadata extraction
- QQ Music API integration for cross-validation
- Gemini API integration for OCR and image comparison
- Spotify API integration (optional) for additional validation
- Automated metadata verification workflow
- Docker-based service deployment
- API validation scripts
- Comprehensive documentation structure
- Gemini response parsing node (`parse_gemini_response`) for integrating AI cover comparison results
- QQ Music response parsing node (`parse_qqmusic_response`) to handle Dify Cloud HTTP node wrapper
- Cover URL parsing node (`parse_cover_url`) to extract image URLs from API responses
- QQ Music cover image API endpoint (`/cover`) for retrieving album artwork
- Raw values output in consolidate node (`raw_values` field) for manual verification
- Unit tests for all Dify workflow code nodes (42/42 passing)

### Changed

- Upgraded Gemini model from 1.5 Flash (deprecated) to 2.5 Flash-Lite
- Simplified proxy server data structure for cleaner API responses
- Migrated to doc-standards v1.1.0 system with symlinked templates
- Reduced documentation by 33% (72 → 48 files) through cleanup and consolidation

### Deprecated

### Removed

- 24 SUMMARY and CHECK/ANALYSIS documents (violate doc-standards rules)
- 14 feature explanation documents (content integrated into CHANGELOG)

### Fixed

- Gemini Vision API 400 error (incorrect model name and image format)
- Husky + lint-staged pre-commit hook failures (ENOENT and KILLED errors)
- parse_qqmusic_response type error ('str' object has no attribute 'get')
- Port and endpoint documentation inconsistencies across multiple files

### Security

## [0.1.0] - 2025-10-26

### Added

- Initial release
- Core workflow for music metadata verification
- Multi-source cross-validation system
- OCR extraction for production credits
- Album cover comparison using AI
- Status determination (Confirmed/Questionable/Not Found)
- Complete documentation and deployment guides

# Fixes Index

Quick reference for all bug fixes and improvements.

> **📍 For AI Agents**: This is an index file optimized for quick retrieval. Read this first to get summaries, then follow links to detailed documentation in `fixes/` directory if needed.

## Overview

This index provides quick summaries of all fixes and improvements. Each entry links to detailed documentation with root cause analysis, solution details, and testing procedures.

## Recent Fixes

### [Port and Endpoint Documentation Inconsistency](fixes/2025-01-27-port-documentation-inconsistency.md)

**Date**: 2025-01-27  
**Impact**: High  
**Status**: ✅ 已完成（包含预防措施）  
**Summary**: Discovered widespread documentation inconsistencies regarding QQ Music API ports (3200/3300) and endpoints (/search/song vs /getSearchByKey). Multiple documents contain outdated information that conflicts with current implementation, violating SSoT principles.

**Key Issues**:

- 15+ files reference incorrect endpoint paths
- Port numbers (3200 vs 3300) used inconsistently without clarification
- Environment variable recommendations point to wrong service layer
- Archived documents lack deprecation warnings

[Read detailed analysis →](fixes/2025-01-27-port-documentation-inconsistency.md)

---

## How to Use This Index

### For AI Agents

1. **Read this file first** (1 tool call) - Get all fix summaries
2. **Follow links** to detailed docs only if needed (1 more tool call)
3. **Total**: 1-2 tool calls vs 5+ without index

### For Humans

- **Quick scan**: Read summaries here
- **Deep dive**: Click links for full details
- **Search**: Use Ctrl+F to find specific issues

## Adding New Fixes

When implementing a fix:

1. **Create detailed doc**: `docs/fixes/YYYY-MM-DD-<description>.md`
2. **Add entry here** using the template below
3. **Update CHANGELOG.md** if user-facing

### Entry Template

```markdown
### [Fix Title](fixes/YYYY-MM-DD-description.md)

**Date**: YYYY-MM-DD  
**Impact**: High/Medium/Low  
**Status**: ✅ Fixed / 🚧 In Progress / ⏳ Planned  
**Summary**: 1-2 sentence description of the issue and solution

[Read detailed fix →](fixes/YYYY-MM-DD-description.md)
```

## Categories

### Performance Improvements

_No entries yet_

### Bug Fixes

_No entries yet_

### Feature Enhancements

_No entries yet_

### Security Fixes

_No entries yet_

---

## Related Documentation

- [Changelog](../CHANGELOG.md) - Version history
- [Roadmap](ROADMAP.md) - Future plans
- [Naming Conventions](NAMING_CONVENTIONS.md) - Documentation standards

---

**Last Updated**: 2025-10-26  
**Maintained By**: [documentation-agent]  
**Review Frequency**: Weekly

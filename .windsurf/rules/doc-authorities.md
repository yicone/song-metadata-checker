# Authority Documents Mapping

> **Project**: song-metadata-checker  
> **Last Updated**: 2025-01-27  
> **Referenced By**: `docs/DOCUMENTATION_MANAGEMENT.md`

## Technical Details Authority Documents

| Type | Authority Document | Purpose |
|------|-------------------|---------|
| QQ Music API Setup | `services/qqmusic-api/CONTAINER_SETUP.md` | Complete setup guide |
| QQ Music API Overview | `services/qqmusic-api/README.md` | Architecture and quick reference |
| Port Mappings | `services/qqmusic-api/README.md` | Definitive port mapping table |
| Endpoint Mappings | `services/qqmusic-api/README.md` | Proxy vs upstream endpoint table |
| Environment Variables | `docs/FUNCTIONAL_SPEC.md` | Application-level config |
| Deployment Config | `docs/guides/DEPLOYMENT.md` | Deployment-specific config |
| NetEase API Setup | `services/netease-api/README.md` | NetEase Cloud Music API setup |

## Feature Documentation Authority

| Feature Area | Authority Document | Purpose |
|-------------|-------------------|---------|
| Metadata Verification | `docs/FUNCTIONAL_SPEC.md` | Core verification logic |
| API Integration | `docs/FUNCTIONAL_SPEC.md` | External API usage |
| Dify Integration | `docs/guides/DIFY_CLOUD_MANUAL_SETUP.md` | Dify setup and config |

## Process Documentation Authority

| Process | Authority Document | Purpose |
|---------|-------------------|---------|
| Quick Start | `docs/QUICKSTART.md` | Getting started guide |
| Deployment | `docs/guides/DEPLOYMENT.md` | Production deployment |
| Contributing | `CONTRIBUTING.md` | Contribution guidelines (if exists) |
| Fixes & Improvements | `docs/FIXES_INDEX.md` | Bug fixes and improvements |

## Update Protocol

When adding new technical components:

1. Decide which document should be the authority
2. Add entry to this mapping table
3. Update `docs/DOCUMENTATION_MANAGEMENT.md` if needed
4. Ensure other docs link to (not duplicate) the authority

## Verification Commands

```bash
# Check for duplicate technical details
grep -r "port.*3001\|port.*3200\|port.*3300" docs/ services/ --exclude-dir=node_modules

# Check for duplicate endpoint definitions
grep -r "/search\|/song\|getSearchByKey\|getSongInfo" docs/ services/ --exclude-dir=node_modules

# Check for duplicate environment variable definitions
grep -r "QQ_MUSIC_API_HOST\|QQMUSIC_API_BASE\|NETEASE_API_HOST" docs/ services/
```

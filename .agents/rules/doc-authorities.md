# Authority Documents Mapping

> **Referenced By**: `docs/DOCUMENTATION_MANAGEMENT.md`

## Technical Details Authority Documents

<!-- 
Instructions: Fill this table with technical topics and their single source of truth (SSOT).
- Type: The kind of technical information (e.g., 'API Port Mappings', 'Environment Variables').
- Authority Document: The ONE file that authoritatively defines this information.
- Purpose: A brief explanation of what the document covers.
-->

| Type                  | Authority Document                        | Purpose                          |
| --------------------- | ----------------------------------------- | -------------------------------- |
| QQ Music API Setup    | `services/qqmusic-api/CONTAINER_SETUP.md` | Complete setup guide             |
| QQ Music API Overview | `services/qqmusic-api/README.md`          | Architecture and quick reference |
| Port Mappings         | `services/qqmusic-api/README.md`          | Definitive port mapping table    |
| Endpoint Mappings     | `services/qqmusic-api/README.md`          | Proxy vs upstream endpoint table |
| Environment Variables | `docs/FUNCTIONAL_SPEC.md`                 | Application-level config         |
| Deployment Config     | `docs/guides/DEPLOYMENT.md`               | Deployment-specific config       |
| NetEase API Setup     | `services/netease-api/README.md`          | NetEase Cloud Music API setup    |

## Feature Documentation Authority

<!-- 
Instructions: Map major features or business domains to their authority documents.
-->

| Feature Area          | Authority Document                       | Purpose                 |
| --------------------- | ---------------------------------------- | ----------------------- |
| Metadata Verification | `docs/FUNCTIONAL_SPEC.md`                | Core verification logic |
| API Integration       | `docs/FUNCTIONAL_SPEC.md`                | External API usage      |

## Process Documentation Authority

<!-- 
Instructions: Map key development processes to their authority documents.
-->

| Process              | Authority Document          | Purpose                             |
| -------------------- | --------------------------- | ----------------------------------- |
| Quick Start          | `docs/QUICKSTART.md`        | Getting started guide               |
| Deployment           | `docs/guides/DEPLOYMENT.md` | Production deployment               |
| Contributing         | `CONTRIBUTING.md`           | Contribution guidelines (if exists) |
| Fixes & Improvements | `docs/FIXES_INDEX.md`       | Bug fixes and improvements          |

## Update Protocol

When adding new technical components:

1. Decide which document should be the authority
2. Add entry to this mapping table
3. Update `docs/DOCUMENTATION_MANAGEMENT.md` if needed
4. Ensure other docs link to (not duplicate) the authority

## Verification Commands

<!--
Instructions: Add shell commands to help verify that the SSOT rules defined above are being followed.
These commands can be used in a CI/CD pipeline or a local review workflow.

```bash
# Check for duplicate technical details
grep -r "port.*3001\|port.*3200\|port.*3300" docs/ services/ --exclude-dir=node_modules

# Check for duplicate endpoint definitions
grep -r "/search\|/song\|getSearchByKey\|getSongInfo" docs/ services/ --exclude-dir=node_modules

# Check for duplicate environment variable definitions
grep -r "QQ_MUSIC_API_HOST\|QQMUSIC_API_BASE\|NETEASE_API_HOST" docs/ services/
```

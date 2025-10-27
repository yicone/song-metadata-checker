# Documentation Review - Project Configuration

> **Project**: song-metadata-checker  
> **Last Updated**: 2025-10-27
> **Referenced By**: `.windsurf/workflows/doc-review.md`

## Project-Specific Check Commands

### Port Number Consistency

```bash
# Check all port references
grep -r "3001\|3200\|3300\|3000" docs/ services/ --exclude-dir=node_modules --exclude-dir=archive

# Expected usage:
# - 3000: NetEase API
# - 3001: QQ Music API proxy layer (recommended)
# - 3200: Rain120 API (container internal)
# - 3300: Rain120 API (host mapping, debugging only)
```

### API Endpoint Consistency

```bash
# Check QQ Music API endpoints
grep -r "/search\|/song\|getSearchByKey\|getSongInfo" docs/ services/ --exclude-dir=node_modules --exclude-dir=archive

# Expected:
# - Proxy layer: /search, /song
# - Rain120 upstream: /getSearchByKey, /getSongInfo
```

### Environment Variable Consistency

```bash
# Check environment variable definitions
grep -r "QQ_MUSIC_API_HOST\|QQMUSIC_API_BASE\|NETEASE_API_HOST\|GEMINI_API" docs/ services/ --exclude-dir=node_modules

# Expected:
# - QQ_MUSIC_API_HOST=http://localhost:3001 (application layer)
# - QQMUSIC_API_BASE=http://qqmusic-upstream:3200 (proxy layer)
# - NETEASE_API_HOST=http://localhost:3000
```

## Project-Specific Authority Documents

Must match `.windsurf/rules/doc-authorities.md`:

| Type                  | Authority Document                        |
| --------------------- | ----------------------------------------- |
| QQ Music API Setup    | `services/qqmusic-api/CONTAINER_SETUP.md` |
| Port Mappings         | `services/qqmusic-api/README.md`          |
| Environment Variables | `docs/FUNCTIONAL_SPEC.md`                 |
| Deployment            | `docs/guides/DEPLOYMENT.md`               |

## Common Issues in This Project

### Issue: Port 3300 vs 3001 Confusion

**Check**:

```bash
grep -r "QQ_MUSIC_API_HOST.*3300" docs/ services/
```

**Fix**: Should be `http://localhost:3001` (proxy layer)

### Issue: Old Endpoint Paths

**Check**:

```bash
grep -r "/search/song\|/song/detail" docs/ services/ --exclude-dir=archive
```

**Fix**: Update to `/search` (proxy) or `/getSearchByKey` (upstream)

### Issue: Missing Deprecation Warnings

**Check**:

```bash
for file in docs/archive/*.md; do
  if ! head -20 "$file" | grep -q "ARCHIVED\|已归档\|DEPRECATED\|已过时"; then
    echo "⚠️  Missing warning: $file"
  fi
done
```

**Fix**: Add deprecation warning at top of file

## Project-Specific Workflows

### Weekly Review Checklist

- [ ] Check recent commits for API changes: `git log --since="1 week ago" --oneline`
- [ ] Verify port configurations in all docs
- [ ] Check for new services that need documentation
- [ ] Update `docs/FIXES_INDEX.md` if fixes were implemented

### Monthly Audit

- [ ] Run all consistency checks above
- [ ] Verify all internal links work
- [ ] Check for outdated screenshots or examples
- [ ] Review and update authority documents mapping
- [ ] Ensure archived docs have deprecation warnings

### Quarterly Review

- [ ] Full documentation restructure assessment
- [ ] Update `docs/DOCUMENTATION_MANAGEMENT.md`
- [ ] Review and update naming conventions
- [ ] Assess need for new workflows or guides

## Quick Fix Commands

### Update Port References

```bash
# Find all incorrect port references (example)
grep -rl "localhost:3300" docs/ | xargs sed -i '' 's/localhost:3300/localhost:3001/g'
```

### Add Deprecation Warning to Archive

```bash
# Template for archived docs
cat > /tmp/deprecation.txt << 'EOF'
> **⚠️ 文档已归档 / ARCHIVED**
> 本文档已过时，仅供历史参考。
> **请参考最新文档**: [链接到新文档]
>
> **主要问题**: [列出过时的原因]

---

EOF
```

## Integration with CI/CD (Future)

Potential automated checks:

```yaml
# .github/workflows/doc-check.yml (example)
name: Documentation Consistency Check

on: [pull_request]

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check port consistency
        run: |
          # Run project-specific checks
          bash .windsurf/workflows/doc-review.md
```

---
trigger: manual
---

# Agent Configuration

> **Project**: song-metadata-checker  
> **Last Updated**: 2025-10-27
> **Referenced By**: `AGENTS.md`

## Agent Responsibilities

### [tooling-agent]

**Configurations to Maintain**:

- `pyproject.toml` - Python dependencies and tool configs

**Tool-Specific Rules**:

- **Ruff**: Maintain consistency across all Python files
- **MyPy**: Ensure type hints are accurate

**Handoff Checklist**:

- [ ] Run `ruff check .`
- [ ] Run `mypy .`
- [ ] Ensure all tests pass

---

### [documentation-agent]

**Primary Guides**:

- `docs/DOCUMENTATION_MANAGEMENT.md` - Complete documentation guide
- `docs/NAMING_CONVENTIONS.md` - File naming standards
- `.windsurf/workflows/doc-review.md` - Review checklist

**Key Responsibilities**:

1. Maintain SSOT principle across all docs
2. Update `docs/FIXES_INDEX.md` when fixes are implemented
3. Follow hybrid approach (index + detail files)
4. Keep documentation synced with code changes
5. Perform weekly/monthly/quarterly maintenance tasks

**Authority Documents** (See `.windsurf/rules/doc-authorities.md`):

- QQ Music API: `services/qqmusic-api/CONTAINER_SETUP.md`
- Deployment: `docs/guides/DEPLOYMENT.md`
- Functional Spec: `docs/FUNCTIONAL_SPEC.md`

**Workflows**:

- `/doc-review` - Run documentation consistency checks
- **Weekly**: Review recent code changes for doc updates
- **Monthly**: Full documentation audit
- **Quarterly**: Review and update documentation management guide

---

## Collaboration Protocols

### Between Agents

1. **Tooling → Documentation**: After config changes, update relevant docs
2. **Documentation → All**: Keep AGENTS.md and guides current
3. **All → Tooling**: Run linting before handoffs

### With Human Developers

- Use `docs/FIXES_INDEX.md` to communicate completed fixes
- Create detailed fix docs in `docs/fixes/` for complex issues
- Update `CHANGELOG.md` for user-facing changes

---

## Project-Specific Entry Points

**Always start here**:

- `docs/FIXES_INDEX.md` → Bug fixes and improvements
- `README.md` → Project overview and navigation
- `AGENTS.md` → Agent collaboration guide
- `docs/NAMING_CONVENTIONS.md` → Documentation standards
- `docs/DOCUMENTATION_MANAGEMENT.md` → Complete documentation guide

---

## Notes

- Keep `.gitignore` exclusions in sync with repo tooling
- When updating shared types, change both TypeScript types and Prisma models (if applicable)
- Document major architectural decisions in `README.md` alongside `AGENTS.md`

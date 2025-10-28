---
trigger: manual
---

# Agent Configuration

> **Referenced By**: `AGENTS.md`

## Agent Responsibilities

### [tooling-agent]

<!-- Example for a Python project. Adapt for your tech stack (e.g., package.json for Node.js, pom.xml for Java). -->

**Configurations to Maintain**:

- `pyproject.toml` - Project dependencies and tool configurations

**Tool-Specific Rules**:

- **Ruff**: Maintain consistency across all Python files
- **MyPy**: Ensure type hints are accurate

**Handoff Checklist**:

- [ ] Run linter (`ruff check .`)
- [ ] Run type checker (`mypy .`)
- [ ] Ensure all tests pass (`pytest`)

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

**Authority Documents**: See `.agents/rules/doc-authorities.md` for the complete mapping.

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

- Use `docs/FIXES_INDEX.md` to communicate completed fixes.
- Create detailed fix docs in `docs/fixes/` for complex issues.
- Update `CHANGELOG.md` for user-facing changes.

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

<!-- Add any project-specific notes for agent collaboration here. -->

- Keep `.gitignore` exclusions in sync with repo tooling.
- When updating shared types, ensure consistency across the stack (e.g., backend models and frontend types).
- Document major architectural decisions in `README.md` alongside `AGENTS.md`.

# Documentation System Quick Reference

> **⚡ Quick commands for the standardized documentation system**

## Required Files

```
✅ AGENTS.md
✅ docs/DOCUMENTATION_MANAGEMENT.md
✅ docs/NAMING_CONVENTIONS.md
✅ .agents/doc-review-config.yml
```

## Quick Commands

```bash
# Initialize new project
./scripts/doc-agent-check.sh init

# Quick check (< 10s)
./scripts/doc-agent-check.sh quick

# Standard check (< 30s)
./scripts/doc-agent-check.sh standard

# Deep audit (< 60s)
./scripts/doc-agent-check.sh deep

# Skip AI checks
DOC_AI_CHECK=false git commit
```

## File Naming Rules

- **UPPERCASE.md** - Major docs (README.md, AGENTS.md)
- **kebab-case.md** - Regular docs (api-guide.md)
- **YYYY-MM-DD-description.md** - Date-stamped (fixes, logs)

## SSOT Principle

**One authoritative source per topic**:

- ✅ Brief summary + link to authority
- ❌ Duplicate detailed content (>30% overlap)

## Configuration

```yaml
# .agents/doc-review-config.yml
agent: "gemini-cli"  # or codex-cli, claude-cli

timeouts:
  quick: 10
  standard: 30
  deep: 60

exclude_patterns:
  - "docs/archive/**"
```

## Troubleshooting

```bash
# Missing files
./scripts/doc-agent-check.sh init

# Agent not found
DOC_AI_CHECK=false ./scripts/doc-agent-check.sh quick

# Timeout
# Edit .agents/doc-review-config.yml → increase timeout
```

## Full Documentation

- [Standard System Overview](./STANDARD_DOC_SYSTEM.md)
- [Documentation Management](../docs/DOCUMENTATION_MANAGEMENT.md)
- [Naming Conventions](../docs/NAMING_CONVENTIONS.md)

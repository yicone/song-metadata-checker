# Husky Quick Reference

> **⚡ Quick commands for daily use**

## Installation

```bash
# One-command setup
./setup-husky.sh

# Manual setup
pnpm install
chmod +x .husky/pre-commit scripts/*.sh
```

## Commit Commands

```bash
# Normal commit (all checks)
git commit -m "docs: update"

# Skip AI check (faster)
DOC_AI_CHECK=false git commit -m "docs: minor fix"

# Skip all checks (emergency only)
git commit --no-verify -m "docs: emergency"
```

## Manual Checks

```bash
# Lint markdown
pnpm lint:md

# Fix markdown
pnpm lint:md:fix

# Check links
./scripts/check-links.sh

# AI review
./scripts/doc-agent-check.sh quick
```

## Troubleshooting

```bash
# Reinstall husky
rm -rf .husky node_modules
pnpm install

# Fix permissions
chmod +x .husky/pre-commit scripts/*.sh

# Check hook status
ls -la .husky/
```

## What Gets Checked

1. ✅ **lint-staged** - Auto-format staged files
2. ✅ **Markdown linting** - If `.md` files staged
3. ✅ **Link checking** - Always runs
4. ⚠️ **AI review** - Optional (default: on)

## Environment Variables

```bash
# Disable AI checks globally
export DOC_AI_CHECK=false

# Enable AI checks (default)
export DOC_AI_CHECK=true
```

## Full Documentation

- [Setup Guide](../docs/guides/HUSKY_SETUP.md)
- [Integration Details](./HUSKY_INTEGRATION.md)

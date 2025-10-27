# Husky Pre-Commit Hook Setup Guide

> **📍 Project**: song-metadata-checker  
> **Last Updated**: 2025-01-27  
> **Purpose**: Automate documentation quality checks before commits

## Overview

This project uses Husky to run automated checks before each commit, ensuring documentation quality and consistency.

## Prerequisites

- **Node.js**: >= 18.0.0
- **pnpm**: >= 8.0.0
- **Python**: 3.12+ (for Python linting)
- **Poetry**: For Python dependency management

## Installation

### 1. Install Node.js Dependencies

```bash
# Install pnpm if not already installed
npm install -g pnpm

# Install project dependencies
pnpm install
```

This will:

- Install Husky, lint-staged, and markdownlint-cli
- Run `husky` (via the `prepare` script) to set up Git hooks
- Create `.husky/` directory with pre-commit hook

### 2. Verify Installation

```bash
# Check if husky is installed
ls -la .husky/

# Should see:
# - pre-commit (executable)
# - _/ (husky internal directory)
```

### 3. Make Scripts Executable

```bash
chmod +x .husky/pre-commit
chmod +x scripts/check-links.sh
chmod +x scripts/doc-agent-check.sh
```

## What Gets Checked

The pre-commit hook runs three types of checks:

### 1. Code Formatting (lint-staged)

**Runs on**: Staged files only

**Markdown files** (`.md`):

- `markdownlint --fix` - Auto-fixes formatting issues

**Python files** (`.py`):

- `ruff check --fix` - Lints and fixes code issues
- `ruff format` - Formats code

### 2. Markdown Linting

**Runs on**: All markdown files (if any `.md` files are staged)

```bash
pnpm lint:md
```

**Checks**:

- Heading structure
- List formatting
- Code block formatting
- Link syntax
- Trailing whitespace

### 3. Link Checking

**Runs on**: All documentation links

```bash
./scripts/check-links.sh
```

**Checks**:

- Internal links (relative paths)
- Anchor links (heading references)
- File existence

### 4. AI Documentation Review (Optional)

**Runs on**: Documentation consistency (controlled by `DOC_AI_CHECK` env var)

```bash
./scripts/doc-agent-check.sh quick
```

**Checks**:

- File naming conventions
- Basic markdown structure
- Documentation consistency
- SSOT compliance

**Default**: Enabled (runs automatically)

**Note**: This uses the [Standardized Documentation System](../../.windsurf/STANDARD_DOC_SYSTEM.md) which is designed for cross-project reuse.

## Usage

### Normal Commit (All Checks)

```bash
git add .
git commit -m "docs: update API documentation"
```

This will run all checks automatically.

### Skip AI Documentation Check

```bash
DOC_AI_CHECK=false git commit -m "docs: minor typo fix"
```

Use this for minor changes that don't require AI review.

### Skip All Checks (Not Recommended)

```bash
git commit --no-verify -m "docs: emergency fix"
```

⚠️ **Warning**: Only use in emergencies. Your commit may break documentation quality.

## Troubleshooting

### Issue: "pnpm: command not found"

**Solution**:

```bash
npm install -g pnpm
```

### Issue: "Permission denied" for scripts

**Solution**:

```bash
chmod +x .husky/pre-commit
chmod +x scripts/check-links.sh
chmod +x scripts/doc-agent-check.sh
```

### Issue: Markdown linting fails

**Solution**:

```bash
# Auto-fix markdown issues
pnpm lint:md:fix

# Or manually fix issues reported by the linter
```

### Issue: Link check fails

**Solution**:

1. Check the error message for broken links
2. Fix the links in the documentation
3. Verify with: `./scripts/check-links.sh`

### Issue: AI documentation check fails

**Solution**:

1. Review the AI agent's feedback
2. Fix the reported issues
3. Or skip AI check: `DOC_AI_CHECK=false git commit`

## Configuration

### Markdown Linting Rules

Edit `.markdownlint.json`:

```json
{
  "MD013": false,
  "MD033": false
}
```

### Lint-Staged Configuration

Edit `package.json`:

```json
{
  "lint-staged": {
    "*.md": ["markdownlint --fix"],
    "*.py": ["ruff check --fix", "ruff format"]
  }
}
```

### Disable Specific Checks

**Disable markdown linting**:

```bash
# Remove or comment out in .husky/pre-commit
# pnpm lint:md
```

**Disable link checking**:

```bash
# Remove or comment out in .husky/pre-commit
# ./scripts/check-links.sh
```

**Disable AI checks by default**:

```bash
# Add to .env or .bashrc
export DOC_AI_CHECK=false
```

## CI/CD Integration

The same checks can be run in CI/CD:

```yaml
# .github/workflows/docs-check.yml
name: Documentation Quality

on: [push, pull_request]

jobs:
  docs-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install pnpm
        run: npm install -g pnpm

      - name: Install dependencies
        run: pnpm install

      - name: Lint markdown
        run: pnpm lint:md

      - name: Check links
        run: ./scripts/check-links.sh

      - name: AI documentation review
        run: ./scripts/doc-agent-check.sh quick
```

## Related Documentation

- [Documentation Management Guide](../DOCUMENTATION_MANAGEMENT.md)
- [Naming Conventions](../NAMING_CONVENTIONS.md)
- [Documentation Review Workflow](../../.windsurf/workflows/doc-review.md)

## Maintenance

### Update Dependencies

```bash
# Update all dependencies
pnpm update

# Update specific package
pnpm update husky
```

### Upgrade Husky

```bash
# Check current version
pnpm list husky

# Upgrade to latest
pnpm update husky@latest
```

## Best Practices

1. **Run checks locally** before pushing to catch issues early
2. **Fix issues immediately** rather than skipping checks
3. **Use `DOC_AI_CHECK=false`** only for trivial changes
4. **Keep scripts executable** with proper permissions
5. **Update documentation** when modifying check scripts

## FAQ

**Q: Why use Node.js tools in a Python project?**  
A: Husky and markdownlint are industry-standard tools for Git hooks and Markdown linting. They work well alongside Python tooling.

**Q: Can I disable husky completely?**  
A: Yes, but not recommended. If needed:

```bash
rm -rf .husky
# Remove "prepare": "husky" from package.json
```

**Q: How long do the checks take?**  
A:

- Lint-staged: < 5 seconds
- Markdown linting: < 10 seconds
- Link checking: < 15 seconds
- AI review: 30-60 seconds (optional)

**Q: What if I'm in a hurry?**  
A: Use `DOC_AI_CHECK=false` to skip the slowest check, but don't skip all checks.

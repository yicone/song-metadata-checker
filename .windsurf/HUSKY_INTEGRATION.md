# Husky Integration Summary

> **Date**: 2025-10-27
> **Purpose**: Document the Husky pre-commit hook integration

## What Was Added

### 1. Node.js Package Management

**File**: `package.json`

```json
{
  "name": "song-metadata-checker",
  "version": "0.1.0",
  "scripts": {
    "prepare": "husky",
    "lint:md": "markdownlint '**/*.md' --ignore node_modules --ignore .venv ...",
    "lint:md:fix": "markdownlint '**/*.md' ... --fix"
  },
  "lint-staged": {
    "*.md": ["markdownlint --fix"],
    "*.py": ["ruff check --fix", "ruff format"]
  },
  "devDependencies": {
    "husky": "^9.0.11",
    "lint-staged": "^15.2.0",
    "markdownlint-cli": "^0.39.0"
  }
}
```

**Purpose**:

- Manage Node.js dependencies for Git hooks
- Define npm scripts for markdown linting
- Configure lint-staged for automatic formatting

### 2. Pre-Commit Hook

**File**: `.husky/pre-commit`

**Checks performed**:

1. **lint-staged**: Auto-format staged files (`.md`, `.py`)
2. **Markdown linting**: Lint all markdown files if any are staged
3. **Link checking**: Verify all documentation links
4. **AI documentation review**: Optional consistency check (controlled by `DOC_AI_CHECK`)

**Exit behavior**:

- Fails fast on any error
- Provides helpful tips for skipping checks
- Shows clear error messages

### 3. Setup Script

**File**: `setup-husky.sh`

**Purpose**: One-command installation script

```bash
./setup-husky.sh
```

**Actions**:

- Installs pnpm if needed
- Installs Node.js dependencies
- Makes scripts executable
- Verifies installation

### 4. Documentation

**File**: `docs/guides/HUSKY_SETUP.md`

**Contents**:

- Installation instructions
- Usage examples
- Troubleshooting guide
- Configuration options
- CI/CD integration examples
- FAQ

## Architecture

### Hybrid Tooling Approach

This project uses a **hybrid Python + Node.js** tooling setup:

**Python (Poetry)**:

- Core application code
- Python linting (Ruff)
- Type checking (MyPy)
- Testing (pytest)

**Node.js (pnpm)**:

- Git hooks management (Husky)
- Markdown linting (markdownlint-cli)
- Staged files processing (lint-staged)

**Why this approach?**

- Husky is the industry standard for Git hooks
- markdownlint-cli is the best Markdown linter
- Works seamlessly alongside Python tooling
- No conflicts between ecosystems

## File Structure

```
song-metadata-checker/
├── package.json                    # Node.js dependencies
├── pnpm-lock.yaml                  # pnpm lockfile (auto-generated)
├── node_modules/                   # Node.js packages (gitignored)
│
├── .husky/
│   ├── _/                          # Husky internals
│   └── pre-commit                  # Pre-commit hook script
│
├── setup-husky.sh                  # Installation script
│
├── scripts/
│   ├── check-links.sh              # Link checker (existing)
│   └── doc-agent-check.sh          # AI doc review (existing)
│
└── docs/guides/
    └── HUSKY_SETUP.md              # Setup documentation
```

## Usage Examples

### Normal Commit

```bash
git add .
git commit -m "docs: update API documentation"
```

**Output**:

```
✔ Preparing lint-staged...
✔ Running tasks for staged files...
✔ Applying modifications from tasks...
✔ Cleaning up temporary files...

📚 Running documentation checks...
  🔍 Linting markdown files...
  ✅ Markdown linting passed
  🔗 Checking documentation links...
  ✅ Link check passed
  🤖 Running AI documentation review...
  ✅ AI documentation check passed

✅ All documentation checks passed!
```

### Skip AI Check

```bash
DOC_AI_CHECK=false git commit -m "docs: fix typo"
```

### Skip All Checks (Emergency)

```bash
git commit --no-verify -m "docs: emergency fix"
```

## Integration Points

### With Python Tooling

**Ruff** (Python linter):

- Configured in `pyproject.toml`
- Called by lint-staged for `.py` files
- Runs automatically on staged Python files

**MyPy** (Type checker):

- Not in pre-commit (too slow)
- Run manually or in CI/CD

### With Existing Scripts

**check-links.sh**:

- Already exists in `scripts/`
- Called by pre-commit hook
- Fast, always runs

**doc-agent-check.sh**:

- Already exists in `scripts/`
- Called by pre-commit hook
- Optional (controlled by `DOC_AI_CHECK`)

## Performance

Typical commit times:

| Check            | Time   | Frequency              |
| ---------------- | ------ | ---------------------- |
| lint-staged      | < 5s   | Always                 |
| Markdown linting | < 10s  | If `.md` staged        |
| Link checking    | < 15s  | Always                 |
| AI review        | 30-60s | Optional (default: on) |

**Total**: ~30s (without AI) or ~90s (with AI)

## Maintenance

### Update Dependencies

```bash
# Update all
pnpm update

# Update specific package
pnpm update husky@latest
```

### Modify Checks

Edit `.husky/pre-commit`:

- Comment out checks you don't want
- Add new checks
- Adjust error messages

### Add New File Types

Edit `package.json`:

```json
{
  "lint-staged": {
    "*.md": ["markdownlint --fix"],
    "*.py": ["ruff check --fix", "ruff format"],
    "*.json": ["prettier --write"] // Add new type
  }
}
```

## Troubleshooting

### Common Issues

1. **"pnpm: command not found"**

   ```bash
   npm install -g pnpm
   ```

2. **"Permission denied" for scripts**

   ```bash
   chmod +x .husky/pre-commit
   chmod +x scripts/*.sh
   ```

3. **Hook not running**

   ```bash
   # Reinstall husky
   rm -rf .husky
   pnpm install
   ```

4. **Slow commits**

   ```bash
   # Skip AI check
   DOC_AI_CHECK=false git commit
   ```

## CI/CD Integration

The same checks can run in GitHub Actions:

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

      - name: Run all checks
        run: |
          pnpm lint:md
          ./scripts/check-links.sh
          ./scripts/doc-agent-check.sh quick
```

## Benefits

1. **Automated Quality**: Catches issues before they're committed
2. **Fast Feedback**: Runs in seconds, not minutes
3. **Consistent Style**: Auto-formats code and docs
4. **Flexible**: Easy to skip checks when needed
5. **Standard Tools**: Uses industry-standard tools (Husky, markdownlint)
6. **Hybrid Approach**: Best of both Python and Node.js ecosystems

## Related Documentation

- [Husky Setup Guide](../docs/guides/HUSKY_SETUP.md)
- [Documentation Management](../docs/DOCUMENTATION_MANAGEMENT.md)
- [Agent Configuration](./rules/agent-config.md)

## Next Steps

1. **Run the setup script**: `./setup-husky.sh`
2. **Test the hook**: Make a commit and see it in action
3. **Customize**: Adjust checks in `.husky/pre-commit` as needed
4. **CI/CD**: Add checks to your CI/CD pipeline
5. **Team**: Share `docs/guides/HUSKY_SETUP.md` with your team

## Notes

- **Node.js version**: Requires >= 18.0.0
- **pnpm version**: Requires >= 8.0.0
- **Python unchanged**: Python tooling (Poetry, Ruff, MyPy) works as before
- **Backwards compatible**: Existing workflows unchanged
- **Optional AI check**: Can be disabled globally or per-commit

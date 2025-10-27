# Standardized Documentation System

> **📦 Cross-Project Reusable System**  
> **Version**: 1.0.0  
> **Last Updated**: 2025-01-27

## Overview

This project uses a **standardized documentation system** designed for cross-project reuse. The system ensures consistent documentation quality, structure, and AI-assisted review across all your projects.

## Core Components

### 1. Required Files

```
project/
├── AGENTS.md                          # Agent collaboration protocol
├── docs/
│   ├── DOCUMENTATION_MANAGEMENT.md    # Documentation rules & SSOT
│   └── NAMING_CONVENTIONS.md          # Naming standards
├── .agents/
│   └── doc-review-config.yml          # Review configuration
└── scripts/
    └── doc-agent-check.sh             # AI-powered review script
```

### 2. Standard Context Files (Hardcoded)

These files are **hardcoded** in `scripts/doc-agent-check.sh` as part of the standard:

- `AGENTS.md` - Agent collaboration protocol
- `docs/DOCUMENTATION_MANAGEMENT.md` - Documentation rules
- `docs/NAMING_CONVENTIONS.md` - Naming standards

**Why hardcoded?** This is **convention over configuration**. All projects following this standard have these files in these locations.

### 3. Project-Specific Configuration

`.agents/doc-review-config.yml` is for **project-specific overrides only**:

```yaml
# Agent selection
agent: "gemini-cli"  # or codex-cli, claude-cli

# Timeouts
timeouts:
  quick: 10
  standard: 30
  deep: 60

# Custom checks (project-specific)
custom_checks:
  - name: "API Documentation Sync"
    level: "standard"
    prompt: |
      Check if API docs match OpenAPI spec...

# Exclusions
exclude_patterns:
  - "docs/archive/**"
```

## Quick Start

### For New Projects

```bash
# 1. Copy the script to your project
cp scripts/doc-agent-check.sh /path/to/new-project/scripts/

# 2. Initialize the standard structure
cd /path/to/new-project
./scripts/doc-agent-check.sh init

# 3. Customize the generated files
# Edit AGENTS.md, docs/DOCUMENTATION_MANAGEMENT.md, etc.

# 4. Run a test check
./scripts/doc-agent-check.sh quick
```

### For Existing Projects

If your project already has these files, just ensure they follow the standard structure:

```bash
# Check if your project is compatible
./scripts/doc-agent-check.sh quick

# If missing files, you'll get a helpful error message
```

## Usage

### Manual Checks

```bash
# Quick check (< 10s)
./scripts/doc-agent-check.sh quick

# Standard check (< 30s)
./scripts/doc-agent-check.sh standard

# Deep audit (< 60s)
./scripts/doc-agent-check.sh deep
```

### Pre-Commit Hook Integration

See `docs/guides/HUSKY_SETUP.md` for Husky integration:

```bash
# .husky/pre-commit
./scripts/doc-agent-check.sh quick || exit 1
```

### Environment Variables

```bash
# Disable AI checks
DOC_AI_CHECK=false git commit

# Enable verbose output
DOC_CHECK_VERBOSE=true ./scripts/doc-agent-check.sh standard
```

## Design Philosophy

### Convention Over Configuration

**Hardcoded paths are intentional**:

- Reduces configuration complexity
- Ensures consistency across projects
- Makes the system portable

**Configuration is for exceptions**:

- Project-specific checks
- Custom exclusions
- Timeout adjustments

### Cross-Project Portability

The entire system can be copied to a new project:

```bash
# Copy the standard system
cp -r scripts/doc-agent-check.sh /new-project/scripts/
cp -r .agents/doc-review-config.yml /new-project/.agents/

# Initialize
cd /new-project
./scripts/doc-agent-check.sh init
```

### AI Agent Compatibility

Tested with:

- ✅ Windsurf Cascade
- ✅ Cursor
- ✅ Aider
- ✅ Continue.dev
- ✅ Gemini CLI
- ✅ Codex CLI
- ✅ Claude CLI

## Standard Checks

### Quick Level (< 10s)

1. **File Naming Convention** - Verify files follow naming standards
2. **Basic Structure** - Check markdown structure

### Standard Level (< 30s)

1. **SSOT Violations** - Check for duplicate content
2. **Content Duplication** - Flag >30% overlap
3. **Documentation Structure** - Verify structure guidelines
4. **Link Integrity** - Check internal links

### Deep Level (< 60s)

1. **Full Documentation Audit** - Comprehensive quality check
   - SSOT compliance
   - Link integrity
   - Naming conventions
   - Audience appropriateness
   - Index updates
   - CHANGELOG updates

## Customization

### Adding Project-Specific Checks

Edit `.agents/doc-review-config.yml`:

```yaml
custom_checks:
  - name: "Database Schema Sync"
    level: "standard"
    prompt: |
      Check if database documentation matches schema.sql:
      1. All tables documented
      2. Column types match
      3. Relationships documented
```

### Excluding Files

```yaml
exclude_patterns:
  - "docs/archive/**"
  - "docs/drafts/**"
  - "**/*-wip.md"
```

### Changing Agent

```yaml
# Use OpenAI Codex instead of Gemini
agent: "codex-cli"

env:
  codex_model: "gpt-4"
```

## Troubleshooting

### "Missing required files"

```bash
# Initialize the standard structure
./scripts/doc-agent-check.sh init

# Or create files manually
```

### "Agent not found"

```bash
# Install the agent
npm install -g @google/generative-ai-cli  # for gemini-cli
# or
pip install openai-cli  # for codex-cli

# Or disable AI checks
DOC_AI_CHECK=false ./scripts/doc-agent-check.sh quick
```

### "Timeout occurred"

```bash
# Increase timeout in .agents/doc-review-config.yml
timeouts:
  standard: 60  # Increase from 30 to 60
```

## Template Repository

Consider creating a template repository with the standard structure:

```
github.com/your-username/doc-standards-template
├── AGENTS.md
├── docs/
│   ├── DOCUMENTATION_MANAGEMENT.md
│   └── NAMING_CONVENTIONS.md
├── .agents/
│   └── doc-review-config.yml
└── scripts/
    └── doc-agent-check.sh
```

Then use it for new projects:

```bash
# Create new project from template
gh repo create my-new-project --template your-username/doc-standards-template
```

## Version History

- **1.0.0** (2025-01-27) - Initial standardized system
  - Hardcoded standard context files
  - Project-specific configuration support
  - AI agent compatibility
  - Cross-project portability

## Related Documentation

- [Husky Integration](./HUSKY_INTEGRATION.md)
- [Documentation Management](../docs/DOCUMENTATION_MANAGEMENT.md)
- [Naming Conventions](../docs/NAMING_CONVENTIONS.md)
- [Agent Configuration](./rules/agent-config.md)

## License

This standardized documentation system is designed for personal/organizational use. Feel free to adapt it to your needs.

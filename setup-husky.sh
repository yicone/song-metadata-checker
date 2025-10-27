#!/bin/bash

# Husky Setup Script for song-metadata-checker
# This script installs and configures Husky pre-commit hooks

set -e  # Exit on error

echo "🚀 Setting up Husky pre-commit hooks..."
echo ""

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm is not installed"
    echo "📦 Installing pnpm..."
    npm install -g pnpm
    echo "✅ pnpm installed"
    echo ""
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
pnpm install
echo "✅ Dependencies installed"
echo ""

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x .husky/pre-commit
chmod +x scripts/check-links.sh
chmod +x scripts/doc-agent-check.sh
echo "✅ Scripts are now executable"
echo ""

# Verify installation
echo "🔍 Verifying installation..."
if [ -f ".husky/pre-commit" ]; then
    echo "✅ Pre-commit hook installed"
else
    echo "❌ Pre-commit hook not found"
    exit 1
fi

echo ""
echo "🎉 Husky setup complete!"
echo ""
echo "📚 Next steps:"
echo "  1. Test the hook: git add . && git commit -m 'test: husky setup'"
echo "  2. Read the guide: docs/guides/HUSKY_SETUP.md"
echo ""
echo "💡 Tips:"
echo "  - Skip AI checks: DOC_AI_CHECK=false git commit"
echo "  - Skip all checks: git commit --no-verify (not recommended)"
echo ""

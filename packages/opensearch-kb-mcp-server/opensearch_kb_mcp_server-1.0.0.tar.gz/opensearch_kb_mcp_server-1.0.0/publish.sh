#!/bin/bash
# Quick publish script for PyPI

set -e

echo "========================================="
echo "Publishing OpenSearch KB MCP Server"
echo "========================================="
echo ""

# Check if in correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from mcp-server directory"
    exit 1
fi

# Check version
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "📦 Package version: $VERSION"
echo ""

# Confirm
read -p "Publish version $VERSION to PyPI? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info opensearch_kb_mcp_server.egg-info
echo ""

# Build
echo "🔨 Building package..."
python -m build
echo ""

# Check build
echo "✅ Build complete:"
ls -lh dist/
echo ""

# Ask about TestPyPI
read -p "Upload to TestPyPI first? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "📤 Uploading to TestPyPI..."
    python -m twine upload --repository testpypi dist/*
    echo ""
    echo "✅ Uploaded to TestPyPI"
    echo "Test with: pip install --index-url https://test.pypi.org/simple/ opensearch-knowledge-base-mcp-server"
    echo ""
    read -p "Continue to production PyPI? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopped at TestPyPI"
        exit 0
    fi
fi

# Upload to PyPI
echo "📤 Uploading to PyPI..."
python -m twine upload dist/*
echo ""

echo "========================================="
echo "✅ Published successfully!"
echo "========================================="
echo ""
echo "Package: https://pypi.org/project/opensearch-knowledge-base-mcp-server/"
echo "Version: $VERSION"
echo ""
echo "Users can now install with:"
echo "  uvx opensearch-knowledge-base-mcp-server"
echo ""
echo "Or configure in their AI agent:"
echo '  "command": "uvx",'
echo '  "args": ["opensearch-knowledge-base-mcp-server"]'

# Publishing to PyPI

This guide explains how to publish the OpenSearch Knowledge Base MCP Server to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/
2. **API Token**: Generate an API token at https://pypi.org/manage/account/token/
3. **Build Tools**: Install required tools

```bash
pip install build twine
```

## Publishing Steps

### 1. Update Version

Edit `pyproject.toml` and increment the version:

```toml
[project]
version = "1.0.1"  # Increment this
```

### 2. Clean Previous Builds

```bash
cd mcp-server
rm -rf dist/ build/ *.egg-info
```

### 3. Build the Package

```bash
python -m build
```

This creates:
- `dist/opensearch_knowledge_base_mcp_server-1.0.0-py3-none-any.whl`
- `dist/opensearch-knowledge-base-mcp-server-1.0.0.tar.gz`

### 4. Test the Build Locally

```bash
# Install locally
pip install dist/opensearch_knowledge_base_mcp_server-1.0.0-py3-none-any.whl

# Test it works
export OPENSEARCH_KB_API_URL="https://your-api-url"
export OPENSEARCH_KB_API_TOKEN="your-token"
opensearch-knowledge-base-mcp-server
```

### 5. Upload to TestPyPI (Optional but Recommended)

Test on TestPyPI first:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ opensearch-knowledge-base-mcp-server
```

### 6. Upload to PyPI

```bash
python -m twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

### 7. Verify Publication

```bash
# Check on PyPI
open https://pypi.org/project/opensearch-knowledge-base-mcp-server/

# Test installation
pip install opensearch-knowledge-base-mcp-server

# Test with uvx
uvx opensearch-knowledge-base-mcp-server
```

## Using the Published Package

Once published, users can use it with:

### Claude Desktop

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "uvx",
      "args": ["opensearch-knowledge-base-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-url",
        "OPENSEARCH_KB_API_TOKEN": "your-token"
      }
    }
  }
}
```

### Cline / Kiro

Same configuration as above.

## Updating the Package

When you make changes:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` (create if doesn't exist)
3. Commit changes
4. Create a git tag: `git tag v1.0.1`
5. Push tag: `git push origin v1.0.1`
6. Build and publish: `python -m build && twine upload dist/*`

## Troubleshooting

### Error: File already exists

You're trying to upload a version that already exists. Increment the version number.

### Error: Invalid credentials

Check your PyPI API token. Make sure:
- Username is `__token__`
- Password is your full API token including `pypi-` prefix

### Error: Package name already taken

The package name `opensearch-knowledge-base-mcp-server` might be taken. Choose a different name in `pyproject.toml`.

### Import Error After Installation

Make sure the package structure is correct:
```
mcp-server/
├── opensearch_kb_mcp_server/
│   ├── __init__.py
│   └── server.py
└── pyproject.toml
```

## Best Practices

1. **Semantic Versioning**: Use MAJOR.MINOR.PATCH
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes

2. **Changelog**: Maintain a CHANGELOG.md file

3. **Testing**: Test on TestPyPI before production

4. **Git Tags**: Tag releases in git

5. **Documentation**: Keep README.md up to date

## Automation with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install build twine
      
      - name: Build package
        run: |
          cd mcp-server
          python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          cd mcp-server
          python -m twine upload dist/*
```

Then:
1. Add `PYPI_API_TOKEN` to GitHub Secrets
2. Create a release on GitHub
3. Package is automatically published

## Support

For issues:
- GitHub Issues: https://github.com/your-org/opensearch-knowledge-base-mcp/issues
- PyPI Page: https://pypi.org/project/opensearch-knowledge-base-mcp-server/

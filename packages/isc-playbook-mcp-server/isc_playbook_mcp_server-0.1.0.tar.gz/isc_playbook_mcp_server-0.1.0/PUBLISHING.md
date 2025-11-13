# Publishing Guide for isc-playbook-mcp-server

This guide will help you publish your MCP server to PyPI so users can install it with `uv` and `uvx`.

## Prerequisites

1. **Install build tools**:
   ```bash
   pip install build twine
   ```

2. **Create PyPI account**:
   - Sign up at https://pypi.org/account/register/
   - Verify your email
   - Set up 2FA (required for publishing)

3. **Create API token**:
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with scope "Entire account"
   - Save the token securely (starts with `pypi-`)

## Pre-Publishing Checklist

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.1.0"  # Follow semantic versioning
   ```

2. **Update author information** in `pyproject.toml`:
   ```toml
   authors = [
       {name = "Your Name", email = "your.email@example.com"}
   ]
   ```

3. **Update repository URLs** in `pyproject.toml`:
   ```toml
   [project.urls]
   Homepage = "https://github.com/yourusername/isc-playbook-mcp-server"
   Repository = "https://github.com/yourusername/isc-playbook-mcp-server"
   Issues = "https://github.com/yourusername/isc-playbook-mcp-server/issues"
   ```

4. **Ensure data files are included**:
   - Make sure `data/index/playbook_hybrid.db` exists
   - Make sure `data/cleaned/cleaned_pages.json` exists

5. **Test locally**:
   ```bash
   # Install in development mode
   pip install -e .
   
   # Test the command
   isc-playbook-mcp-server --help
   ```

## Building the Package

1. **Clean previous builds**:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

2. **Build the package**:
   ```bash
   python -m build
   ```

   This creates:
   - `dist/isc_playbook_mcp_server-0.1.0.tar.gz` (source distribution)
   - `dist/isc_playbook_mcp_server-0.1.0-py3-none-any.whl` (wheel)

3. **Check the package**:
   ```bash
   twine check dist/*
   ```

## Publishing to PyPI

### Test on TestPyPI First (Recommended)

1. **Upload to TestPyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```
   
   Enter your username (`__token__`) and your TestPyPI API token.

2. **Test installation from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ isc-playbook-mcp-server
   ```

### Publish to PyPI

1. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```
   
   Enter your username (`__token__`) and your PyPI API token.

2. **Verify publication**:
   - Visit https://pypi.org/project/isc-playbook-mcp-server/
   - Check that all information displays correctly

## Using the Published Package

Once published, users can install and use your MCP server in three ways:

### 1. With uvx (Easiest):
```bash
uvx isc-playbook-mcp-server
```

### 2. With uv:
```bash
uv tool install isc-playbook-mcp-server
isc-playbook-mcp-server
```

### 3. With pip:
```bash
pip install isc-playbook-mcp-server
isc-playbook-mcp-server
```

## MCP Configuration

Users can configure the server in their MCP settings:

```json
{
  "mcpServers": {
    "isc-playbook": {
      "command": "uvx",
      "args": ["isc-playbook-mcp-server"]
    }
  }
}
```

## Version Updates

To publish a new version:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Commit and tag the release:
   ```bash
   git commit -am "Release v0.1.1"
   git tag v0.1.1
   git push origin main --tags
   ```
4. Build and publish:
   ```bash
   rm -rf dist/
   python -m build
   twine upload dist/*
   ```

## Troubleshooting

### Package too large
If your package exceeds PyPI's size limit (100MB), consider:
- Excluding large data files
- Using separate data downloads
- Hosting large files elsewhere

### Import errors after installation
- Check that `__init__.py` exists in package directory
- Verify package structure in `pyproject.toml`
- Test import: `python -c "from isc_playbook_mcp_server import server"`

### Command not found
- Ensure entry point is correct in `pyproject.toml`
- Reinstall: `pip install --force-reinstall isc-playbook-mcp-server`

## CI/CD Automation (Optional)

Consider setting up GitHub Actions for automated publishing:

1. Add PyPI token to GitHub Secrets
2. Create `.github/workflows/publish.yml`
3. Automate publishing on tag creation

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)
- [MCP Documentation](https://modelcontextprotocol.io/)

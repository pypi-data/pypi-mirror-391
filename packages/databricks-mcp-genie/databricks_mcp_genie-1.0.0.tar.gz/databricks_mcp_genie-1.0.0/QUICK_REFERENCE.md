# Quick Reference - databricks-mcp-genie

## Publishing Checklist (First Time)

```bash
# 1. Fill PyPI form (in browser) → Click "Add"
# 2. Create GitHub repo
# 3. Push code
git init
git add .
git commit -m "Initial commit - v1.0.0"
git remote add origin https://github.com/sidart10/databricks-mcp-genie.git
git push -u origin main

# 4. Create GitHub release v1.0.0 → Package auto-publishes!
```

## Future Version Updates

```bash
# 1. Update version in pyproject.toml
version = "1.0.1"

# 2. Commit and push
git add pyproject.toml
git commit -m "Bump version to 1.0.1"
git push

# 3. Create GitHub release v1.0.1 → Auto-publishes!
```

## Team Installation (After Publishing)

```bash
# Install
pip install databricks-mcp-genie

# Configure Cursor
# See: docs/CURSOR_SETUP.md
```

## Cursor Config Template

```json
{
  "mcpServers": {
    "databricks": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "databricks_mcp.main"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Useful Commands

```bash
# Build package locally
python -m build

# Test installation
pip install dist/databricks_mcp_genie-1.0.0-py3-none-any.whl

# Check package contents
tar -tzf dist/databricks_mcp_genie-1.0.0.tar.gz | less

# View workflow runs
# https://github.com/sidart10/databricks-mcp-genie/actions
```

## Important Files

- `pyproject.toml` - Package metadata and version
- `.github/workflows/publish.yml` - Auto-publishing workflow
- `docs/CURSOR_SETUP.md` - Team installation guide
- `FINAL_STEPS.md` - Complete publishing checklist

## Links

- PyPI Package: https://pypi.org/project/databricks-mcp-genie/
- GitHub Repo: https://github.com/sidart10/databricks-mcp-genie
- GitHub Actions: https://github.com/sidart10/databricks-mcp-genie/actions
- PyPI Publishing: https://pypi.org/manage/account/publishing/

## Support

Questions? Check:
1. `FINAL_STEPS.md` - Step-by-step publishing
2. `GITHUB_PUBLISHING_GUIDE.md` - Detailed explanations
3. `docs/CURSOR_SETUP.md` - Installation help
4. GitHub Issues - Report bugs

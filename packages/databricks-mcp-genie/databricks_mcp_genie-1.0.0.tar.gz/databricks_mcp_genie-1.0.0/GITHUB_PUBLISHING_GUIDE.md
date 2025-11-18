# GitHub Actions Publishing Guide

Complete guide to publish `databricks-mcp-genie` to PyPI using GitHub Actions (Trusted Publishing).

## What You Have Now

- ✅ PyPI account
- ✅ Package built (`dist/databricks_mcp_genie-1.0.0-py3-none-any.whl`)
- ✅ GitHub Actions workflow (`.github/workflows/publish.yml`)

## Step-by-Step Setup

### Step 1: Configure Trusted Publisher on PyPI

You're already on this page! Fill in the form with these **exact values**:

```
PyPI Project Name: databricks-mcp-genie
Owner: sidart10
Repository name: databricks-mcp-genie
Workflow name: publish.yml
Environment name: pypi
```

Then click **"Add"** button.

**Important**: The project name `databricks-mcp-genie` will be reserved for you once you click Add.

### Step 2: Create GitHub Repository

If you haven't created the repo yet:

1. Go to https://github.com/new
2. Repository name: `databricks-mcp-genie`
3. Description: "MCP server for Databricks with enhanced Genie AI integration"
4. Public or Private: **Public** (recommended for PyPI packages)
5. Click "Create repository"

### Step 3: Push Your Code to GitHub

```bash
cd /Users/sid/Desktop/4.\ Coding\ Projects/databrics-mcp-server

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit - databricks-mcp-genie v1.0.0"

# Add remote (replace with your actual repo URL)
git remote add origin https://github.com/sidart10/databricks-mcp-genie.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Create a GitHub Release (This Triggers Publishing!)

#### Option A: Via GitHub Web Interface (Easier)

1. Go to your repo: `https://github.com/sidart10/databricks-mcp-genie`
2. Click on **"Releases"** (right sidebar)
3. Click **"Create a new release"**
4. Fill in:
   - **Tag version**: `v1.0.0` (must start with 'v')
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**:
     ```
     ## What's New
     - Complete Databricks MCP server with 43 tools
     - Enhanced Genie AI integration for natural language queries
     - Support for clusters, SQL, jobs, notebooks, Unity Catalog
     - One-click installation for Cursor and Claude Code

     ## Installation
     ```
     pip install databricks-mcp-genie
     ```

     See [Cursor Setup Guide](docs/CURSOR_SETUP.md) for configuration.
     ```
5. Click **"Publish release"**

#### Option B: Via Command Line (Advanced)

```bash
# Create and push a tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Then create release on GitHub using gh CLI (if installed)
gh release create v1.0.0 --title "v1.0.0 - Initial Release" --notes "Initial release of databricks-mcp-genie"
```

### Step 5: Watch the Magic Happen!

Once you publish the release:

1. Go to **Actions** tab in your GitHub repo
2. You'll see the "Publish to PyPI" workflow running
3. Wait 2-3 minutes for it to complete
4. Check https://pypi.org/project/databricks-mcp-genie/ - your package is live!

## What the Workflow Does

When you create a GitHub release:

1. **Builds** the package from source
2. **Tests** that the build succeeded
3. **Publishes** to PyPI automatically (using trusted publishing, no tokens needed!)
4. Updates your PyPI package page

## Troubleshooting

### "Workflow not found" error on PyPI

**Problem**: The workflow name doesn't match.

**Solution**: Make sure the workflow file is exactly `.github/workflows/publish.yml`

### Workflow runs but doesn't publish

**Problem**: Trusted publisher not configured correctly.

**Solution**:
- Check PyPI trusted publishers page
- Verify owner, repo name, and workflow name match exactly
- Make sure you clicked "Add" on PyPI

### "Environment 'pypi' not found"

**Solution**: Create environment in GitHub:
1. Go to repo Settings → Environments
2. Click "New environment"
3. Name it `pypi`
4. Click "Configure environment"
5. No need to add any protection rules (unless you want)

Or remove the environment from the workflow:
```yaml
# Remove these lines from .github/workflows/publish.yml
environment:
  name: pypi
  url: https://pypi.org/p/databricks-mcp-genie
```

### How to publish a new version

1. Update version in `pyproject.toml`:
   ```toml
   version = "1.0.1"  # or 1.1.0, 2.0.0, etc.
   ```

2. Commit and push changes:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 1.0.1"
   git push
   ```

3. Create a new release on GitHub with tag `v1.0.1`

4. Workflow runs automatically and publishes!

## Testing Before Publishing

### Test Locally First

```bash
# Build the package
python -m build

# Test installation
pip install dist/databricks_mcp_genie-1.0.0-py3-none-any.whl

# Test import
python -c "from databricks_mcp.server import DatabricksMCPServer; print('Success!')"
```

### Test the Workflow (Without Publishing)

You can test the workflow without publishing by:

1. Push code to a branch (not creating a release)
2. The workflow won't run (it only runs on releases)
3. Or trigger manually via Actions tab → "Publish to PyPI" → "Run workflow"

## Security Benefits

**Why Trusted Publishing is Better:**
- ✅ No API tokens to manage or leak
- ✅ No credentials stored anywhere
- ✅ GitHub verifies the workflow automatically
- ✅ More secure than password/token auth
- ✅ Recommended by PyPI

## Quick Reference

```bash
# Publish new version workflow:
1. Update version in pyproject.toml
2. git commit -am "Bump version to X.Y.Z"
3. git push
4. Create GitHub release with tag vX.Y.Z
5. Wait for workflow to complete
6. Verify on PyPI!
```

## After First Publish

Once your package is live on PyPI:

1. **Test installation**:
   ```bash
   pip install databricks-mcp-genie
   ```

2. **Share with team**:
   - Send them `docs/CURSOR_SETUP.md`
   - Installation command: `pip install databricks-mcp-genie`

3. **Update package anytime**:
   - Just create a new GitHub release
   - Workflow handles everything automatically

## Support

- GitHub Actions docs: https://docs.github.com/en/actions
- PyPI Trusted Publishers: https://docs.pypi.org/trusted-publishers/
- Your workflow runs: https://github.com/sidart10/databricks-mcp-genie/actions

---

**You're all set!** Just complete the PyPI form, push to GitHub, and create your first release.

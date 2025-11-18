# Publishing Guide for databricks-mcp-genie

Instructions for publishing this package to PyPI.

## Prerequisites

1. PyPI account (create at https://pypi.org/account/register/)
2. TestPyPI account (create at https://test.pypi.org/account/register/)
3. Package built locally (already done: `dist/databricks_mcp_genie-1.0.0-py3-none-any.whl`)

## First-Time Setup

### 1. Create PyPI API Tokens

#### For TestPyPI (testing):
1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: "databricks-mcp-genie-test"
4. Scope: "Entire account" (or specific project after first upload)
5. Copy the token (starts with `pypi-...`)

#### For PyPI (production):
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: "databricks-mcp-genie"
4. Scope: "Entire account" (or specific project after first upload)
5. Copy the token (starts with `pypi-...`)

### 2. Configure PyPI Credentials

Create or edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

**Security**: Make sure this file is only readable by you:
```bash
chmod 600 ~/.pypirc
```

## Publishing Steps

### Step 1: Test on TestPyPI First

Always test on TestPyPI before publishing to production PyPI:

```bash
cd /Users/sid/Desktop/4.\ Coding\ Projects/databrics-mcp-server

# Upload to TestPyPI
.venv/bin/twine upload --repository testpypi dist/*
```

### Step 2: Test Installation from TestPyPI

```bash
# Create a fresh test environment
python3 -m venv /tmp/test-install
source /tmp/test-install/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ databricks-mcp-genie

# Test import
python -c "from databricks_mcp.server import DatabricksMCPServer; print('Success!')"

# Clean up
deactivate
rm -rf /tmp/test-install
```

### Step 3: Publish to Production PyPI

Once testing is successful:

```bash
# Upload to production PyPI
.venv/bin/twine upload dist/*
```

### Step 4: Verify on PyPI

1. Visit https://pypi.org/project/databricks-mcp-genie/
2. Check the package page looks correct
3. Test installation:
   ```bash
   pip install databricks-mcp-genie
   ```

## Updating the Package

When you make changes and want to release a new version:

### 1. Update Version Number

Edit `pyproject.toml`:

```toml
[project]
name = "databricks-mcp-genie"
version = "1.0.1"  # Increment this (major.minor.patch)
```

Version numbering:
- **Patch** (1.0.0 → 1.0.1): Bug fixes, no new features
- **Minor** (1.0.0 → 1.1.0): New features, backwards compatible
- **Major** (1.0.0 → 2.0.0): Breaking changes

### 2. Update Changelog

Document changes in README.md or create CHANGELOG.md:

```markdown
## [1.0.1] - 2025-11-14
### Fixed
- Bug fix description

### Added
- New feature description
```

### 3. Rebuild Package

```bash
# Clean old builds
rm -rf dist/ build/

# Build new version
.venv/bin/python -m build
```

### 4. Upload New Version

```bash
# Test on TestPyPI first
.venv/bin/twine upload --repository testpypi dist/*

# Then upload to PyPI
.venv/bin/twine upload dist/*
```

## Common Issues

### "File already exists"

**Problem**: You're trying to upload the same version again.

**Solution**: You cannot replace an existing version on PyPI. You must:
1. Increment the version number in `pyproject.toml`
2. Rebuild the package
3. Upload the new version

### "Invalid credentials"

**Problem**: PyPI API token is incorrect.

**Solution**:
1. Generate a new token from PyPI
2. Update `~/.pypirc`
3. Make sure username is `__token__` (with underscores)

### "Package name already taken"

**Problem**: Someone else has already published a package with this name.

**Solution**: This shouldn't happen with `databricks-mcp-genie`, but if it does, you'll need to choose a different name.

## Security Checklist

Before publishing:
- [ ] No hardcoded credentials in code
- [ ] No `.env` files in package
- [ ] No personal data in examples
- [ ] `.bmad` development files excluded
- [ ] Tests directory excluded
- [ ] LICENSE file included
- [ ] README.md is accurate and helpful

## Package Distribution Checklist

- [ ] Version number updated
- [ ] README.md updated with new features
- [ ] CHANGELOG updated (if you have one)
- [ ] All tests passing
- [ ] Built successfully (`python -m build`)
- [ ] Tested on TestPyPI
- [ ] Installed and tested from TestPyPI
- [ ] Published to production PyPI
- [ ] Verified on PyPI website
- [ ] Tested installation from PyPI
- [ ] Tagged release in Git (optional but recommended)

## Git Tagging (Optional but Recommended)

After successful PyPI publication:

```bash
# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Or create a GitHub release
# Go to https://github.com/sidart10/databricks-mcp-genie/releases/new
```

## Quick Reference Commands

```bash
# Build package
python -m build

# Check package contents
tar -tzf dist/databricks_mcp_genie-VERSION.tar.gz

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install databricks-mcp-genie

# Install specific version
pip install databricks-mcp-genie==1.0.0
```

## Support

If you encounter issues during publishing:
- PyPI Help: https://pypi.org/help/
- Twine docs: https://twine.readthedocs.io/
- Packaging guide: https://packaging.python.org/

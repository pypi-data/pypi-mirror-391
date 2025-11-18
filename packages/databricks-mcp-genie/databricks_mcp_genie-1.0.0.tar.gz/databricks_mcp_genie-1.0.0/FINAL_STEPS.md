# Final Steps to Publish databricks-mcp-genie

You're almost there! Here's your exact checklist:

## Right Now (In the PyPI Browser Tab)

You have the PyPI Trusted Publisher form open. Fill it in:

```
✅ PyPI Project Name: databricks-mcp-genie
✅ Owner: sidart10
✅ Repository name: databricks-mcp-genie
✅ Workflow name: publish.yml
✅ Environment name: pypi
```

Then click the **"Add"** button.

This reserves the package name `databricks-mcp-genie` for you and sets up trusted publishing.

## Next: Create GitHub Repository (5 minutes)

### Option 1: Via GitHub Website (Easier)

1. Go to https://github.com/new
2. Fill in:
   - Repository name: `databricks-mcp-genie`
   - Description: `MCP server for Databricks with enhanced Genie AI integration`
   - Public ✅ (recommended for PyPI packages)
   - Don't initialize with README (you already have one)
3. Click "Create repository"

### Option 2: Via Command Line

```bash
# If you have GitHub CLI installed
gh repo create databricks-mcp-genie --public --source=. --remote=origin
```

## Then: Push Your Code (2 minutes)

```bash
cd /Users/sid/Desktop/4.\ Coding\ Projects/databrics-mcp-server

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - databricks-mcp-genie v1.0.0"

# Add your GitHub repo as remote
git remote add origin https://github.com/sidart10/databricks-mcp-genie.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Finally: Create a GitHub Release (3 minutes)

This automatically publishes to PyPI!

### Via GitHub Website:

1. Go to `https://github.com/sidart10/databricks-mcp-genie`
2. Click **"Releases"** (right sidebar)
3. Click **"Create a new release"**
4. Fill in:
   - **Choose a tag**: `v1.0.0` (type it, then click "Create new tag")
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**: Copy this:

```markdown
## databricks-mcp-genie v1.0.0

First release of the Databricks MCP Genie server - bringing natural language AI to your Databricks workflows!

### Features

- 43 MCP tools across 9 Databricks API modules
- Enhanced Genie AI integration for natural language data queries
- Cluster management (create, start, stop, monitor)
- SQL execution with warehouse support
- Jobs and notebook automation
- Unity Catalog integration
- DBFS, repos, and library management

### Installation

```bash
pip install databricks-mcp-genie
```

### Quick Start

See the [Cursor Setup Guide](docs/CURSOR_SETUP.md) for one-click installation in Cursor IDE.

For Claude Desktop or other MCP clients, see the [Quick Start Guide](QUICK_START.md).

### What's New

- Complete implementation of Databricks APIs
- Genie AI natural language interface
- One-click installation for teams
- Comprehensive documentation

### Credits

Built on the foundation of databricks-mcp by Olivier Debeuf De Rijcker.
Enhanced with Genie AI integration and team-friendly distribution.
```

5. Click **"Publish release"**

## What Happens Next (Automatic!)

1. GitHub Actions workflow starts automatically
2. Builds your package
3. Publishes to PyPI (using trusted publishing - no tokens needed!)
4. In 2-3 minutes, your package is live at https://pypi.org/project/databricks-mcp-genie/

## Verify It Worked

### Check GitHub Actions

1. Go to https://github.com/sidart10/databricks-mcp-genie/actions
2. You should see "Publish to PyPI" workflow running
3. Wait for green checkmark ✅

### Check PyPI

1. Go to https://pypi.org/project/databricks-mcp-genie/
2. Your package should be live!

### Test Installation

```bash
# In a new terminal/environment
pip install databricks-mcp-genie

# Test it works
python -c "from databricks_mcp.server import DatabricksMCPServer; print('Success!')"
```

## Share with Your Team

Once published, send your team:

**Subject: New Tool - Databricks MCP for Cursor**

```
Hey team,

We now have one-click Databricks integration for Cursor!

Installation:
pip install databricks-mcp-genie

Setup guide: [link to your repo]/docs/CURSOR_SETUP.md

This gives you natural language querying, cluster management, SQL execution, and more - all directly in Cursor.

Let me know if you have any questions!
```

## Troubleshooting

### "Workflow not running"

- Check the Actions tab - is the workflow visible?
- Make sure the file is at `.github/workflows/publish.yml`
- Try creating the release again

### "Authentication failed"

- Did you click "Add" on the PyPI Trusted Publishers form?
- Are owner/repo/workflow names exactly correct?
- Wait a few minutes and try again (PyPI can be slow)

### "Environment 'pypi' not found"

Create it in GitHub:
1. Repo Settings → Environments
2. New environment → name it `pypi`

Or remove the environment section from `.github/workflows/publish.yml`

## Future Updates

To publish a new version:

1. Update `version = "1.0.1"` in `pyproject.toml`
2. Commit and push changes
3. Create new GitHub release with tag `v1.0.1`
4. Workflow automatically publishes to PyPI!

## Complete Checklist

- [ ] Fill in PyPI Trusted Publisher form and click "Add"
- [ ] Create GitHub repository `databricks-mcp-genie`
- [ ] Push code to GitHub
- [ ] Create GitHub release `v1.0.0`
- [ ] Wait for workflow to complete
- [ ] Verify package on PyPI
- [ ] Test installation: `pip install databricks-mcp-genie`
- [ ] Share with team

## You're Done!

Once you complete these steps, your team can install with:
```bash
pip install databricks-mcp-genie
```

See **GITHUB_PUBLISHING_GUIDE.md** for detailed explanations of each step.

---

**Need help?** Check the guides:
- `GITHUB_PUBLISHING_GUIDE.md` - Detailed publishing instructions
- `docs/CURSOR_SETUP.md` - Team installation guide
- `docs/DEPLOYMENT_SUMMARY.md` - Overview of the whole process

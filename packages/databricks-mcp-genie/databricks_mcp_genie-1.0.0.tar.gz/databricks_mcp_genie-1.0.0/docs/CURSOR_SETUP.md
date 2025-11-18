# Cursor Setup Guide for databricks-mcp-genie

Quick guide to install and configure the Databricks MCP Genie server for your team's Cursor IDE.

## Prerequisites

- Python 3.10 or higher
- Databricks workspace access
- Databricks personal access token
- Cursor IDE

## Installation Steps

### 1. Install the Package

Open your terminal and run:

```bash
pip install databricks-mcp-genie
```

Or if you need a specific Python version:

```bash
python3.10 -m pip install databricks-mcp-genie
# or
python3.11 -m pip install databricks-mcp-genie
```

### 2. Get Your Databricks Credentials

You'll need two things:

1. **Workspace URL**: Your Databricks workspace URL (e.g., `https://your-company.cloud.databricks.com`)
2. **Personal Access Token**:
   - Go to your Databricks workspace
   - Click your profile icon (top right)
   - Go to **User Settings** → **Developer** → **Access Tokens**
   - Click **Generate New Token**
   - Copy the token (you won't see it again!)

### 3. Configure Cursor

#### Find your Python path

First, find where pip installed the package:

```bash
which python3
# Example output: /usr/local/bin/python3
# or: /opt/homebrew/bin/python3
# or: ~/.pyenv/versions/3.11.0/bin/python3
```

Use this path in the next step.

#### Edit Cursor Settings

1. Open Cursor
2. Open **Settings** (Cmd+, on Mac, Ctrl+, on Windows/Linux)
3. Search for "MCP" or go to **Features** → **Model Context Protocol**
4. Click **Edit Config** or open the settings JSON file
5. Add the following configuration:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "databricks_mcp.main"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-personal-access-token-here"
      }
    }
  }
}
```

**Important**:
- Replace `/usr/local/bin/python3` with your actual Python path from step 3.1
- Replace `https://your-workspace.cloud.databricks.com` with your Databricks workspace URL
- Replace `your-personal-access-token-here` with your actual token

#### Optional: SQL Warehouse ID

If you want to use SQL execution tools without specifying warehouse ID each time:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "databricks_mcp.main"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-personal-access-token-here",
        "DATABRICKS_WAREHOUSE_ID": "your-warehouse-id-here"
      }
    }
  }
}
```

### 4. Restart Cursor

Close and reopen Cursor completely for the changes to take effect.

### 5. Verify Installation

In Cursor, try asking:

```
"List my Databricks clusters"
```

or

```
"Show me the available Genie AI spaces"
```

If you see results, you're all set!

## Troubleshooting

### "Command not found" or "Module not found"

**Problem**: Cursor can't find Python or the databricks_mcp module.

**Solution**:
1. Make sure you used the correct Python path in the config
2. Try using the full path to the module:
   ```bash
   # Find where the module is installed
   python3 -c "import databricks_mcp; print(databricks_mcp.__file__)"
   ```
3. You might need to use a virtual environment:
   ```bash
   python3 -m venv ~/databricks-mcp-env
   source ~/databricks-mcp-env/bin/activate
   pip install databricks-mcp-genie
   # Then use ~/databricks-mcp-env/bin/python3 in Cursor config
   ```

### "Authentication failed" or "Invalid token"

**Problem**: Databricks credentials are incorrect.

**Solution**:
1. Verify your workspace URL is correct (should start with `https://`)
2. Generate a new access token
3. Make sure there are no extra spaces in your token
4. Check the token hasn't expired

### "Connection timeout" or "Cannot connect"

**Problem**: Network or firewall issues.

**Solution**:
1. Verify you can access your Databricks workspace in a browser
2. Check if you're behind a corporate firewall/VPN
3. Make sure your workspace URL is accessible from your machine

### Server not showing up in Cursor

**Problem**: MCP server isn't loaded.

**Solution**:
1. Check Cursor's MCP logs (usually in Cursor's developer console)
2. Verify the JSON syntax in your config is correct (no trailing commas, proper quotes)
3. Completely quit Cursor (not just close the window) and restart

## Available Features

Once configured, you can ask Cursor to:

### Genie AI (Natural Language Queries)
- "Ask Genie: What were the top products by revenue last month?"
- "Use Genie to analyze customer churn trends"
- "Query Genie about sales by region"

### Cluster Management
- "List all my clusters"
- "Start cluster xyz"
- "Create a new cluster for testing"

### SQL Execution
- "Execute: SELECT * FROM catalog.schema.table LIMIT 10"
- "Run this query on my warehouse"

### Jobs & Notebooks
- "List my Databricks jobs"
- "Run notebook /Users/me/analysis"
- "Show recent job runs"

### Unity Catalog
- "List all catalogs"
- "Show tables in my_catalog.my_schema"
- "Get lineage for this table"

## Security Best Practices

1. **Never commit credentials**: Don't put tokens in code or git repositories
2. **Use workspace-level tokens**: Avoid personal admin tokens
3. **Rotate tokens regularly**: Generate new tokens periodically
4. **Limit token scope**: Use the minimum required permissions
5. **Team sharing**: Each team member should use their own token

## Team Distribution

Share this guide with your team along with:
1. Your Databricks workspace URL
2. Instructions on how to generate their own personal access token
3. Link to this package: `https://pypi.org/project/databricks-mcp-genie/`

## Support

- GitHub Issues: https://github.com/sidart10/databricks-mcp-genie/issues
- PyPI Package: https://pypi.org/project/databricks-mcp-genie/
- Full Documentation: See README.md in the repository

## Version

Current version: 1.0.0

Last updated: 2025-11-13

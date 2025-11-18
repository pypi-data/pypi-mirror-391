# Troubleshooting Guide - Databricks MCP Server

## Issue: "Failed to reconnect to databricks"

### ✅ Fixes Applied

1. **Fixed DATABRICKS_HOST** - Removed query parameters
   - ❌ Was: `https://dbc-992a5856-b2ed.cloud.databricks.com/?o=8589181270079680`
   - ✅ Now: `https://dbc-992a5856-b2ed.cloud.databricks.com`

2. **Fixed Python Path** - Using virtual environment Python
   - ❌ Was: `python3` (system Python missing dependencies)
   - ✅ Now: `/Users/sid/.../databricks-mcp/.venv/bin/python`

3. **Fixed Logging** - Changed from stdout to stderr
   - ❌ Was: `logging.StreamHandler(sys.stdout)` (breaks MCP protocol)
   - ✅ Now: `logging.StreamHandler(sys.stderr)` (MCP compatible)

### ✅ Verification Tests Passed

- ✅ Config loads successfully
- ✅ Databricks API connection works (HTTP 200 OK)
- ✅ Found 1 cluster in workspace
- ✅ Server module imports correctly
- ✅ FastMCP methods available
- ✅ Server starts and logs properly

## Current Configuration

### `.mcp.json`
```json
{
  "mcpServers": {
    "databricks": {
      "command": "/Users/sid/Desktop/4. Coding Projects/databrics-mcp-server/databricks-mcp/.venv/bin/python",
      "args": ["-m", "databricks_mcp.main"],
      "cwd": "/Users/sid/Desktop/4. Coding Projects/databrics-mcp-server/databricks-mcp",
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-databricks-token-here"
      }
    }
  }
}
```

## How to Test Connection

### Option 1: Restart Claude Desktop
1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. Check MCP status (should show "connected")

### Option 2: Check Server Manually
```bash
cd databricks-mcp
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-databricks-token-here"

# Test Python import
.venv/bin/python -c "from databricks_mcp.main import main; print('OK')"

# Test API connectivity
.venv/bin/python << 'EOF'
import os, asyncio
os.environ['DATABRICKS_HOST'] = 'https://your-workspace.cloud.databricks.com'
os.environ['DATABRICKS_TOKEN'] = 'your-databricks-token-here'
from databricks_mcp.api import clusters
async def test():
    result = await clusters.list_clusters()
    print(f"✓ Connected! Found {len(result.get('clusters', []))} clusters")
asyncio.run(test())
EOF
```

## Common Issues

### Issue: Module not found
**Problem**: Missing Python dependencies
**Solution**: Use the `.venv/bin/python` path in `.mcp.json`

### Issue: Authentication failed
**Problem**: Invalid token or host URL
**Solution**: Verify credentials:
- Token should start with `dapi`
- Host should NOT include `/?o=...` parameters
- Host should be just: `https://your-workspace.cloud.databricks.com`

### Issue: Server logs to stdout
**Problem**: Logging breaks MCP protocol
**Solution**: Already fixed - logs now go to stderr

### Issue: Connection works in terminal but not in Claude
**Problem**: Environment variables not set
**Solution**: Verify `.mcp.json` has `env` section with HOST and TOKEN

## Next Steps

**The server is configured correctly and ready to use!**

1. **Completely quit Claude Desktop** (⌘Q on Mac)
2. **Reopen Claude Desktop**
3. The Databricks server should now appear in the MCP list
4. Test by asking: "List my Databricks clusters"

If it still shows "failed to reconnect":
- Check Claude Desktop's MCP logs (if available)
- Verify the `.mcp.json` file hasn't been modified
- Ensure the `.venv` directory exists with dependencies installed

## Testing New Features

Once connected, try these commands:

### Basic Commands
- "List all Unity Catalogs"
- "Show me tables in the prod schema"
- "Describe the customers table"

### With New Enhancements
- "List catalogs in concise format"
- "Show table details with lineage"
- "Execute this SQL query: SELECT * FROM table LIMIT 10"

### Genie AI (if configured)
- "Ask Genie: What are the top 5 products?"

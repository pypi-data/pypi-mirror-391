#!/bin/bash
cd "/Users/sid/Desktop/4. Coding Projects/databrics-mcp-server/databricks-mcp"

export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-databricks-token-here"

echo "Starting server..."
.venv/bin/python -m databricks_mcp.main 2>&1 &
SERVER_PID=$!

sleep 3

if ps -p $SERVER_PID > /dev/null; then
   echo "✓ Server is running (PID: $SERVER_PID)"
   kill $SERVER_PID
   echo "✓ Server stopped"
else
   echo "✗ Server failed to start or crashed"
fi

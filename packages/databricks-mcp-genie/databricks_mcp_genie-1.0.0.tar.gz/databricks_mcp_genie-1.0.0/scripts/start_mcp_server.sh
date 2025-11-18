#!/bin/bash

set -euo pipefail

# Always run from the project root (one level up from this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR%/scripts}"
cd "$PROJECT_ROOT"

# Helper: check command availability
has_cmd() { command -v "$1" >/dev/null 2>&1; }

PYTHON_EXEC="python3"
has_cmd python3 || PYTHON_EXEC="python"

# Preferred: use existing venv if present
if [ -x ".venv/bin/python" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
  exec python -m databricks_mcp.server.databricks_mcp_server
fi

# Try creating venv with uv if available
if has_cmd uv; then
  echo "[databricks-mcp] Creating virtual environment with uv..." 1>&2
  if uv venv >/dev/null 2>&1; then
    echo "[databricks-mcp] Installing project (editable)..." 1>&2
    if uv pip install -e . >/dev/null 2>&1; then
      # shellcheck disable=SC1091
      source .venv/bin/activate
      exec python -m databricks_mcp.server.databricks_mcp_server
    fi
  fi
  echo "[databricks-mcp] uv path present but venv/setup failed; falling back to Python venv" 1>&2
fi

# Fallback: python -m venv
if "$PYTHON_EXEC" -m venv .venv >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
  # Best-effort install; ignore failures to allow PYTHONPATH fallback later
  pip install -e . >/dev/null 2>&1 || echo "[databricks-mcp] pip install failed; will try PYTHONPATH fallback" 1>&2
  exec python -m databricks_mcp.server.databricks_mcp_server
fi

# Last resort: run with system Python and project on PYTHONPATH
echo "[databricks-mcp] Running without venv; using system Python and PYTHONPATH" 1>&2
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON_EXEC" -m databricks_mcp.server.databricks_mcp_server
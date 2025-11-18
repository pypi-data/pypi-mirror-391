# Source Tree Analysis - Databricks MCP Server

## Project Structure

```
databricks-mcp-server/
├── databricks-mcp/                    # Main implementation directory
│   ├── databricks_mcp/                # Python package root
│   │   ├── __init__.py                # Package initialization
│   │   ├── __main__.py                # CLI entry point
│   │   ├── main.py                    # Main application entry (v0.3.1)
│   │   │
│   │   ├── api/                       # Databricks API integration modules
│   │   │   ├── clusters.py            # Cluster management (create, start, stop, resize)
│   │   │   ├── dbfs.py                # Databricks File System operations
│   │   │   ├── genie.py               # Genie AI natural language queries
│   │   │   ├── jobs.py                # Job management and execution
│   │   │   ├── libraries.py           # Library installation management
│   │   │   ├── notebooks.py           # Notebook operations
│   │   │   ├── repos.py               # Git repository integration
│   │   │   ├── sql.py                 # SQL execution with safety validation
│   │   │   ├── unity_catalog.py       # Unity Catalog basic operations
│   │   │   └── unity_catalog_enhanced.py  # Enhanced Unity Catalog features
│   │   │
│   │   ├── cli/                       # Command-line interface
│   │   │   └── commands.py            # CLI commands implementation
│   │   │
│   │   ├── core/                      # Core utilities and configuration
│   │   │   ├── auth.py                # Databricks authentication
│   │   │   ├── config.py              # Settings and environment configuration
│   │   │   ├── formatting.py          # Query result formatting (13KB)
│   │   │   ├── models.py              # Data models and type definitions
│   │   │   ├── sql_safety.py          # SQL safety validation for AI agents
│   │   │   └── utils.py               # HTTP utilities and API request handling
│   │   │
│   │   └── server/                    # MCP server implementation
│   │       ├── app.py                 # FastAPI application wrapper
│   │       ├── databricks_mcp_server.py  # Main MCP server (33KB, ~1000 lines)
│   │       └── __main__.py            # Server entry point
│   │
│   ├── tests/                         # Test suite
│   │   ├── test_clusters.py           # Cluster API tests
│   │   ├── test_jobs.py               # Jobs API tests
│   │   ├── test_direct.py             # Direct API tests
│   │   ├── test_mcp_client.py         # MCP client tests
│   │   └── test_additional_features.py  # Additional feature tests
│   │
│   ├── docs/                          # Project documentation
│   │   ├── AGENTS.md                  # Agent documentation
│   │   ├── CHANGELOG.md               # Version history
│   │   ├── new_features.md            # New features documentation
│   │   ├── phase1.md                  # Phase 1 roadmap
│   │   └── project_structure.md       # Project structure guide
│   │
│   ├── examples/                      # Usage examples
│   │   ├── direct_usage.py            # Direct API usage example
│   │   └── mcp_client_usage.py        # MCP client usage example
│   │
│   ├── scripts/                       # Utility scripts (20+ scripts)
│   │   ├── setup.sh / setup.ps1       # Environment setup scripts
│   │   ├── run_tests.sh / run_tests.ps1  # Test execution scripts
│   │   ├── start_mcp_server.sh / .ps1 # Server startup scripts
│   │   └── test_*.sh / test_*.ps1     # Various test scripts
│   │
│   ├── pyproject.toml                 # Python package configuration
│   ├── uv.lock                        # UV package lock file
│   ├── README.md                      # Main project documentation
│   ├── QUICK_START.md                 # Quick start guide
│   ├── ENHANCEMENTS.md                # Enhancement documentation
│   └── TROUBLESHOOTING.md             # Troubleshooting guide
│
├── docs/                              # Generated brownfield documentation (THIS LOCATION)
│   ├── bmm-workflow-status.yaml       # BMM workflow tracking
│   ├── project-scan-report.json       # Workflow state file
│   └── api-contracts.md               # API documentation (generated)
│
└── pyproject.toml                     # Root package configuration

```

## Critical Directories

### `/databricks_mcp/api/` - API Integration Layer
**Purpose:** Databricks REST API integration modules
**Key Files:**
- `clusters.py` - 7 functions for cluster lifecycle management
- `sql.py` - 5 functions including safety validation
- `genie.py` - 5 functions for AI-powered data analysis
- `unity_catalog_enhanced.py` - Enhanced catalog operations

**Integration Pattern:** All modules follow async/await pattern with `make_api_request()` utility

### `/databricks_mcp/core/` - Core Utilities
**Purpose:** Shared configuration, authentication, and utilities
**Key Components:**
- `config.py` - Environment variable management (DATABRICKS_HOST, TOKEN, WAREHOUSE_ID)
- `auth.py` - Databricks authentication handling
- `sql_safety.py` - Read-only SQL validation for AI agents
- `formatting.py` - Result formatting for MCP responses
- `utils.py` - HTTP request handling with error management

### `/databricks_mcp/server/` - MCP Server
**Purpose:** Model Context Protocol server implementation
**Entry Point:** `databricks_mcp_server.py` (33KB)
- Implements `FastMCP` base class
- Registers ~64 tools from API modules
- Handles stdio communication
- Parameter unwrapping for MCP clients

### `/tests/` - Test Suite
**Purpose:** pytest-asyncio test coverage
**Configuration:** `pyproject.toml` pytest settings
- Async test mode enabled
- Test discovery: `test_*.py`
- Coverage for clusters, jobs, direct API, MCP client

### `/scripts/` - Automation Scripts
**Purpose:** Development and testing utilities
**Cross-platform:** Both `.sh` (Unix) and `.ps1` (PowerShell) versions
- Environment setup
- Server startup
- Test execution
- Client testing

## Entry Points

### 1. MCP Server (Primary)
**File:** `databricks_mcp/server/databricks_mcp_server.py`
**Command:** `databricks-mcp-server` (from pyproject.toml scripts)
**Usage:** Stdio-based MCP protocol server

### 2. CLI Interface
**File:** `databricks_mcp/cli/commands.py`
**Command:** `databricks-mcp` (from pyproject.toml scripts)
**Usage:** Command-line tool for direct API access

### 3. Main Entry
**File:** `databricks_mcp/main.py`
**Purpose:** Application initialization and logging setup

## File Organization Patterns

### Module Naming Convention
- **API Modules:** `{resource}.py` (e.g., `clusters.py`, `sql.py`)
- **Core Modules:** `{function}.py` (e.g., `auth.py`, `config.py`)
- **Test Files:** `test_{module}.py`
- **Scripts:** `{action}_{purpose}.{sh|ps1}`

### Package Structure
- All directories contain `__init__.py` for Python package structure
- Server and CLI have dedicated `__main__.py` entry points
- Main package exports in root `__init__.py`

## Asset Locations

### Configuration Files
- `pyproject.toml` - Python package metadata and dependencies
- `.env.example` - Environment variable template
- `uv.lock` - Dependency lock file

### Documentation
- `/docs/` (this location) - All project documentation (brownfield analysis + original technical docs)
- Root level: README.md, QUICK_START.md, TROUBLESHOOTING.md, ENHANCEMENTS.md

### Logs
- `databricks_mcp.log` - Server runtime logs (configured in server.py)
- `local_mcp_stderr.log` - Local test error logs
- `local_mcp_stderr2.log` - Additional test logs

## Key Integration Points

### 1. API → Core
All API modules import from `core`:
```python
from databricks_mcp.core.utils import make_api_request
from databricks_mcp.core.config import settings
```

### 2. Server → API
Server imports all API modules:
```python
from databricks_mcp.api import clusters, sql, genie, jobs, ...
```

### 3. Tests → API + Server
Tests import both API modules and server for integration testing

## Build and Deployment

**Build System:** Hatchling (PEP 517)
**Package Name:** `databricks-mcp-server`
**Version:** 0.3.1
**Python:** >=3.10

**Installation:**
```bash
pip install databricks-mcp-server
# or
uvx databricks-mcp-server
```

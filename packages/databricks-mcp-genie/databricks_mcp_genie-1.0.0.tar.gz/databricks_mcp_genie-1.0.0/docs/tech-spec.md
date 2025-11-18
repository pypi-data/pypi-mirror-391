# databrics-mcp-server - Technical Specification

**Author:** Sid
**Date:** 2025-11-12
**Project Level:** Level 1 (Coherent Feature)
**Change Type:** Reorganization + Bug Fixes
**Development Context:** Brownfield - Fixing and restructuring existing MCP server

---

## Context

### Available Documents

**Brownfield Documentation:**
- ✅ docs/index.md - AI-assisted development entry point with complete codebase overview
- ✅ docs/project-overview.md - Executive summary, tech stack (Python 3.10+, FastMCP, databricks-sdk)
- ✅ docs/api-contracts.md - All 64 async API functions documented across 10 modules
- ✅ docs/source-tree-analysis.md - Complete directory structure with critical folder annotations

**Existing Project Documentation:**
- databricks-mcp/README.md - Main project documentation
- databricks-mcp/QUICK_START.md - Quick start guide
- databricks-mcp/TROUBLESHOOTING.md - Common issues and solutions
- databricks-mcp/ENHANCEMENTS.md - Enhancement tracking

### Project Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | >=3.10 | Core implementation |
| **Protocol** | MCP | >=1.2.0 | Model Context Protocol |
| **Framework** | FastMCP | - | MCP server framework |
| **SDK** | databricks-sdk | latest | Databricks API integration |
| **HTTP** | httpx | latest | Async HTTP client |
| **CLI** | click | latest | Command-line interface |
| **Testing** | pytest + pytest-asyncio | latest | Async test framework |
| **Code Quality** | black, pylint | latest | Linting and formatting |
| **Build** | hatchling | latest | PEP 517 build backend |

**Architecture Pattern:** Layered Backend
- API Layer: 10 modules with ~64 async functions
- Core Layer: Auth, config, utilities, SQL safety
- Server Layer: MCP protocol implementation
- CLI Layer: Command-line interface

### Existing Codebase Structure

**Repository Type:** Monolith (single cohesive Python backend)

**Current Structure After Partial Move:**
```
root/
├── databricks_mcp/          # ✅ MOVED - Source code at root
│   ├── api/                 # 10 API modules
│   ├── core/                # 6 utility modules
│   ├── server/              # MCP server implementation
│   └── cli/                 # CLI commands
├── tests/                   # ✅ MOVED - Test suite at root
├── examples/                # ✅ MOVED - Examples at root
├── scripts/                 # ✅ MOVED - Scripts at root
├── .venv/                   # ❌ BROKEN - Points to old path
├── pyproject.toml           # ✅ At root (but duplicate exists)
├── .mcp.json                # ❌ BROKEN - Points to old paths
└── databricks-mcp/          # ❌ ORPHANED FOLDER
    ├── README.md            # Should be at root
    ├── QUICK_START.md       # Should be at root
    ├── TROUBLESHOOTING.md   # Should be at root
    ├── ENHANCEMENTS.md      # Should be at root
    ├── docs/                # Orphaned docs folder
    ├── pyproject.toml       # Duplicate
    ├── uv.lock              # Duplicate
    └── test_server.sh       # Utility script
```

**Detected Code Conventions:**
- **Style:** PEP 8 compliant (black formatting)
- **Async:** All API functions use async/await pattern
- **Imports:** Absolute imports from `databricks_mcp.*`
- **Error Handling:** Custom `DatabricksAPIError` exception class
- **Logging:** Python logging module with stderr output for MCP compatibility
- **Testing:** pytest with `test_*.py` naming convention
- **Docstrings:** Google-style docstrings for all functions

---

## The Change

### Problem Statement

The Databricks MCP Server has been partially reorganized from a nested structure (`/databricks-mcp/`) to a root-level structure, but the reorganization is incomplete and has broken the server's functionality. Critical issues include:

1. **Non-functional MCP server** - Cannot start due to broken virtual environment and outdated configuration paths
2. **Broken virtual environment** - venv symlinks point to old `/databricks-mcp/.venv/` location that no longer exists
3. **Outdated MCP configuration** - `.mcp.json` references old paths preventing Claude Desktop/MCP client integration
4. **Incomplete reorganization** - Documentation files (README, QUICK_START, etc.) remain in old `/databricks-mcp/` folder
5. **Duplicate configuration** - pyproject.toml and uv.lock exist in both locations creating ambiguity
6. **Non-standard structure** - Missing root README violates MCP server best practices

Additionally, **no verification exists** that all 64 MCP tools are actually functional after the move.

### Proposed Solution

**Complete the reorganization to proper MCP server structure with full verification:**

1. **Create fresh virtual environment** at root with correct paths
2. **Move all documentation** to root (README, QUICK_START, TROUBLESHOOTING, ENHANCEMENTS)
3. **Consolidate configuration** - Remove duplicates, keep only root versions
4. **Update .mcp.json** with correct paths for root-level execution
5. **Remove orphaned `/databricks-mcp/` folder** entirely after moving everything useful
6. **Install dependencies** in new venv and verify imports work
7. **Run comprehensive test suite** to verify all functionality intact
8. **Test all MCP tools** manually to ensure end-to-end functionality
9. **Update brownfield documentation** to reflect new structure

### Scope

**In Scope:**

- ✅ Create new virtual environment at root
- ✅ Move README, QUICK_START, TROUBLESHOOTING, ENHANCEMENTS to root
- ✅ Consolidate pyproject.toml and uv.lock (keep root versions)
- ✅ Update .mcp.json configuration with correct paths
- ✅ Remove `/databricks-mcp/` folder after migration
- ✅ Install all dependencies (mcp, httpx, databricks-sdk, pytest, etc.)
- ✅ Run full pytest suite and verify all tests pass
- ✅ Test MCP server startup and tool registration
- ✅ Verify all 64 MCP tools are accessible and functional
- ✅ Update generated documentation (docs/*.md) to reflect new structure
- ✅ Create comprehensive testing checklist for all API modules

**Out of Scope:**

- ❌ Adding new features or API endpoints
- ❌ Refactoring existing code logic
- ❌ Changing MCP protocol implementation
- ❌ Upgrading dependencies to newer versions
- ❌ Performance optimization
- ❌ Adding new documentation beyond reorganization updates

---

## Implementation Details

### Source Tree Changes

**Files to MOVE (from databricks-mcp/ to root):**

1. `databricks-mcp/README.md` → `README.md` - MOVE - Main project documentation
2. `databricks-mcp/QUICK_START.md` → `QUICK_START.md` - MOVE - Quick start guide
3. `databricks-mcp/TROUBLESHOOTING.md` → `TROUBLESHOOTING.md` - MOVE - Troubleshooting guide
4. `databricks-mcp/ENHANCEMENTS.md` → `ENHANCEMENTS.md` - MOVE - Enhancement tracking
5. `databricks-mcp/test_server.sh` → `test_server.sh` - MOVE (if not already at root) - Test utility

**Files to DELETE (duplicates or obsolete):**

1. `databricks-mcp/pyproject.toml` - DELETE - Duplicate (keep root version)
2. `databricks-mcp/uv.lock` - DELETE - Duplicate (keep root version)
3. `databricks-mcp/local_mcp_stderr.log` - DELETE - Old log file
4. `databricks-mcp/local_mcp_stderr2.log` - DELETE - Old log file
5. `databricks-mcp/docs/` - DELETE - Orphaned docs (already have /docs/ at root)
6. `.venv/` - DELETE - Broken virtual environment

**Folders to REMOVE:**

1. `databricks-mcp/` - DELETE - Entire folder after moving useful files

**Files to CREATE:**

1. `.venv/` - CREATE - Fresh virtual environment at root
2. `README.md` - UPDATE - Paths corrected for root-level structure

**Files to MODIFY:**

1. `.mcp.json` - MODIFY - Update all paths to point to root structure
2. `docs/index.md` - MODIFY - Update file path references
3. `docs/source-tree-analysis.md` - MODIFY - Update directory structure documentation
4. `docs/project-overview.md` - MODIFY - Update installation and structure info

### Technical Approach

**Phase 1: Environment Reconstruction**
- Delete broken `.venv/` directory completely
- Create fresh virtual environment using Python 3.13 (system Python): `python3 -m venv .venv`
- Activate venv and upgrade pip: `.venv/bin/pip install --upgrade pip`
- Install package in editable mode: `.venv/bin/pip install -e .`
- This installs all dependencies from `pyproject.toml` including mcp[cli], httpx, databricks-sdk
- Install dev dependencies: `.venv/bin/pip install -e ".[dev]"`

**Phase 2: File Consolidation**
- Move documentation files from `databricks-mcp/` to root using shell commands
- Compare and verify pyproject.toml files are identical before deleting duplicate
- Remove duplicate configuration files
- Delete entire `databricks-mcp/` directory after verification

**Phase 3: Configuration Updates**
- Update `.mcp.json` paths:
  - `command`: Point to new `.venv/bin/python` at root
  - `cwd`: Set to project root directory
  - `args`: Keep as `-m databricks_mcp.main` (entry point unchanged)
- Verify `.env.example` is at root with correct template

**Phase 4: Verification & Testing**
- Import test: `python3 -m databricks_mcp.server --help` (verify no import errors)
- Run pytest suite: `.venv/bin/pytest tests/ -v`
- Start MCP server and verify stdio communication
- Test tool registration by listing available tools
- Manually test key tools from each API module:
  - Clusters: list_clusters
  - SQL: execute_safe_statement
  - Genie: list_genie_spaces
  - Jobs: list_jobs
  - Notebooks: list_notebooks

**Phase 5: Documentation Updates**
- Update all path references in `/docs/*.md` files
- Remove references to `/databricks-mcp/` nested structure
- Update installation instructions to reflect root-level structure

### Existing Patterns to Follow

**Python Code Patterns (from brownfield analysis):**

1. **Async/Await Pattern:**
   ```python
   async def api_function(param: str) -> Dict[str, Any]:
       """Google-style docstring"""
       logger.info(f"Action: {param}")
       return await make_api_request("METHOD", "/endpoint", data={...})
   ```

2. **MCP Tool Registration Pattern:**
   ```python
   @self.tool(
       name="tool_name",
       description="Tool description with parameters"
   )
   async def tool_function(params: Dict[str, Any]) -> List[TextContent]:
       actual_params = _unwrap_params(params)
       result = await api_module.function(actual_params)
       return [{"type": "text", "text": json.dumps(result)}]
   ```

3. **Error Handling:**
   - Use `DatabricksAPIError` from `core/utils.py`
   - Log errors before raising
   - Return structured error responses in JSON

4. **Import Organization:**
   - Standard library imports first
   - Third-party imports second
   - Local imports last
   - Absolute imports: `from databricks_mcp.core.utils import ...`

5. **Logging:**
   - Configure logger at module level: `logger = logging.getLogger(__name__)`
   - Log to stderr for MCP compatibility
   - Use appropriate log levels (INFO for operations, ERROR for failures)

**Testing Patterns:**
- Test file naming: `test_{module}.py`
- Location: `/tests/` directory at root
- Framework: pytest with pytest-asyncio
- Async test functions: `async def test_function_name()`
- Configuration: `pyproject.toml` [tool.pytest.ini_options]

**File Organization:**
- Package root: `databricks_mcp/`
- All modules have `__init__.py`
- Entry points in `__main__.py` files
- Configuration in project root

### Integration Points

**Internal Module Dependencies:**
- All API modules (`api/*.py`) → `core/utils.make_api_request()`
- All API modules → `core/config.settings` for environment variables
- Server (`server/databricks_mcp_server.py`) → All API modules (imports and registers as tools)
- SQL API → `core/sql_safety.check_sql_safety()` for validation
- Main entry (`main.py`) → `server/databricks_mcp_server.DatabricksMCPServer`

**External Dependencies:**
- MCP Client → Server via stdio protocol
- Server → Databricks REST API via httpx
- Configuration → Environment variables (DATABRICKS_HOST, TOKEN, WAREHOUSE_ID)

**No database, no state management** - stateless API server

---

## Development Context

### Relevant Existing Code

**Key Files to Reference:**

1. **Server Implementation:**
   - `databricks_mcp/server/databricks_mcp_server.py:1-1000` - Main MCP server with tool registration
   - `databricks_mcp/server/__main__.py:1-20` - Server entry point
   - `databricks_mcp/main.py:1-70` - Application initialization and logging

2. **API Patterns:**
   - `databricks_mcp/api/clusters.py:14-133` - Reference implementation for async API functions
   - `databricks_mcp/api/sql.py:16-242` - Example with safety validation and polling
   - `databricks_mcp/api/genie.py:34-285` - Complex polling pattern with conversation state

3. **Core Utilities:**
   - `databricks_mcp/core/utils.py` - HTTP request handling with `make_api_request()` utility
   - `databricks_mcp/core/config.py` - Settings class with environment variable management
   - `databricks_mcp/core/sql_safety.py` - SQL validation for read-only enforcement

4. **Testing Examples:**
   - `tests/test_clusters.py` - Unit tests for cluster API
   - `tests/test_mcp_client.py` - MCP client integration tests

### Dependencies

**Framework/Libraries (from pyproject.toml):**

**Production:**
- `mcp[cli]>=1.2.0` - Model Context Protocol framework
- `httpx` - Async HTTP client for Databricks API calls
- `databricks-sdk` - Official Databricks Python SDK

**CLI Optional:**
- `click` - Command-line interface framework

**Development:**
- `black` - Code formatter
- `pylint` - Linter
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `fastapi` - API framework (dev dependency)
- `anyio` - Async compatibility layer
- `build>=1.2.2.post1` - Build tool
- `twine>=6.1.0` - Package upload tool

**Internal Modules:**

All API modules depend on:
- `databricks_mcp.core.utils` (make_api_request, DatabricksAPIError)
- `databricks_mcp.core.config` (settings object)

Server depends on:
- All 10 API modules in `databricks_mcp.api.*`
- `mcp.server.FastMCP` base class
- `mcp.types.TextContent` for responses

### Configuration Changes

**Files to Update:**

1. **`.mcp.json`** - MCP client configuration
   ```json
   {
     "mcpServers": {
       "databricks": {
         "command": "/Users/sid/Desktop/4. Coding Projects/databrics-mcp-server/.venv/bin/python",
         "args": ["-m", "databricks_mcp.main"],
         "cwd": "/Users/sid/Desktop/4. Coding Projects/databrics-mcp-server",
         "env": {
           "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
           "DATABRICKS_TOKEN": "your-databricks-token-here"
         }
       }
     }
   }
   ```
   Changes: Update `command` to new venv path, update `cwd` to root

2. **Environment Variables** - Already configured in `.mcp.json` env section
   - DATABRICKS_HOST: Points to workspace
   - DATABRICKS_TOKEN: Personal access token
   - (DATABRICKS_WAREHOUSE_ID optional, can be provided per-tool)

3. **No changes needed to:**
   - pyproject.toml structure (already correct at root)
   - Python import paths (still `databricks_mcp.*`)
   - Test configuration (already correct)

### Existing Conventions (Brownfield)

**Code Style:**
- **Formatting:** black (automated PEP 8 compliance)
- **Linting:** pylint for code quality
- **Indentation:** 4 spaces (Python standard)
- **Line length:** black default (88 characters)
- **Quotes:** Double quotes for strings
- **Imports:** Organized in standard library, third-party, local order

**Naming Conventions:**
- **Functions:** snake_case (e.g., `list_clusters`, `execute_statement`)
- **Classes:** PascalCase (e.g., `DatabricksMCPServer`, `DatabricksAPIError`)
- **Files:** snake_case (e.g., `databricks_mcp_server.py`, `sql_safety.py`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `GENIE_POLL_INTERVAL`)

**Async Patterns:**
- All API functions are `async def`
- Use `await` for all API calls
- Polling loops use `asyncio.sleep()`
- Return `Dict[str, Any]` for API responses

**Error Handling:**
- Custom exceptions: `DatabricksAPIError`, `SQLSafetyError`
- Log before raising: `logger.error(f"...")`  then `raise`
- Include context in exception messages

**Testing Conventions:**
- File naming: `test_{module}.py`
- Function naming: `async def test_{function_name}()`
- Use pytest fixtures for setup
- Async tests with `pytest-asyncio`

### Test Framework & Standards

**Framework:** pytest 7.x with pytest-asyncio plugin

**Configuration (from pyproject.toml):**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

**Test Standards:**
- All async functions must have async tests
- Use descriptive test names indicating what's being tested
- Test both success and error paths
- Mock external API calls (Databricks API)
- Coverage target: Aim for >80% coverage on critical paths

**Existing Test Files:**
- `tests/test_clusters.py` - Cluster API tests
- `tests/test_jobs.py` - Jobs API tests
- `tests/test_direct.py` - Direct API call tests
- `tests/test_mcp_client.py` - MCP client integration tests
- `tests/test_additional_features.py` - Additional feature coverage

---

## Implementation Stack

**Runtime Environment:**
- Python 3.13.2 (system Python on macOS)
- Virtual environment: `.venv/` at project root

**Core Stack (from pyproject.toml dependencies):**
- mcp[cli] >= 1.2.0 - Model Context Protocol framework
- httpx (latest) - Async HTTP client
- databricks-sdk (latest) - Databricks Python SDK
- click (latest) - CLI framework

**Development Stack:**
- pytest (latest) - Test framework
- pytest-asyncio (latest) - Async test support
- black (latest) - Code formatting
- pylint (latest) - Code linting
- fastapi (latest) - Dev dependency
- anyio (latest) - Async compatibility

**Build & Package:**
- hatchling - PEP 517 build backend
- build >= 1.2.2.post1 - Build tool
- twine >= 6.1.0 - Package publishing

**Version Control:**
- Git repository initialized
- .gitignore configured (excludes .venv, __pycache__, .env, etc.)

---

## Technical Details

### Root Cause Analysis

**Issue #1: Broken Virtual Environment**
- **Cause:** venv created at `/databricks-mcp/.venv` before file move
- **Symptom:** `pyvenv.cfg` contains `command = ... -m venv /Users/sid/.../databricks-mcp/.venv`
- **Impact:** All pip/python executables have broken shebang lines pointing to non-existent path
- **Fix:** Delete and recreate venv at correct root location

**Issue #2: Outdated MCP Configuration**
- **Cause:** `.mcp.json` not updated after reorganization
- **Current values:**
  - `command`: `/databricks-mcp/.venv/bin/python` (broken path)
  - `cwd`: `/databricks-mcp` (wrong directory)
- **Impact:** MCP clients (Claude Desktop, etc.) cannot start server
- **Fix:** Update paths to root-level locations

**Issue #3: Incomplete File Migration**
- **Cause:** Documentation files left in `/databricks-mcp/` during move
- **Impact:** Non-standard structure, missing root README
- **Fix:** Move all user-facing docs to root, delete old folder

**Issue #4: Duplicate Configuration**
- **Cause:** pyproject.toml exists in both locations
- **Impact:** Ambiguity about which config is authoritative
- **Fix:** Keep root version, delete `/databricks-mcp/pyproject.toml`

### MCP Server Best Practices (Compliance)

**Required Structure:**
```
project-root/
├── README.md                 # Required - Project documentation
├── pyproject.toml            # Required - Package configuration
├── .env.example              # Required - Environment template
├── {package_name}/           # Required - Source code package
│   ├── __init__.py
│   ├── server/               # MCP server implementation
│   └── ...
├── tests/                    # Recommended - Test suite
├── examples/                 # Recommended - Usage examples
└── .venv/                    # Recommended - Virtual environment
```

**MCP Configuration Requirements:**
- `.mcp.json` with correct command path (absolute recommended)
- Working directory should be project root
- Environment variables properly configured
- Server must start via stdio mode

### Verification Strategy

**Level 1: Import Verification**
```bash
# Verify package imports work
.venv/bin/python -c "from databricks_mcp.server import DatabricksMCPServer; print('Import successful')"
.venv/bin/python -c "from databricks_mcp.api import clusters, sql, genie; print('API imports successful')"
```

**Level 2: Server Startup**
```bash
# Verify server can start (will hang waiting for stdio - that's correct)
timeout 3s .venv/bin/python -m databricks_mcp.main || echo "Server started successfully"
```

**Level 3: Test Suite**
```bash
# Run all tests
.venv/bin/pytest tests/ -v

# Expected: All tests pass or skip (no failures)
```

**Level 4: MCP Tool Verification**
- Use MCP Inspector or client to list available tools
- Verify all ~64 tools are registered
- Test representative tool from each module

---

## Development Setup

### Prerequisites

- Python 3.10 or higher (system has Python 3.13.2)
- Git (for version control)
- Databricks workspace access (with host URL and personal access token)
- Optional: Databricks SQL Warehouse ID for SQL operations

### Installation Steps

```bash
# 1. Navigate to project root
cd /Users/sid/Desktop/4.\ Coding\ Projects/databrics-mcp-server

# 2. Create fresh virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install package in editable mode (installs all dependencies)
pip install -e .

# 6. Install development dependencies
pip install -e ".[dev]"

# 7. Verify installation
python -c "from databricks_mcp.server import DatabricksMCPServer"
```

### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Databricks credentials
# Required:
#   DATABRICKS_HOST=https://your-workspace.databricks.com
#   DATABRICKS_TOKEN=your-personal-access-token
# Optional:
#   DATABRICKS_WAREHOUSE_ID=your-warehouse-id
```

### Running the Server

```bash
# Start MCP server (stdio mode)
python -m databricks_mcp.main

# Or use installed command
databricks-mcp-server

# Or use CLI for direct testing
databricks-mcp list-clusters
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_clusters.py

# Run with coverage
pytest --cov=databricks_mcp --cov-report=html
```

---

## Implementation Guide

### Setup Steps

**Pre-Implementation Checklist:**

1. ✅ Verify current working directory is project root
2. ✅ Backup `/databricks-mcp/` folder contents (optional safety measure)
3. ✅ Ensure no running processes using old venv
4. ✅ Document current `.mcp.json` configuration (for reference)
5. ✅ Create feature branch: `git checkout -b fix/reorganize-to-root-structure`

### Implementation Steps

**Story 1: Environment Reconstruction**

1. Delete broken virtual environment
   ```bash
   rm -rf .venv
   ```

2. Create fresh venv at root
   ```bash
   python3 -m venv .venv
   ```

3. Activate and upgrade pip
   ```bash
   source .venv/bin/activate
   pip install --upgrade pip
   ```

4. Install package and dependencies
   ```bash
   pip install -e .
   pip install -e ".[dev]"
   ```

5. Verify imports work
   ```bash
   python -c "from databricks_mcp.server import DatabricksMCPServer; print('✓ Imports working')"
   ```

**Story 2: File Consolidation & Cleanup**

1. Move documentation files to root
   ```bash
   mv databricks-mcp/README.md ./README.md
   mv databricks-mcp/QUICK_START.md ./QUICK_START.md
   mv databricks-mcp/TROUBLESHOOTING.md ./TROUBLESHOOTING.md
   mv databricks-mcp/ENHANCEMENTS.md ./ENHANCEMENTS.md
   ```

2. Move test_server.sh if not already at root
   ```bash
   test -f test_server.sh || mv databricks-mcp/test_server.sh ./
   ```

3. Verify pyproject.toml files are identical
   ```bash
   diff pyproject.toml databricks-mcp/pyproject.toml
   ```
   - If identical: safe to delete duplicate
   - If different: merge changes into root version

4. Delete duplicate files and orphaned folder
   ```bash
   rm -rf databricks-mcp/
   ```

5. Verify root structure is complete
   ```bash
   ls -la  # Should see: README.md, databricks_mcp/, tests/, .venv/, pyproject.toml
   ```

**Story 3: Configuration Updates & Verification**

1. Update `.mcp.json` with correct paths
   ```json
   {
     "mcpServers": {
       "databricks": {
         "command": "/Users/sid/Desktop/4. Coding Projects/databrics-mcp-server/.venv/bin/python",
         "args": ["-m", "databricks_mcp.main"],
         "cwd": "/Users/sid/Desktop/4. Coding Projects/databrics-mcp-server",
         "env": {
           "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
           "DATABRICKS_TOKEN": "your-databricks-token-here"
         }
       }
     }
   }
   ```

2. Test server startup (import verification)
   ```bash
   timeout 3s .venv/bin/python -m databricks_mcp.main
   # Expected: Timeout (server waiting for stdio input - this is correct!)
   # If errors: Import or path issues need fixing
   ```

3. Run pytest suite
   ```bash
   .venv/bin/pytest tests/ -v
   ```
   - Document any test failures
   - Fix import errors if present

4. Test MCP tool registration
   ```bash
   # Use MCP Inspector or test client to list tools
   # Verify ~64 tools registered across all API modules
   ```

5. Update generated documentation paths
   - Edit `docs/index.md` - Remove `/databricks-mcp/` path references
   - Edit `docs/source-tree-analysis.md` - Update directory structure
   - Edit `docs/project-overview.md` - Update installation paths

### Testing Strategy

**Phase 1: Smoke Tests (Verify Nothing Broke)**

1. **Import Tests:**
   ```bash
   python -c "from databricks_mcp.server import DatabricksMCPServer"
   python -c "from databricks_mcp.api import clusters, sql, genie"
   python -c "from databricks_mcp.core import config, utils"
   ```
   - Expected: No ImportError

2. **Entry Point Test:**
   ```bash
   python -m databricks_mcp.main --help 2>&1
   ```
   - Expected: Help text or server initialization (not ModuleNotFoundError)

**Phase 2: Automated Test Suite**

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=databricks_mcp --cov-report=term
```

**Expected Results:**
- All tests pass or skip (acceptable)
- No ImportError or ModuleNotFoundError
- Coverage >70% (existing baseline)

**Phase 3: MCP Integration Tests**

1. **Server Startup Test:**
   ```bash
   # Server should start and wait for stdio input
   timeout 3s python -m databricks_mcp.main
   # Exit code 124 (timeout) = SUCCESS
   # Any other error = FAILURE
   ```

2. **Tool Registration Test:**
   - Start server with MCP client
   - Call `tools/list` to enumerate all tools
   - Verify count: ~64 tools registered
   - Verify modules covered: clusters, sql, genie, jobs, notebooks, dbfs, unity_catalog, repos, libraries

3. **Representative Tool Tests (one per module):**
   - **Clusters:** `list_clusters` - Should list clusters or return empty array
   - **SQL:** `execute_safe_statement` - Should validate SQL safety
   - **Genie:** `list_genie_spaces` - Should list available spaces
   - **Jobs:** `list_jobs` - Should list jobs
   - **Notebooks:** `list` - Should list notebooks

**Phase 4: End-to-End Verification**

Test complete workflow using MCP client:
```
1. Connect to server via .mcp.json configuration
2. List available tools
3. Execute sample tool (e.g., list_clusters)
4. Verify response format is correct
5. Confirm no errors in logs
```

### Acceptance Criteria

**Environment & Structure:**
1. ✅ Virtual environment exists at `.venv/` and is functional
2. ✅ All dependencies installed successfully (mcp, httpx, databricks-sdk)
3. ✅ README.md exists at project root
4. ✅ No `/databricks-mcp/` folder exists (completely removed)
5. ✅ pyproject.toml exists only at root (no duplicates)
6. ✅ All documentation files (README, QUICK_START, TROUBLESHOOTING, ENHANCEMENTS) at root

**Configuration:**
1. ✅ `.mcp.json` points to correct venv path at root
2. ✅ `.mcp.json` working directory is project root
3. ✅ `.mcp.json` environment variables configured
4. ✅ `.env.example` exists at root with template

**Functionality:**
1. ✅ Server starts without ImportError: `python -m databricks_mcp.main`
2. ✅ All Python imports resolve correctly (no ModuleNotFoundError)
3. ✅ pytest suite runs and all tests pass or skip (no failures)
4. ✅ MCP server registers all ~64 tools successfully
5. ✅ Server communicates via stdio protocol correctly
6. ✅ At least one tool from each API module verified functional:
   - Clusters API: list_clusters works
   - SQL API: execute_safe_statement works
   - Genie API: list_genie_spaces works
   - Jobs API: list_jobs works
   - Notebooks API: list works
   - DBFS API: list works
   - Unity Catalog API: list_schemas works
   - Repos API: list works
   - Libraries API: cluster_status works

**Documentation:**
1. ✅ `docs/index.md` updated with correct paths (no /databricks-mcp/ references)
2. ✅ `docs/source-tree-analysis.md` reflects new root structure
3. ✅ `docs/project-overview.md` has correct installation instructions
4. ✅ All path references in documentation are accurate

**Quality Gates:**
1. ✅ No broken imports
2. ✅ No broken file paths
3. ✅ No duplicate configuration
4. ✅ Follows MCP server best practices
5. ✅ All tests passing
6. ✅ Documentation accurate

---

## Developer Resources

### File Paths Reference

**Files to MOVE:**
- `databricks-mcp/README.md` → `README.md`
- `databricks-mcp/QUICK_START.md` → `QUICK_START.md`
- `databricks-mcp/TROUBLESHOOTING.md` → `TROUBLESHOOTING.md`
- `databricks-mcp/ENHANCEMENTS.md` → `ENHANCEMENTS.md`
- `databricks-mcp/test_server.sh` → `test_server.sh` (if not exists)

**Files to DELETE:**
- `.venv/` (entire directory - broken)
- `databricks-mcp/` (entire directory after moving useful files)

**Files to CREATE:**
- `.venv/` (fresh virtual environment at root)

**Files to MODIFY:**
- `.mcp.json` (update command, cwd paths)
- `docs/index.md` (update path references)
- `docs/source-tree-analysis.md` (update directory tree)
- `docs/project-overview.md` (update installation instructions)

### Key Code Locations

**No code changes required** - This is purely reorganization and environment fixes.

**Key configuration locations:**
- Package metadata: `pyproject.toml:1-69` (at root)
- MCP config: `.mcp.json:1-15` (needs path updates)
- Server entry: `databricks_mcp/main.py:39-70` (unchanged)
- MCP server: `databricks_mcp/server/databricks_mcp_server.py:52-700` (unchanged)

### Testing Locations

**Test Suite (already at root):**
- Unit tests: `tests/test_*.py`
- Test configuration: `pyproject.toml:56-62` [tool.pytest.ini_options]
- Test README: `tests/README.md`

**Test Commands:**
```bash
# All tests
pytest

# Specific module
pytest tests/test_clusters.py

# With coverage
pytest --cov=databricks_mcp

# Verbose
pytest -v
```

### Documentation to Update

**Generated Documentation (in /docs/):**

1. **docs/index.md**
   - Lines 49-63: Remove references to `../databricks-mcp/` paths
   - Update to reference root-level files: `../README.md`, `../QUICK_START.md`, etc.

2. **docs/source-tree-analysis.md**
   - Lines 1-100: Update directory tree to show root-level structure
   - Remove nested `databricks-mcp/` wrapper
   - Update paths to reflect `databricks_mcp/` at root

3. **docs/project-overview.md**
   - Lines 112-124: Update installation instructions
   - Remove nested directory references
   - Update "From source" section to reflect root structure

**Existing Documentation (after move):**
- `README.md` - Update if any paths reference old structure
- `QUICK_START.md` - Update paths if needed
- `TROUBLESHOOTING.md` - Update paths if needed

---

## UX/UI Considerations

No UI/UX impact - This is purely backend infrastructure and reorganization work.

**User-facing changes:**
- Installation path changes in documentation
- MCP configuration updates for Claude Desktop users
- Otherwise identical functionality

---

## Testing Approach

### Test Framework

**Framework:** pytest 7.x with pytest-asyncio

**Configuration:**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### Test Strategy

**Unit Tests (via pytest):**
- All existing tests in `tests/` directory
- Tests for: clusters, jobs, SQL, MCP client integration
- Run with: `pytest tests/ -v`

**Integration Tests:**
- MCP client tests (`tests/test_mcp_client.py`)
- Direct API tests (`tests/test_direct.py`)
- Verify end-to-end tool execution

**Manual Verification Tests:**
- Server startup: `timeout 3s python -m databricks_mcp.main`
- Import verification: Python import statements
- Tool enumeration: MCP Inspector or client

**Coverage Requirements:**
- Target: >80% for critical paths
- Use: `pytest --cov=databricks_mcp --cov-report=html`
- Review: Coverage report in htmlcov/index.html

### Test Execution Checklist

**Story 1 Tests: Environment Reconstruction**
- [ ] Virtual environment created successfully
- [ ] Pip upgraded without errors
- [ ] All dependencies installed (verify with `pip list`)
- [ ] Package installed in editable mode
- [ ] Import test passes: `python -c "from databricks_mcp.server import DatabricksMCPServer"`

**Story 2 Tests: File Consolidation**
- [ ] All docs moved to root (README, QUICK_START, etc.)
- [ ] No duplicate pyproject.toml files
- [ ] /databricks-mcp/ folder deleted
- [ ] Root structure matches MCP best practices

**Story 3 Tests: Configuration & Verification**
- [ ] .mcp.json updated with correct paths
- [ ] Server starts without ModuleNotFoundError
- [ ] pytest suite completes (all pass or skip, no failures)
- [ ] All ~64 MCP tools registered
- [ ] Sample tools from each module execute successfully
- [ ] Documentation updated with correct paths

---

## Deployment Strategy

### Deployment Steps

**This is development environment reorganization - no production deployment.**

Steps to finalize:

1. Complete all implementation stories
2. Verify all acceptance criteria met
3. Run full test suite: `pytest tests/ -v`
4. Test MCP server manually with Claude Desktop or MCP client
5. Commit changes: `git add . && git commit -m "fix: reorganize to root structure and fix broken venv"`
6. Update workflow status: Mark tech-spec complete
7. Proceed to sprint-planning for implementation tracking

### Rollback Plan

**If issues arise during reorganization:**

1. **Before deleting /databricks-mcp/:**
   - Folder still exists, can revert file moves easily
   - Simply move files back: `mv README.md databricks-mcp/`

2. **After deleting /databricks-mcp/:**
   - Use git to restore: `git checkout databricks-mcp/`
   - Recreate venv in old location if needed

3. **Venv issues:**
   - Can always recreate: `rm -rf .venv && python3 -m venv .venv`
   - Reinstall: `pip install -e ".[dev]"`

**Safest approach:** Make changes incrementally, test after each story.

### Monitoring

**Post-Implementation Monitoring:**

1. **Verify in Claude Desktop:**
   - MCP server appears in settings
   - Server starts without errors
   - Tools are discoverable

2. **Check Logs:**
   - `databricks_mcp.log` - No error messages
   - stderr output - Clean startup

3. **Functional Testing:**
   - Execute representative tool from each API module
   - Verify responses are correct
   - Confirm no regressions

**Success Metrics:**
- ✅ Server starts in <2 seconds
- ✅ All 64 tools register successfully
- ✅ All pytest tests passing
- ✅ No import errors in logs
- ✅ MCP client can connect and execute tools

---

**End of Tech-Spec**

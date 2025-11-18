# databrics-mcp-server - Epic Breakdown

**Date:** 2025-11-12
**Project Level:** Level 1

---

## Epic 1: MCP Server Reorganization and Functionality Restoration

**Slug:** mcp-server-fix

### Goal

Complete the partial reorganization of the Databricks MCP Server from nested structure to root-level MCP best practices, fix broken dependencies and configuration, and verify all 64 MCP tools are fully functional.

### Scope

**In Scope:**
- Reconstruct broken virtual environment at project root
- Complete file migration (move all documentation from /databricks-mcp/ to root)
- Remove duplicate configuration files and orphaned directories
- Update .mcp.json with correct paths for root-level execution
- Verify all Python imports resolve correctly
- Run comprehensive test suite to ensure functionality intact
- Manually test all 10 API modules to confirm MCP tools working
- Update generated brownfield documentation to reflect new structure

**Out of Scope:**
- Adding new features or API endpoints
- Refactoring existing code logic or architecture
- Upgrading dependencies to newer versions
- Performance optimization
- New documentation beyond path corrections

### Success Criteria

1. ✅ MCP server starts successfully without ImportError or ModuleNotFoundError
2. ✅ All pytest tests pass (or skip - no failures allowed)
3. ✅ All ~64 MCP tools register and are accessible via MCP protocol
4. ✅ Root directory follows MCP server best practices (has README, proper structure)
5. ✅ No duplicate configuration files or orphaned folders exist
6. ✅ .mcp.json configuration works with Claude Desktop/MCP clients
7. ✅ Generated documentation (docs/*.md) reflects accurate file paths
8. ✅ At least one tool from each API module verified functional

### Dependencies

**External:**
- Python 3.10+ (system has 3.13.2)
- Databricks workspace access for testing tools

**Internal:**
- Existing codebase already moved to root (databricks_mcp/, tests/, scripts/, examples/)
- pyproject.toml at root with correct package configuration
- .mcp.json exists (needs path updates)

---

## Story Map - Epic 1

```
Epic: MCP Server Reorganization and Functionality Restoration
├── Story 1: Environment Reconstruction (2 points)
│   Dependencies: None (foundational work)
│   Deliverable: Fresh venv with all dependencies installed
│
├── Story 2: File Consolidation and Cleanup (2 points)
│   Dependencies: None (parallel to Story 1, but typically done after)
│   Deliverable: Clean root structure, no orphaned folders
│
└── Story 3: Configuration Update and Comprehensive Verification (3 points)
    Dependencies: Story 1 (requires working venv) + Story 2 (requires clean structure)
    Deliverable: Working MCP server, all tests passing, all tools verified
```

**Total Story Points:** 7 points
**Estimated Timeline:** 1 sprint (1-1.5 weeks at 1-2 points per day)

**Dependency Validation:** ✅ Valid sequence
- Story 1 & 2 can run in parallel or sequential order (no interdependency)
- Story 3 requires both Story 1 & 2 complete (valid dependency on prior work)

---

## Stories - Epic 1

### Story 1.1: Environment Reconstruction

As a developer,
I want a functional virtual environment at the project root with all dependencies installed,
So that I can run the MCP server and execute tests without import errors.

**Acceptance Criteria:**

**AC #1:** Given the project root directory, when I delete the broken .venv and create a fresh virtual environment using `python3 -m venv .venv`, then the venv is created successfully at the root level.

**AC #2:** Given the new virtual environment, when I activate it and run `pip install -e ".[dev]"`, then all dependencies from pyproject.toml are installed without errors (mcp, httpx, databricks-sdk, pytest, etc.).

**AC #3:** Given all dependencies installed, when I run `python -c "from databricks_mcp.server import DatabricksMCPServer"`, then the import succeeds with no ModuleNotFoundError.

**AC #4:** Given the installed package, when I run `python -c "from databricks_mcp.api import clusters, sql, genie"`, then all API module imports succeed.

**Prerequisites:** None (foundational work)

**Technical Notes:**
- Delete broken venv that points to old `/databricks-mcp/.venv` path
- Use Python 3.13.2 system Python
- Install in editable mode for development

**Estimated Effort:** 2 story points (0.5-1 day)

---

### Story 1.2: File Consolidation and Cleanup

As a developer,
I want all project files organized at the root level following MCP server best practices,
So that the project structure is standard, maintainable, and has no duplicate or orphaned files.

**Acceptance Criteria:**

**AC #1:** Given the files in /databricks-mcp/ folder, when I move README.md, QUICK_START.md, TROUBLESHOOTING.md, and ENHANCEMENTS.md to the project root, then all documentation files exist at root and are accessible.

**AC #2:** Given duplicate pyproject.toml and uv.lock files, when I verify they are identical and delete the copies in /databricks-mcp/, then only root versions remain.

**AC #3:** Given all useful files migrated, when I delete the entire /databricks-mcp/ directory, then the folder no longer exists and root structure is clean.

**AC #4:** Given the final root structure, when I list files at project root, then I see: README.md, databricks_mcp/, tests/, examples/, scripts/, pyproject.toml, .venv/, .mcp.json, and no /databricks-mcp/ folder.

**AC #5:** Given the reorganized structure, when I check for MCP best practices compliance, then the project has README at root, proper package structure, and follows standard layout.

**Prerequisites:** None (can run in parallel with Story 1 or after)

**Technical Notes:**
- Verify pyproject.toml files identical before deleting: `diff pyproject.toml databricks-mcp/pyproject.toml`
- Keep test_server.sh at root if not already there
- Delete log files in /databricks-mcp/ (local_mcp_stderr*.log)

**Estimated Effort:** 2 story points (0.5-1 day)

---

### Story 1.3: Configuration Update and Comprehensive Verification

As a developer and MCP user,
I want the MCP server configuration updated and all functionality verified,
So that the server starts correctly, all 64 tools work, and I can use it with Claude Desktop and other MCP clients.

**Acceptance Criteria:**

**AC #1:** Given the new root structure, when I update .mcp.json with correct paths (command: root/.venv/bin/python, cwd: root directory), then the configuration is syntactically valid and points to existing paths.

**AC #2:** Given the updated configuration, when I run `timeout 3s .venv/bin/python -m databricks_mcp.main`, then the server starts and waits for stdio input (timeout exit code 124 = success).

**AC #3:** Given the working server, when I run the full pytest suite with `.venv/bin/pytest tests/ -v`, then all tests pass or skip with zero failures.

**AC #4:** Given the MCP server running, when I connect via MCP client and list available tools, then approximately 64 tools are registered across all 10 API modules (clusters, sql, genie, jobs, notebooks, dbfs, unity_catalog, repos, libraries).

**AC #5:** Given the registered tools, when I test one representative tool from each API module, then all tools execute without errors and return properly formatted responses:
- Clusters: list_clusters
- SQL: execute_safe_statement
- Genie: list_genie_spaces
- Jobs: list_jobs
- Notebooks: list
- DBFS: list
- Unity Catalog: list_schemas
- Repos: list
- Libraries: cluster_status

**AC #6:** Given the updated structure, when I review docs/index.md, docs/source-tree-analysis.md, and docs/project-overview.md, then all file path references are correct (no /databricks-mcp/ paths remain) and documentation accurately reflects root-level organization.

**Prerequisites:**
- Story 1 complete (working venv)
- Story 2 complete (clean structure)

**Technical Notes:**
- .mcp.json absolute paths recommended for reliability
- Use timeout command for server startup test (server will hang waiting for stdio - this is correct behavior)
- Document any test failures for investigation
- Manual MCP tool testing can use MCP Inspector or test client

**Estimated Effort:** 3 story points (1-1.5 days)

---

## Implementation Timeline - Epic 1

**Total Story Points:** 7 points

**Estimated Timeline:** 1 sprint (1-1.5 weeks assuming 1-2 points per day)

**Implementation Sequence:**

1. **Story 1** → Reconstruct environment (setup, install dependencies, verify imports)
   - Dependencies: None
   - Deliverable: Working venv at root with all packages installed

2. **Story 2** → Consolidate files (move docs, remove duplicates, clean up)
   - Dependencies: None (can run parallel or after Story 1)
   - Deliverable: Clean root structure following MCP best practices

3. **Story 3** → Update config and verify (fix .mcp.json, run tests, verify all tools)
   - Dependencies: Story 1 & 2 must be complete
   - Deliverable: Fully functional MCP server with all tools verified

**Dependency Validation:** ✅ Valid sequence - Story 3 depends only on Stories 1 & 2 (no forward dependencies)

---

## Tech-Spec Reference

See [tech-spec.md](./tech-spec.md) for complete technical implementation details including:
- Root cause analysis
- Detailed file paths and changes
- Testing strategy
- Development setup instructions
- Existing code patterns to follow

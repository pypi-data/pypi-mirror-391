# Databricks MCP Server - Documentation Index

> **AI-Assisted Development Entry Point**
> This is your primary reference for understanding and enhancing the Databricks MCP Server codebase.

## Project Overview

- **Type:** Monolith (single cohesive Python backend)
- **Primary Language:** Python 3.10+
- **Architecture:** Layered backend with MCP protocol
- **Version:** 0.3.1 (Beta)
- **Purpose:** Model Context Protocol server for Databricks API integration

## Quick Reference

### Technology Stack
- **Core:** Python 3.10+, asyncio
- **Framework:** FastMCP (Model Context Protocol)
- **API SDK:** databricks-sdk, httpx
- **Testing:** pytest, pytest-asyncio
- **Build:** hatchling (PEP 517)

### Entry Points
- **MCP Server:** `databricks_mcp/server/databricks_mcp_server.py`
- **CLI Tool:** `databricks_mcp/cli/commands.py`
- **Main App:** `databricks_mcp/main.py`

### Architecture Pattern
**Layered Backend:**
- API Layer: 10 modules with ~64 async functions
- Core Layer: Auth, config, utilities, SQL safety
- Server Layer: MCP protocol implementation
- CLI Layer: Command-line interface

## Generated Documentation

### Core Documentation
- [**Project Overview**](./project-overview.md) - Executive summary, tech stack, and quick start
- [**Source Tree Analysis**](./source-tree-analysis.md) - Complete directory structure with annotations
- [**API Contracts**](./api-contracts.md) - All API endpoints and MCP tools (64 functions)

### Architecture & Implementation _(To be generated)_
- [Architecture](./architecture.md) _(To be generated)_
- [Development Guide](./development-guide.md) _(To be generated)_

## Existing Project Documentation

### Main Documentation (Root Level)
- [README.md](../README.md) - Main project documentation with features and installation
- [QUICK_START.md](../QUICK_START.md) - Quick start guide for getting up and running
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common issues and solutions
- [ENHANCEMENTS.md](../ENHANCEMENTS.md) - Enhancement tracking and roadmap

### Technical Documentation (docs/)
- [CHANGELOG.md](./CHANGELOG.md) - Version history and changes
- [AGENTS.md](./AGENTS.md) - AI agent integration documentation
- [project_structure.md](./project_structure.md) - Project structure guide
- [phase1.md](./phase1.md) - Phase 1 development roadmap
- [new_features.md](./new_features.md) - New features documentation

### Module-Specific
- [tests/README.md](../tests/README.md) - Test suite documentation
- [examples/README.md](../examples/README.md) - Usage examples

## API Reference

The Databricks MCP Server exposes the following API modules:

1. **Clusters API** - Cluster lifecycle management (create, start, stop, resize, restart)
2. **SQL API** - SQL execution with safety validation and polling
3. **Genie AI API** - Natural language data analysis with conversation context
4. **Jobs API** - Job management and execution control
5. **Notebooks API** - Notebook operations and management
6. **DBFS API** - Databricks File System operations
7. **Unity Catalog API** - Data governance and catalog management
8. **Repositories API** - Git repository integration
9. **Libraries API** - Library installation and management

See [API Contracts](./api-contracts.md) for complete endpoint documentation.

## Key Capabilities

### For AI Agents
- **SQL Safety:** Read-only validation prevents destructive operations
- **Natural Language:** Genie AI integration for conversational data analysis
- **Async Operations:** Polling and timeout management for long-running tasks
- **Error Handling:** Comprehensive exception hierarchy with detailed error messages

### For Developers
- **MCP Protocol:** Standard Model Context Protocol implementation
- **Extensible:** Modular design for adding new Databricks features
- **Well-Tested:** pytest-asyncio test suite
- **Cross-Platform:** Supports Unix (.sh) and Windows (.ps1) scripts

## Getting Started

### 1. Environment Setup
```bash
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="your-personal-access-token"
export DATABRICKS_WAREHOUSE_ID="your-warehouse-id"  # Optional for SQL
```

### 2. Installation
```bash
# Via uvx (recommended)
uvx databricks-mcp-server

# Via pip
pip install databricks-mcp-server

# From source
cd databricks-mcp
pip install -e .
```

### 3. Usage
```bash
# Start MCP server (stdio mode)
databricks-mcp-server

# Use CLI
databricks-mcp list-clusters
```

## AI-Assisted Development Guide

### Planning New Features
1. **Review API Contracts** - Understand existing API patterns and conventions
2. **Check Source Tree** - Identify where new code should live
3. **Follow Patterns** - All API modules use async/await with `make_api_request()`
4. **Add Safety** - Use SQL safety validation for any SQL-related features

### Common Modification Tasks

#### Adding a New Databricks API
1. Create new module in `databricks_mcp/api/{feature}.py`
2. Implement async functions using `make_api_request()` from `core/utils.py`
3. Register tools in `server/databricks_mcp_server.py`
4. Add tests in `tests/test_{feature}.py`

#### Enhancing Existing APIs
1. Locate module in `databricks_mcp/api/`
2. Add new async function following existing patterns
3. Update tool registration in server
4. Add test coverage

#### Improving Core Utilities
- **Auth:** `core/auth.py`
- **Config:** `core/config.py`
- **SQL Safety:** `core/sql_safety.py`
- **Formatting:** `core/formatting.py`

### Testing
```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/test_clusters.py

# Run with coverage
pytest --cov=databricks_mcp
```

## Integration Patterns

### MCP Tool Registration Pattern
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

### API Module Pattern
```python
async def api_function(param: str) -> Dict[str, Any]:
    """Function docstring"""
    logger.info(f"Action: {param}")
    return await make_api_request("METHOD", "/endpoint", data={...})
```

## Project Context for PRD Creation

### When Planning Brownfield Features:
- **Architecture:** Layered backend with clear separation (API/Core/Server/CLI)
- **Patterns:** All API functions are async, use `make_api_request()` utility
- **Safety First:** SQL operations use `sql_safety.py` validation
- **Testing:** pytest-asyncio with comprehensive coverage
- **MCP Integration:** Tools registered via decorators, stdio communication

### Reusable Components:
- `core/utils.py` - HTTP request handling with retries and error management
- `core/config.py` - Environment variable management with validation
- `core/formatting.py` - Result formatting for various data types
- `core/sql_safety.py` - SQL validation for read-only enforcement

### Integration Points:
- All API modules → `core/utils.make_api_request()`
- Server → API modules (imports and registers as tools)
- Tests → Both API modules and server for end-to-end testing

## Workflow Status

This documentation was generated as part of the BMad Method workflow:
- **Track:** Quick Flow (Brownfield)
- **Phase:** Documentation Complete
- **Next Step:** Tech-Spec creation for planned enhancements

See `bmm-workflow-status.yaml` for current workflow state.

---

**Last Updated:** 2025-11-13
**Documentation Version:** 1.0 (Deep Scan)
**Generated By:** BMad Method - document-project workflow

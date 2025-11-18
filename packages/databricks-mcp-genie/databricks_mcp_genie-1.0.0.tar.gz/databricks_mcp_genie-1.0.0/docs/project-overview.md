# Project Overview - Databricks MCP Server

## Executive Summary

The Databricks MCP Server is a **Model Context Protocol (MCP) server** that provides LLM-powered tools with programmatic access to Databricks functionality. Built in Python 3.10+, it exposes approximately 64 async API functions across 10 functional modules, enabling AI agents to interact with Databricks clusters, SQL warehouses, notebooks, jobs, and Genie AI.

**Version:** 0.3.1
**Status:** Beta (Production-ready with ongoing enhancements)
**License:** MIT

## Purpose

Enable Large Language Models and AI agents to:
- Manage Databricks resources (clusters, jobs, notebooks)
- Execute SQL queries with safety validation
- Interact with Genie AI for natural language data analysis
- Access Unity Catalog for data governance
- Manage files via DBFS
- Control git repositories

## Technology Stack

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

## Architecture Type

**Pattern:** Layered Backend Architecture
- **API Layer:** Databricks REST API wrappers (`api/` modules)
- **Core Layer:** Shared utilities, auth, configuration (`core/` modules)
- **Server Layer:** MCP protocol implementation (`server/` modules)
- **CLI Layer:** Command-line interface (`cli/` modules)

**Communication:** Async/await throughout with stdio-based MCP protocol

## Repository Structure

**Type:** Monolith
**Structure:** Single cohesive Python backend project
**Organization:** Modular package with clear separation of concerns

```
databricks-mcp/          # Main implementation
├── databricks_mcp/      # Python package
│   ├── api/             # 10 API modules
│   ├── core/            # 6 utility modules
│   ├── server/          # MCP server implementation
│   └── cli/             # CLI commands
├── tests/               # pytest test suite
├── docs/                # Project documentation
├── examples/            # Usage examples
└── scripts/             # Automation scripts
```

## Key Features

1. **MCP Protocol Support**
   - Implements FastMCP server
   - Stdio communication
   - Structured tool registration
   - Parameter unwrapping for client compatibility

2. **Comprehensive Databricks API Coverage**
   - Clusters: Create, start, stop, resize, restart
   - SQL: Execute, poll, safety validation
   - Genie AI: Natural language data analysis
   - Jobs: Management and execution
   - Notebooks: Operations and management
   - Unity Catalog: Data governance
   - DBFS: File system operations
   - Repos: Git integration

3. **AI Agent Safety**
   - SQL safety validation (read-only enforcement)
   - Configurable row/byte limits
   - Timeout protection
   - Error handling and logging

4. **Async Architecture**
   - Full async/await implementation
   - Efficient concurrent operations
   - Polling for long-running tasks

## Links to Detailed Documentation

- [API Contracts](./api-contracts.md) - Complete API endpoint documentation
- [Source Tree Analysis](./source-tree-analysis.md) - Detailed directory structure
- [Architecture](./architecture.md) - System architecture and patterns _(To be generated)_
- [Development Guide](./development-guide.md) - Setup and development workflow _(To be generated)_

## Existing Project Documentation

Located at project root and in `/docs/`:
- [README.md](../README.md) - Main project documentation
- [QUICK_START.md](../QUICK_START.md) - Quick start guide
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common issues
- [ENHANCEMENTS.md](../ENHANCEMENTS.md) - Enhancement tracking
- [CHANGELOG.md](./CHANGELOG.md) - Version history
- [AGENTS.md](./AGENTS.md) - Agent documentation

## Installation

```bash
# Via pip
pip install databricks-mcp-server

# Via uvx (recommended)
uvx databricks-mcp-server

# From source
git clone https://github.com/markov-kernel/databricks-mcp
cd databricks-mcp
pip install -e .
```

## Quick Start

```bash
# Set environment variables
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="your-token"
export DATABRICKS_WAREHOUSE_ID="your-warehouse-id"

# Start MCP server
databricks-mcp-server

# Or use CLI
databricks-mcp list-clusters
```

## Current Status

**Latest Release:** v0.3.1
- Issue #9 fix
- Enhanced MCP client compatibility
- Improved error handling
- SQL safety features

**Development Stage:** Beta
**Production Readiness:** Suitable for production use with monitoring

## Maintainer

**Built by:** [Markov](https://markov.bot)
**Author:** Olivier Debeuf De Rijcker <olivier@markov.bot>
**Original Credit:** [@JustTryAI](https://github.com/JustTryAI/databricks-mcp-server)

## License

MIT License - See project repository for details

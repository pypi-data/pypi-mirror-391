# API Contracts - Databricks MCP Server

## Overview

The Databricks MCP Server exposes approximately 64 async API functions organized into functional modules. All API endpoints communicate with the Databricks REST API using async/await patterns.

## API Modules

### 1. Clusters API (`api/clusters.py`)

**Base Path:** `/api/2.0/clusters`

| Function | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| `create_cluster()` | POST | `/create` | Create a new Databricks cluster |
| `terminate_cluster()` | POST | `/delete` | Terminate a cluster |
| `list_clusters()` | GET | `/list` | List all clusters |
| `get_cluster()` | GET | `/get` | Get cluster information |
| `start_cluster()` | POST | `/start` | Start a terminated cluster |
| `resize_cluster()` | POST | `/resize` | Resize cluster workers |
| `restart_cluster()` | POST | `/restart` | Restart a cluster |

**Request/Response:** All functions return `Dict[str, Any]` with Databricks API responses.

---

### 2. SQL API (`api/sql.py`)

**Base Path:** `/api/2.0/sql`

| Function | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| `execute_statement()` | POST | `/statements` | Execute SQL statement |
| `execute_and_wait()` | POST | `/statements` + polling | Execute SQL and wait for completion |
| `get_statement_status()` | GET | `/statements/{id}` | Get statement status |
| `cancel_statement()` | POST | `/statements/{id}/cancel` | Cancel running statement |
| `execute_safe_statement()` | POST | `/statements` | Execute with safety validation |

**Special Features:**
- SQL safety validation (read-only enforcement)
- Automatic polling for long-running queries
- Configurable row and byte limits
- Warehouse ID from environment or parameter

**Request Parameters:**
```python
{
    "statement": str,
    "warehouse_id": Optional[str],
    "catalog": Optional[str],
    "schema": Optional[str],
    "parameters": Optional[Dict],
    "row_limit": int = 10000,
    "byte_limit": int = 100000000
}
```

---

### 3. Genie AI API (`api/genie.py`)

**Base Path:** `/api/2.0/genie`

| Function | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| `list_genie_spaces()` | GET | `/spaces` | List available Genie spaces |
| `start_conversation()` | POST | `/spaces/{id}/start-conversation` | Start AI conversation |
| `send_followup_message()` | POST | `/spaces/{id}/conversations/{cid}/messages` | Send follow-up question |
| `get_message_status()` | GET | `/spaces/{id}/conversations/{cid}/messages/{mid}` | Get message status |
| `get_query_results()` | GET | `/spaces/{id}/conversations/{cid}/messages/{mid}/query-result/{aid}` | Get query results |

**Special Features:**
- Natural language data analysis
- Automatic polling with 2-second intervals
- 300-second max wait timeout
- Conversation context retention

**Example Workflow:**
```python
# 1. Start conversation
response = await start_conversation(space_id, "Show me sales by region")

# 2. Get results
conversation_id = response["conversation_id"]
sql = response["sql"]  # Generated SQL
results = response["results"]  # Query results

# 3. Follow-up
followup = await send_followup_message(
    space_id, conversation_id, "Now show top 10"
)
```

---

### 4. DBFS API (`api/dbfs.py`)

**Base Path:** `/api/2.0/dbfs`

Provides file system operations for Databricks File System.

---

### 5. Jobs API (`api/jobs.py`)

**Base Path:** `/api/2.0/jobs`

Job management and execution control.

---

### 6. Notebooks API (`api/notebooks.py`)

**Base Path:** `/api/2.0/workspace`

Notebook management and operations.

---

### 7. Unity Catalog API (`api/unity_catalog.py`, `api/unity_catalog_enhanced.py`)

**Base Paths:** `/api/2.1/unity-catalog`

Data governance and catalog management with enhanced features.

---

### 8. Repositories API (`api/repos.py`)

**Base Path:** `/api/2.0/repos`

Git repository integration.

---

### 9. Libraries API (`api/libraries.py`)

**Base Path:** `/api/2.0/libraries`

Library installation and management.

---

## Authentication

All API calls use the Databricks authentication via:
- `DATABRICKS_HOST` environment variable
- `DATABRICKS_TOKEN` environment variable

Implemented in `core/auth.py` and `core/config.py`.

## Error Handling

**Exception Hierarchy:**
- `DatabricksAPIError` - Base API error (from `core/utils.py`)
- `SQLSafetyError` - SQL validation error (from `core/sql_safety.py`)
- `ValueError` - Missing required parameters
- `TimeoutError` - Long-running operation timeout

## Common Patterns

### 1. Async/Await
All API functions are async and must be awaited:
```python
result = await clusters.list_clusters()
```

### 2. Parameter Unwrapping
MCP server unwraps nested parameters from client:
```python
# Client may send: {"params": {"cluster_id": "123"}}
# Server unwraps to: {"cluster_id": "123"}
```

### 3. Polling Pattern
Long-running operations use polling:
```python
while status in ["PENDING", "RUNNING"]:
    await asyncio.sleep(poll_interval)
    status = await check_status()
```

## MCP Tool Registration

The `server/databricks_mcp_server.py` registers all API functions as MCP tools using decorators:

```python
@self.tool(
    name="list_clusters",
    description="List all Databricks clusters"
)
async def list_clusters(params: Dict[str, Any]) -> List[TextContent]:
    result = await clusters.list_clusters()
    return [{"type": "text", "text": json.dumps(result)}]
```

## Response Format

All MCP tool responses follow this format:
```python
[{
    "type": "text",
    "text": json.dumps({
        # Databricks API response data
    })
}]
```

## Rate Limiting & Quotas

Managed by Databricks API. Server implements:
- Configurable timeouts
- Row/byte limits for SQL queries
- Polling intervals to avoid overwhelming API

## Data Models

See `core/models.py` for request/response type definitions.

## Formatting & Safety

- **SQL Formatting:** `core/formatting.py` - Query result formatting
- **SQL Safety:** `core/sql_safety.py` - Read-only validation for AI agents
- **Configuration:** `core/config.py` - Settings management
- **Utilities:** `core/utils.py` - HTTP request handling

## Integration with MCP Protocol

The server implements the Model Context Protocol (MCP):
- Uses `FastMCP` base class from `mcp.server`
- Communicates via stdio
- Returns structured `TextContent` responses
- Supports both sync and async tool execution

## Testing

Test coverage for API endpoints in `/tests` directory with pytest-asyncio.

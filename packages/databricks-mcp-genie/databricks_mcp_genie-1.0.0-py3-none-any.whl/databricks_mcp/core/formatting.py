"""
Enhanced formatting utilities for context-optimized responses.

Provides response formatting, truncation, and detail level management
to optimize for limited context windows in AI agent interactions.
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class DetailLevel(str, Enum):
    """Detail level for responses."""
    CONCISE = "concise"  # High-signal summary
    DETAILED = "detailed"  # Full information


# Constants
CHARACTER_LIMIT = 25000  # Maximum response size in characters


def format_timestamp(ts: Optional[int]) -> str:
    """
    Format Unix timestamp to human-readable format.

    Args:
        ts: Unix timestamp in milliseconds

    Returns:
        Formatted timestamp string or "N/A"
    """
    if not ts:
        return "N/A"
    try:
        return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, OSError):
        return f"Invalid timestamp: {ts}"


def truncate_response(data: str, max_chars: int = CHARACTER_LIMIT) -> Tuple[str, bool]:
    """
    Truncate response if it exceeds character limit.

    Args:
        data: Response string to truncate
        max_chars: Maximum characters allowed

    Returns:
        Tuple of (truncated_data, was_truncated)
    """
    if len(data) <= max_chars:
        return data, False

    truncated = data[:max_chars]
    return truncated, True


def format_catalogs_markdown(
    catalogs: List[Dict[str, Any]],
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    Format catalogs list as Markdown.

    Args:
        catalogs: List of catalog dictionaries
        detail_level: Level of detail to include

    Returns:
        Formatted Markdown string
    """
    lines = ["# Unity Catalogs", "", f"Found {len(catalogs)} catalogs", ""]

    for catalog in catalogs:
        lines.append(f"## {catalog.get('name', 'Unknown')}")

        if detail_level == DetailLevel.DETAILED:
            if catalog.get('catalog_type'):
                lines.append(f"- **Type**: {catalog['catalog_type']}")
            if catalog.get('comment'):
                lines.append(f"- **Description**: {catalog['comment']}")
            if catalog.get('owner'):
                lines.append(f"- **Owner**: {catalog['owner']}")
            if catalog.get('created_at'):
                lines.append(f"- **Created**: {format_timestamp(catalog['created_at'])}")
        else:
            # Concise mode: just name and description
            if catalog.get('comment'):
                lines.append(f"- {catalog['comment']}")

        lines.append("")

    return "\n".join(lines)


def format_schemas_markdown(
    schemas: List[Dict[str, Any]],
    catalog_name: str,
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    Format schemas list as Markdown.

    Args:
        schemas: List of schema dictionaries
        catalog_name: Name of parent catalog
        detail_level: Level of detail to include

    Returns:
        Formatted Markdown string
    """
    lines = [f"# Catalog: {catalog_name}", "", f"## Schemas ({len(schemas)})", ""]

    if not schemas:
        lines.append("No schemas found in this catalog.")
        return "\n".join(lines)

    for schema in schemas:
        lines.append(f"### {schema.get('name', 'Unknown')}")
        if schema.get('comment'):
            lines.append(f"- {schema['comment']}")

        if detail_level == DetailLevel.DETAILED:
            if schema.get('owner'):
                lines.append(f"- Owner: {schema['owner']}")
            if schema.get('created_at'):
                lines.append(f"- Created: {format_timestamp(schema['created_at'])}")

        lines.append("")

    return "\n".join(lines)


def format_tables_markdown(
    tables: List[Dict[str, Any]],
    schema_name: str,
    include_columns: bool = False,
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    Format tables list as Markdown.

    Args:
        tables: List of table dictionaries
        schema_name: Name of parent schema
        include_columns: Whether to include column details
        detail_level: Level of detail to include

    Returns:
        Formatted Markdown string
    """
    lines = [f"# Schema: {schema_name}", "", f"## Tables ({len(tables)})", ""]

    if not tables:
        lines.append("No tables found in this schema.")
        return "\n".join(lines)

    for table in tables:
        lines.append(f"### {table.get('name', 'Unknown')}")
        if table.get('comment'):
            lines.append(f"- {table['comment']}")

        if detail_level == DetailLevel.DETAILED or include_columns:
            if table.get('table_type'):
                lines.append(f"- **Type**: {table['table_type']}")

        if include_columns and table.get('columns'):
            lines.append("- **Columns**:")
            for col in table['columns']:
                col_line = f"  - {col.get('name', 'unknown')} ({col.get('type_name', 'unknown')})"
                if col.get('comment'):
                    col_line += f" - {col['comment']}"
                lines.append(col_line)

        lines.append("")

    return "\n".join(lines)


def format_table_detail_markdown(
    table: Dict[str, Any],
    lineage: Optional[Dict[str, Any]] = None,
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    Format table details as Markdown.

    Args:
        table: Table dictionary
        lineage: Optional lineage information
        detail_level: Level of detail to include

    Returns:
        Formatted Markdown string
    """
    lines = [f"# Table: {table.get('full_name', 'Unknown')}", ""]

    if table.get('comment'):
        lines.append(f"{table['comment']}")
        lines.append("")

    # Table metadata
    if table.get('table_type'):
        lines.append(f"- **Type**: {table['table_type']}")
    if table.get('data_source_format'):
        lines.append(f"- **Format**: {table['data_source_format']}")

    if detail_level == DetailLevel.DETAILED:
        if table.get('storage_location'):
            lines.append(f"- **Location**: {table['storage_location']}")
        if table.get('owner'):
            lines.append(f"- **Owner**: {table['owner']}")
        if table.get('created_at'):
            lines.append(f"- **Created**: {format_timestamp(table['created_at'])}")

    lines.append("")

    # Columns
    if table.get('columns'):
        lines.append(f"## Columns ({len(table['columns'])})")
        lines.append("")
        for col in table['columns']:
            col_line = f"- **{col.get('name', 'unknown')}** ({col.get('type_name', 'unknown')})"
            if col.get('comment'):
                col_line += f" - {col['comment']}"
            if detail_level == DetailLevel.DETAILED and not col.get('nullable'):
                col_line += " [NOT NULL]"
            lines.append(col_line)
        lines.append("")

    # Lineage
    if lineage:
        lines.append("## Lineage")
        lines.append("")

        if lineage.get('upstream_tables'):
            lines.append("### Upstream Tables")
            lines.append("Tables that this table reads from:")
            for table_name in lineage['upstream_tables']:
                lines.append(f"- {table_name}")
            lines.append("")

        if lineage.get('downstream_tables'):
            lines.append("### Downstream Tables")
            lines.append("Tables that read from this table:")
            for table_name in lineage['downstream_tables']:
                lines.append(f"- {table_name}")
            lines.append("")

        if lineage.get('notebooks'):
            lines.append("### Notebooks")
            lines.append("")
            for notebook in lineage['notebooks']:
                lines.append(f"#### {notebook.get('name', 'Unnamed')}")
                lines.append(f"- **Path**: {notebook.get('path')}")
                if notebook.get('job_name'):
                    lines.append(f"- **Job**: {notebook['job_name']} (ID: {notebook.get('job_id')})")
                lines.append(f"- **Operations**: {', '.join(notebook.get('operations', []))}")
                lines.append("")

    return "\n".join(lines)


def format_sql_results_markdown(
    columns: List[str],
    rows: List[List[Any]],
    execution_time: Optional[float] = None,
    truncated: bool = False
) -> str:
    """
    Format SQL query results as Markdown table.

    Args:
        columns: List of column names
        rows: List of row data
        execution_time: Optional execution time in seconds
        truncated: Whether results were truncated

    Returns:
        Formatted Markdown string
    """
    lines = ["# Query Results", ""]

    if execution_time:
        lines.append(f"Executed in {execution_time:.2f} seconds")
    lines.append(f"Returned {len(rows)} rows")
    lines.append("")

    # Create markdown table
    if rows:
        # Header row
        lines.append("| " + " | ".join(columns) + " |")
        # Separator row
        lines.append("|" + "|".join(["---" for _ in columns]) + "|")
        # Data rows
        for row in rows:
            formatted_row = []
            for val in row:
                if val is None:
                    formatted_row.append("NULL")
                elif isinstance(val, (int, float)):
                    formatted_row.append(str(val))
                else:
                    formatted_row.append(str(val)[:50])  # Truncate long values
            lines.append("| " + " | ".join(formatted_row) + " |")
    else:
        lines.append("No rows returned")

    lines.append("")

    if truncated:
        lines.append(f"[Showing first {len(rows)} rows - response truncated]")
    else:
        lines.append(f"[Showing all {len(rows)} rows]")

    return "\n".join(lines)


def format_clusters_markdown(
    clusters: List[Dict[str, Any]],
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    Format clusters list as Markdown.

    Args:
        clusters: List of cluster dictionaries
        detail_level: Level of detail to include

    Returns:
        Formatted Markdown string
    """
    lines = ["# Databricks Clusters", "", f"Found {len(clusters)} clusters", ""]

    for cluster in clusters:
        lines.append(f"## {cluster.get('cluster_name', 'Unknown')}")
        lines.append(f"- **Cluster ID**: {cluster.get('cluster_id')}")
        lines.append(f"- **State**: {cluster.get('state', 'Unknown')}")

        if detail_level == DetailLevel.DETAILED:
            if cluster.get('spark_version'):
                lines.append(f"- **Spark Version**: {cluster['spark_version']}")
            if cluster.get('node_type_id'):
                lines.append(f"- **Node Type**: {cluster['node_type_id']}")
            if cluster.get('num_workers') is not None:
                lines.append(f"- **Workers**: {cluster['num_workers']}")
            elif cluster.get('autoscale'):
                autoscale = cluster['autoscale']
                lines.append(f"- **Autoscale**: {autoscale.get('min_workers')} - {autoscale.get('max_workers')} workers")

        lines.append("")

    return "\n".join(lines)


def format_jobs_markdown(
    jobs: List[Dict[str, Any]],
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    Format jobs list as Markdown.

    Args:
        jobs: List of job dictionaries
        detail_level: Level of detail to include

    Returns:
        Formatted Markdown string
    """
    lines = ["# Databricks Jobs", "", f"Found {len(jobs)} jobs", ""]

    for job in jobs:
        settings = job.get('settings', {})
        lines.append(f"## {settings.get('name', 'Unnamed Job')}")
        lines.append(f"- **Job ID**: {job.get('job_id')}")

        if detail_level == DetailLevel.DETAILED:
            if settings.get('schedule'):
                lines.append(f"- **Schedule**: {settings['schedule'].get('quartz_cron_expression')}")
            if settings.get('timeout_seconds'):
                lines.append(f"- **Timeout**: {settings['timeout_seconds']}s")
            if job.get('created_time'):
                lines.append(f"- **Created**: {format_timestamp(job['created_time'])}")

        lines.append("")

    return "\n".join(lines)


def apply_truncation_if_needed(content: str, format_type: ResponseFormat) -> str:
    """
    Apply truncation if content exceeds character limit.

    Args:
        content: Content to check and truncate
        format_type: Response format type

    Returns:
        Potentially truncated content with indicator
    """
    truncated_content, was_truncated = truncate_response(content)

    if was_truncated:
        if format_type == ResponseFormat.MARKDOWN:
            truncated_content += "\n\n[Response truncated due to size. Use filters or detail_level='concise' to reduce results.]"
        else:  # JSON
            try:
                data = json.loads(truncated_content)
                data["truncated"] = True
                data["truncation_message"] = "Response truncated due to size"
                truncated_content = json.dumps(data, indent=2)
            except json.JSONDecodeError:
                # If can't parse, just add note
                truncated_content += '\n{"truncated": true}'

    return truncated_content

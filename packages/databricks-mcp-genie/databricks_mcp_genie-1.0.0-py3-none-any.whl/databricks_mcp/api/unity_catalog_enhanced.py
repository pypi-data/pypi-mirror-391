"""
Enhanced Unity Catalog API with response formatting and detail levels.

Provides Unity Catalog exploration with context-optimized responses for AI agents.
"""

import json
import logging
from typing import Any, Dict, Optional

from databricks_mcp.core.utils import make_api_request
from databricks_mcp.core.formatting import (
    ResponseFormat,
    DetailLevel,
    format_catalogs_markdown,
    format_schemas_markdown,
    format_tables_markdown,
    format_table_detail_markdown,
    apply_truncation_if_needed,
)
from databricks_mcp.api import sql

logger = logging.getLogger(__name__)


async def list_catalogs_enhanced(
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    List all Unity Catalogs with enhanced formatting.

    Args:
        response_format: Output format (markdown or json)
        detail_level: Level of detail (concise or detailed)

    Returns:
        Formatted string response

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Listing catalogs with format={response_format}, detail={detail_level}")

    # Get catalogs from API
    result = await make_api_request("GET", "/api/2.1/unity-catalog/catalogs")
    catalogs = result.get("catalogs", [])

    if response_format == ResponseFormat.MARKDOWN:
        content = format_catalogs_markdown(catalogs, detail_level)
    else:  # JSON
        if detail_level == DetailLevel.CONCISE:
            # Concise: just essential fields
            catalogs_data = [
                {
                    "name": cat.get("name"),
                    "comment": cat.get("comment"),
                }
                for cat in catalogs
            ]
        else:
            # Detailed: all fields
            catalogs_data = catalogs

        content = json.dumps({"catalogs": catalogs_data, "count": len(catalogs)}, indent=2)

    return apply_truncation_if_needed(content, response_format)


async def describe_catalog_enhanced(
    catalog_name: str,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    Describe a Unity Catalog with its schemas.

    Args:
        catalog_name: Name of the catalog
        response_format: Output format (markdown or json)
        detail_level: Level of detail (concise or detailed)

    Returns:
        Formatted string response

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Describing catalog {catalog_name} with format={response_format}, detail={detail_level}")

    # Get catalog details
    catalog = await make_api_request("GET", f"/api/2.1/unity-catalog/catalogs/{catalog_name}")

    # Get schemas
    schemas_result = await make_api_request(
        "GET",
        "/api/2.1/unity-catalog/schemas",
        params={"catalog_name": catalog_name}
    )
    schemas = schemas_result.get("schemas", [])

    if response_format == ResponseFormat.MARKDOWN:
        lines = [f"# Catalog: {catalog.get('name')}", ""]

        if detail_level == DetailLevel.DETAILED:
            if catalog.get("comment"):
                lines.append(f"**Description**: {catalog['comment']}")
            if catalog.get("owner"):
                lines.append(f"**Owner**: {catalog['owner']}")
            if catalog.get("catalog_type"):
                lines.append(f"**Type**: {catalog['catalog_type']}")
            lines.append("")
        elif catalog.get("comment"):
            lines.append(f"{catalog['comment']}")
            lines.append("")

        lines.append(f"## Schemas ({len(schemas)})")
        lines.append("")

        if not schemas:
            lines.append("No schemas found in this catalog.")
        else:
            for schema in schemas:
                lines.append(f"### {schema.get('name')}")
                if schema.get("comment"):
                    lines.append(f"- {schema['comment']}")
                if detail_level == DetailLevel.DETAILED and schema.get("owner"):
                    lines.append(f"- Owner: {schema['owner']}")
                lines.append("")

        content = "\n".join(lines)
    else:  # JSON
        catalog_dict = {"name": catalog.get("name")}

        if detail_level == DetailLevel.DETAILED:
            catalog_dict.update({
                "comment": catalog.get("comment"),
                "owner": catalog.get("owner"),
                "catalog_type": catalog.get("catalog_type"),
                "created_at": catalog.get("created_at"),
            })
        elif catalog.get("comment"):
            catalog_dict["comment"] = catalog["comment"]

        schemas_data = []
        for schema in schemas:
            schema_dict = {"name": schema.get("name")}
            if detail_level == DetailLevel.DETAILED:
                schema_dict.update({
                    "comment": schema.get("comment"),
                    "owner": schema.get("owner"),
                })
            elif schema.get("comment"):
                schema_dict["comment"] = schema["comment"]
            schemas_data.append(schema_dict)

        content = json.dumps({
            "catalog": catalog_dict,
            "schemas": schemas_data,
            "schema_count": len(schemas)
        }, indent=2)

    return apply_truncation_if_needed(content, response_format)


async def describe_schema_enhanced(
    catalog_name: str,
    schema_name: str,
    include_columns: bool = False,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    Describe a schema with its tables.

    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema
        include_columns: Whether to include column details
        response_format: Output format (markdown or json)
        detail_level: Level of detail (concise or detailed)

    Returns:
        Formatted string response

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(
        f"Describing schema {catalog_name}.{schema_name} "
        f"with columns={include_columns}, format={response_format}, detail={detail_level}"
    )

    # Get schema details
    schema = await make_api_request(
        "GET",
        f"/api/2.1/unity-catalog/schemas/{catalog_name}.{schema_name}"
    )

    # Get tables
    tables_result = await make_api_request(
        "GET",
        "/api/2.1/unity-catalog/tables",
        params={"catalog_name": catalog_name, "schema_name": schema_name}
    )
    tables = tables_result.get("tables", [])

    if response_format == ResponseFormat.MARKDOWN:
        content = format_tables_markdown(
            tables,
            f"{catalog_name}.{schema_name}",
            include_columns,
            detail_level
        )
    else:  # JSON
        schema_dict = {
            "full_name": f"{catalog_name}.{schema_name}",
            "catalog_name": catalog_name,
            "name": schema_name,
        }

        if detail_level == DetailLevel.DETAILED:
            schema_dict.update({
                "comment": schema.get("comment"),
                "owner": schema.get("owner"),
                "created_at": schema.get("created_at"),
            })
        elif schema.get("comment"):
            schema_dict["comment"] = schema["comment"]

        tables_data = []
        for table in tables:
            table_dict = {
                "name": table.get("name"),
                "table_type": table.get("table_type"),
            }

            if detail_level == DetailLevel.DETAILED or include_columns:
                if table.get("comment"):
                    table_dict["comment"] = table["comment"]

            if include_columns and table.get("columns"):
                table_dict["columns"] = [
                    {
                        "name": col.get("name"),
                        "type": col.get("type_name"),
                        "comment": col.get("comment"),
                        "nullable": col.get("nullable"),
                    }
                    for col in table["columns"]
                ]

            tables_data.append(table_dict)

        content = json.dumps({
            "schema": schema_dict,
            "tables": tables_data,
            "table_count": len(tables)
        }, indent=2)

    return apply_truncation_if_needed(content, response_format)


async def describe_table_enhanced(
    full_table_name: str,
    include_lineage: bool = False,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
    detail_level: DetailLevel = DetailLevel.CONCISE
) -> str:
    """
    Describe a table with optional lineage information.

    Args:
        full_table_name: Fully qualified table name (catalog.schema.table)
        include_lineage: Whether to include lineage information
        response_format: Output format (markdown or json)
        detail_level: Level of detail (concise or detailed)

    Returns:
        Formatted string response

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(
        f"Describing table {full_table_name} "
        f"with lineage={include_lineage}, format={response_format}, detail={detail_level}"
    )

    # Get table details
    table = await make_api_request(
        "GET",
        f"/api/2.1/unity-catalog/tables/{full_table_name}"
    )

    lineage = None
    if include_lineage:
        try:
            # Get lineage from API
            lineage_result = await make_api_request(
                "GET",
                f"/api/2.1/unity-catalog/lineage-tracking/table-lineage/{full_table_name}"
            )
            # Process lineage data
            lineage = _process_lineage_data(lineage_result)
        except Exception as e:
            logger.warning(f"Failed to fetch lineage: {e}")
            lineage = {
                "error": str(e),
                "note": "Lineage requires access to system.access.table_lineage table"
            }

    if response_format == ResponseFormat.MARKDOWN:
        content = format_table_detail_markdown(table, lineage, detail_level)
    else:  # JSON
        table_dict = {
            "full_name": table.get("full_name"),
            "name": table.get("name"),
            "table_type": table.get("table_type"),
            "data_source_format": table.get("data_source_format"),
        }

        if detail_level == DetailLevel.DETAILED:
            table_dict.update({
                "comment": table.get("comment"),
                "storage_location": table.get("storage_location"),
                "owner": table.get("owner"),
                "created_at": table.get("created_at"),
            })
        elif table.get("comment"):
            table_dict["comment"] = table["comment"]

        if table.get("columns"):
            table_dict["columns"] = [
                {
                    "name": col.get("name"),
                    "type": col.get("type_name"),
                    "comment": col.get("comment"),
                    "nullable": col.get("nullable"),
                }
                for col in table["columns"]
            ]

        response_data = {"table": table_dict}
        if lineage:
            response_data["lineage"] = lineage

        content = json.dumps(response_data, indent=2)

    return apply_truncation_if_needed(content, response_format)


def _process_lineage_data(lineage_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process raw lineage data into a structured format.

    Args:
        lineage_result: Raw lineage data from API

    Returns:
        Processed lineage dictionary
    """
    # Extract upstream and downstream tables
    upstream_tables = lineage_result.get("upstream_tables", [])
    downstream_tables = lineage_result.get("downstream_tables", [])

    # Extract notebook and job information
    notebooks = []
    for entity in lineage_result.get("entities", []):
        if entity.get("entity_type") == "NOTEBOOK":
            notebooks.append({
                "name": entity.get("name"),
                "path": entity.get("path"),
                "job_id": entity.get("job_id"),
                "job_name": entity.get("job_name"),
                "operations": entity.get("operations", []),
            })

    return {
        "upstream_tables": upstream_tables,
        "downstream_tables": downstream_tables,
        "notebooks": notebooks,
    }

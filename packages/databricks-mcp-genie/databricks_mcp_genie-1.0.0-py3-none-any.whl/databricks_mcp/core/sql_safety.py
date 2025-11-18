"""
SQL safety validation utilities.

Provides validation to prevent destructive SQL operations and ensure
safe query execution for AI agent interactions.
"""

import re
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Destructive SQL keywords that should be blocked for read-only operations
DESTRUCTIVE_KEYWORDS = [
    "DROP",
    "DELETE",
    "TRUNCATE",
    "ALTER",
    "UPDATE",
    "INSERT",
    "MERGE",
    "CREATE",
    "REPLACE"
]

# Keywords that are allowed in subqueries but not as main operations
CONDITIONAL_KEYWORDS = ["CREATE", "INSERT", "REPLACE"]


class SQLSafetyError(Exception):
    """Raised when SQL query fails safety validation."""
    pass


def validate_read_only_sql(sql: str, strict_mode: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validate that SQL query is read-only.

    Args:
        sql: SQL query to validate
        strict_mode: If True, blocks all potentially destructive operations.
                    If False, allows CREATE TEMP TABLE and INSERT INTO TEMP.

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if query is safe, False otherwise
        - error_message: None if valid, error description if not

    Examples:
        >>> validate_read_only_sql("SELECT * FROM table")
        (True, None)

        >>> validate_read_only_sql("DROP TABLE table")
        (False, "SQL contains destructive operation 'DROP'. ...")

        >>> validate_read_only_sql("DELETE FROM table WHERE id = 1")
        (False, "SQL contains destructive operation 'DELETE'. ...")
    """
    # Normalize SQL: remove comments and extra whitespace
    normalized_sql = _normalize_sql(sql)

    # Check for destructive keywords
    keywords_to_check = DESTRUCTIVE_KEYWORDS if strict_mode else [
        kw for kw in DESTRUCTIVE_KEYWORDS if kw not in CONDITIONAL_KEYWORDS
    ]

    for keyword in keywords_to_check:
        if _contains_destructive_keyword(normalized_sql, keyword):
            error_msg = (
                f"SQL contains potentially destructive operation '{keyword}'. "
                f"This tool is designed for read-only queries (SELECT statements). "
            )

            if not strict_mode and keyword in CONDITIONAL_KEYWORDS:
                error_msg += (
                    f"If you need to use {keyword}, ensure it's for temporary tables only "
                    f"(CREATE TEMP TABLE, INSERT INTO TEMP)."
                )

            return False, error_msg

    # Additional checks for dangerous patterns
    dangerous_patterns = [
        (r";\s*DROP\s+", "Contains statement separator followed by DROP"),
        (r";\s*DELETE\s+", "Contains statement separator followed by DELETE"),
        (r";\s*TRUNCATE\s+", "Contains statement separator followed by TRUNCATE"),
    ]

    for pattern, description in dangerous_patterns:
        if re.search(pattern, normalized_sql, re.IGNORECASE):
            return False, f"SQL contains dangerous pattern: {description}"

    return True, None


def _normalize_sql(sql: str) -> str:
    """
    Normalize SQL by removing comments and extra whitespace.

    Args:
        sql: Raw SQL string

    Returns:
        Normalized SQL string
    """
    # Remove line comments (-- ...)
    sql = re.sub(r"--[^\n]*", "", sql)

    # Remove block comments (/* ... */)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)

    # Replace multiple whitespace with single space
    sql = re.sub(r"\s+", " ", sql)

    # Trim
    return sql.strip()


def _contains_destructive_keyword(sql: str, keyword: str) -> bool:
    """
    Check if SQL contains a destructive keyword as a standalone operation.

    This function attempts to distinguish between the keyword being used as
    a main operation vs. being part of a subquery or column name.

    Args:
        sql: Normalized SQL string
        keyword: Keyword to search for

    Returns:
        True if keyword is found as a main operation
    """
    # Create pattern that matches keyword as a whole word at statement boundaries
    # This helps avoid false positives like "SELECT created_at" matching "CREATE"
    pattern = rf"\b{keyword}\b"

    matches = list(re.finditer(pattern, sql, re.IGNORECASE))

    if not matches:
        return False

    # Check if any match is at a statement boundary (start of query or after semicolon)
    for match in matches:
        start_pos = match.start()

        # Check what comes before the keyword
        before = sql[:start_pos].strip()

        # Keyword at start of query
        if not before:
            return True

        # Keyword after semicolon (new statement)
        if before.endswith(";"):
            return True

        # For keywords like CREATE, INSERT, allow in WITH clauses or subqueries
        # but block at main statement level
        if keyword in CONDITIONAL_KEYWORDS:
            # Check if we're inside parentheses (subquery)
            open_parens = before.count("(")
            close_parens = before.count(")")
            if open_parens > close_parens:
                # We're inside a subquery, might be okay
                continue

            # Check for WITH clause
            if re.search(r"\bWITH\b", before, re.IGNORECASE):
                continue

            # Otherwise, it's a main statement
            return True

    # If we got here and keyword was found, it's likely destructive
    return len(matches) > 0


def suggest_safe_alternative(sql: str, error_message: str) -> str:
    """
    Suggest a safe alternative to a rejected SQL query.

    Args:
        sql: Original SQL query
        error_message: Error message from validation

    Returns:
        Helpful suggestion for the user
    """
    sql_upper = sql.upper()

    suggestions = []

    if "DROP" in sql_upper:
        suggestions.append(
            "Instead of DROP, use SELECT to query the table structure: "
            "DESCRIBE TABLE or SHOW COLUMNS FROM"
        )

    if "DELETE" in sql_upper or "TRUNCATE" in sql_upper:
        suggestions.append(
            "Instead of deleting data, use SELECT with WHERE clause to view the data you want to remove"
        )

    if "UPDATE" in sql_upper:
        suggestions.append(
            "Instead of UPDATE, use SELECT to view the data you want to modify"
        )

    if "INSERT" in sql_upper:
        suggestions.append(
            "Instead of INSERT, use SELECT to query existing data. "
            "If you need to insert data, use a separate write-enabled tool."
        )

    if suggestions:
        return "\n\nSuggestions:\n- " + "\n- ".join(suggestions)

    return "\n\nUse SELECT statements to query data without modifying it."


def check_sql_safety(sql: str, strict_mode: bool = True) -> None:
    """
    Check SQL safety and raise exception if invalid.

    This is a convenience wrapper around validate_read_only_sql that raises
    an exception on validation failure.

    Args:
        sql: SQL query to validate
        strict_mode: If True, blocks all potentially destructive operations

    Raises:
        SQLSafetyError: If SQL query is not safe

    Examples:
        >>> check_sql_safety("SELECT * FROM table")
        # No exception

        >>> check_sql_safety("DROP TABLE table")
        SQLSafetyError: SQL contains destructive operation 'DROP'. ...
    """
    is_valid, error_message = validate_read_only_sql(sql, strict_mode)

    if not is_valid:
        suggestion = suggest_safe_alternative(sql, error_message)
        raise SQLSafetyError(error_message + suggestion)


def sanitize_sql_for_logging(sql: str, max_length: int = 200) -> str:
    """
    Sanitize SQL for logging by removing sensitive data and truncating.

    Args:
        sql: SQL query to sanitize
        max_length: Maximum length of sanitized query

    Returns:
        Sanitized SQL string safe for logging
    """
    # Remove potential sensitive data patterns
    sanitized = re.sub(r"'[^']*'", "'***'", sql)  # Replace string literals
    sanitized = re.sub(r'"[^"]*"', '"***"', sanitized)  # Replace quoted identifiers

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... [truncated]"

    return sanitized

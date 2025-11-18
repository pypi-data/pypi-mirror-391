"""
API for Databricks Genie AI agent interactions.

Provides natural language data analysis through Genie AI conversations.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from databricks_mcp.core.utils import make_api_request, DatabricksAPIError

logger = logging.getLogger(__name__)

# Constants
GENIE_POLL_INTERVAL = 2  # Seconds between status polls
GENIE_MAX_WAIT = 300  # Maximum seconds to wait for response


async def list_genie_spaces() -> Dict[str, Any]:
    """
    List all available Genie spaces in the workspace.

    Returns:
        Response containing list of Genie spaces

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Listing Genie spaces")
    return await make_api_request("GET", "/api/2.0/genie/spaces")


async def start_conversation(
    space_id: str,
    question: str,
    wait_for_result: bool = True
) -> Dict[str, Any]:
    """
    Start a new conversation with Genie AI.

    Genie is Databricks' natural language data analysis AI. Ask questions in
    natural language and Genie will generate SQL, execute queries, and provide
    insights.

    Args:
        space_id: Genie space ID to use
        question: Natural language question to ask
        wait_for_result: If True, poll until result is ready. If False, return immediately.

    Returns:
        Response containing conversation_id, message_id, and optionally results

    Raises:
        DatabricksAPIError: If the API request fails
        TimeoutError: If wait_for_result=True and response takes too long
    """
    logger.info(f"Starting Genie conversation in space {space_id}")

    # Start conversation
    payload = {"content": question}
    response = await make_api_request(
        "POST",
        f"/api/2.0/genie/spaces/{space_id}/start-conversation",
        data=payload
    )

    conversation_id = response.get("conversation_id")
    message_id = response.get("message_id")

    if not conversation_id or not message_id:
        raise DatabricksAPIError("No conversation_id or message_id returned from Genie")

    # If not waiting, return immediately
    if not wait_for_result:
        return {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "status": "PENDING",
            "question": question
        }

    # Poll for completion
    return await _poll_for_message_completion(space_id, conversation_id, message_id, question)


async def send_followup_message(
    space_id: str,
    conversation_id: str,
    question: str,
    wait_for_result: bool = True
) -> Dict[str, Any]:
    """
    Send a follow-up message in an existing Genie conversation.

    Genie retains context from previous messages, so you can ask related
    questions without repeating information.

    Args:
        space_id: Genie space ID
        conversation_id: Conversation ID from previous interaction
        question: Follow-up question
        wait_for_result: If True, poll until result is ready

    Returns:
        Response containing message_id and optionally results

    Raises:
        DatabricksAPIError: If the API request fails
        TimeoutError: If wait_for_result=True and response takes too long
    """
    logger.info(f"Sending Genie follow-up in conversation {conversation_id}")

    # Send follow-up message
    payload = {"content": question}
    response = await make_api_request(
        "POST",
        f"/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages",
        data=payload
    )

    message_id = response.get("message_id")

    if not message_id:
        raise DatabricksAPIError("No message_id returned from Genie")

    # If not waiting, return immediately
    if not wait_for_result:
        return {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "status": "PENDING",
            "question": question
        }

    # Poll for completion
    return await _poll_for_message_completion(space_id, conversation_id, message_id, question)


async def get_message_status(
    space_id: str,
    conversation_id: str,
    message_id: str
) -> Dict[str, Any]:
    """
    Get the status of a Genie message.

    Args:
        space_id: Genie space ID
        conversation_id: Conversation ID
        message_id: Message ID to check

    Returns:
        Response containing message status and optionally results

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting Genie message status: {message_id}")
    return await make_api_request(
        "GET",
        f"/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
    )


async def get_query_results(
    space_id: str,
    conversation_id: str,
    message_id: str,
    attachment_id: str
) -> Dict[str, Any]:
    """
    Get query results from a Genie message.

    Args:
        space_id: Genie space ID
        conversation_id: Conversation ID
        message_id: Message ID
        attachment_id: Attachment ID containing results

    Returns:
        Response containing query results

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting Genie query results for attachment {attachment_id}")
    return await make_api_request(
        "GET",
        f"/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/query-result/{attachment_id}"
    )


async def _poll_for_message_completion(
    space_id: str,
    conversation_id: str,
    message_id: str,
    question: str,
    max_wait: int = GENIE_MAX_WAIT
) -> Dict[str, Any]:
    """
    Poll for Genie message completion.

    Args:
        space_id: Genie space ID
        conversation_id: Conversation ID
        message_id: Message ID to poll
        question: Original question asked
        max_wait: Maximum seconds to wait

    Returns:
        Response containing results

    Raises:
        TimeoutError: If polling exceeds max_wait
        DatabricksAPIError: If the API request fails
    """
    import time

    start_time = time.time()
    status = "PENDING"

    while status in ["PENDING", "EXECUTING_QUERY"]:
        # Check timeout
        if time.time() - start_time > max_wait:
            raise TimeoutError(
                f"Genie response timed out after {max_wait} seconds. "
                f"You can check status later with conversation_id={conversation_id}, message_id={message_id}"
            )

        # Wait before polling
        await asyncio.sleep(GENIE_POLL_INTERVAL)

        # Get message status
        status_response = await get_message_status(space_id, conversation_id, message_id)
        status = status_response.get("status", "UNKNOWN")

        if status == "COMPLETED":
            # Extract results
            attachments = status_response.get("attachments", [])
            sql = None
            results = None

            for attachment in attachments:
                if attachment.get("query"):
                    sql = attachment["query"].get("query")

                attachment_id = attachment.get("id")
                if attachment_id:
                    try:
                        query_result = await get_query_results(
                            space_id, conversation_id, message_id, attachment_id
                        )
                        if query_result.get("data_array"):
                            results = query_result
                    except Exception as e:
                        logger.warning(f"Failed to fetch query results: {e}")

            return {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "status": "COMPLETED",
                "question": question,
                "sql": sql,
                "results": results,
                "response": status_response.get("text", ""),
                "attachments": attachments
            }

        elif status in ["FAILED", "CANCELLED"]:
            error_message = status_response.get("error", {}).get("message", "Unknown error")
            raise DatabricksAPIError(
                f"Genie message failed: {error_message}",
                response=status_response
            )

    # If we exit loop without completion, return current status
    return {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "status": status,
        "question": question,
        "message": "Genie response not yet complete"
    }

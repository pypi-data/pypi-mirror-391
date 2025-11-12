from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import PostClient

tool_subawards = Tool(
    name="subawards",
    description="This returns a filtered set of subawards",
    inputSchema={
        "type": "object",
        "required": ["page", "sort", "order"],
        "properties": {
            "page": {"type": "number", "default": 1},
            "limit": {"type": "number", "default": 10},
            "sort": {
                "type": "string",
                "enum": [
                    "subaward_number",
                    "id",
                    "description",
                    "action_date",
                    "amount",
                    "recipient_name",
                ],
            },
            "order": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
            "award_id": {
                "type": "string",
                "description": (
                    "Either a generated natural award id or a database surrogate award id. "
                    "Generated award identifiers are preferred as they are effectively permanent. "
                    "Surrogate award ids retained for backward compatibility but are deprecated."
                ),
            },
        },
    },
)

response_schema = {
    "type": "object",
    "required": ["results", "page_metadata"],
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "subaward_number",
                    "description",
                    "action_date",
                    "amount",
                    "recipient_name",
                ],
                "properties": {
                    "id": {"type": "number"},
                    "subaward_number": {"type": "string"},
                    "description": {"type": "string"},
                    "action_date": {"type": "string"},
                    "amount": {"type": "number"},
                    "recipient_name": {"type": "string"},
                },
            },
        },
        "page_metadata": {
            "type": "object",
            "required": ["page", "next", "previous", "hasNext", "hasPrevious"],
            "properties": {
                "page": {"type": "number"},
                "next": {"type": ["number", "null"]},
                "previous": {"type": ["number", "null"]},
                "hasNext": {"type": "boolean"},
                "hasPrevious": {"type": "boolean"},
            },
        },
    },
}


async def call_tool_subawards(arguments: dict[str, Any]):
    endpoint = "/api/v2/subawards/"
    page = arguments.get("page")
    limit = arguments.get("limit")
    sort = arguments.get("sort")
    order = arguments.get("order")
    award_id = arguments.get("award_id")

    if page is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="page is a required argument",
            )
        )

    if sort is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="sort is a required argument",
            )
        )

    if order is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="order is a required argument",
            )
        )

    payload = {
        "page": page,
        "sort": sort,
        "order": order,
    }

    if limit is not None:
        payload["limit"] = limit

    if award_id is not None:
        payload["award_id"] = award_id

    post_client = PostClient(endpoint, payload, response_schema)
    return await post_client.send()

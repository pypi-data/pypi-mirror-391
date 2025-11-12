from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import PostClient

tool_spending = Tool(
    name="spending",
    description=(
        "This data can be used to drill down into specific subsets of data by level of detail. "
        "This data represents all government spending in the specified time period, "
        "grouped by the data type of your choice."
    ),
    inputSchema={
        "type": "object",
        "required": ["type", "filters"],
        "properties": {
            "type": {
                "type": "string",
                "enum": [
                    "federal_account",
                    "object_class",
                    "recipient",
                    "award",
                    "budget_function",
                    "budget_subfunction",
                    "agency",
                    "program_activity",
                ],
            },
            "filters": {
                "type": "object",
                "required": ["fy"],
                "properties": {
                    "fy": {"type": "string"},
                    "quarter": {"type": "string", "enum": ["1", "2", "3", "4"]},
                    "period": {
                        "type": "string",
                        "enum": [
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                            "6",
                            "7",
                            "8",
                            "9",
                            "10",
                            "11",
                            "12",
                        ],
                    },
                    "agency": {"type": "number"},
                    "federal_account": {"type": "number"},
                    "object_class": {"type": "number"},
                    "budget_function": {"type": "number"},
                    "budget_subfunction": {"type": "number"},
                    "recipient": {"type": "number"},
                    "program_activity": {"type": "number"},
                },
            },
        },
    },
)

response_schema = {
    "type": "object",
    "required": ["total", "end_date", "results"],
    "properties": {
        "total": {"type": ["number", "null"]},
        "end_date": {"type": "string"},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["code", "id", "type", "name", "amount"],
                "properties": {
                    "code": {"type": "string"},
                    "id": {"type": "string"},
                    "generated_unique_number_id": {"type": "string"},
                    "type": {"type": "string"},
                    "name": {"type": "string"},
                    "amount": {"type": "number"},
                    "account_number": {"type": "string"},
                    "link": {"type": "string"},
                },
            },
        },
    },
}


async def call_tool_spending(arguments: dict[str, Any]):
    endpoint = "/api/v2/spending/"
    spending_type = arguments.get("type")
    filters = arguments.get("filters")
    if spending_type is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="type is a required argument",
            )
        )

    if not bool(filters):
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="filters is a required argument",
            )
        )

    payload = {
        "type": spending_type,
        "filters": filters,
    }

    post_client = PostClient(endpoint, payload, response_schema)
    return await post_client.send()

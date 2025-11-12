from typing import Any

from mcp.types import Tool

from utils.http import PostClient

tool_recipient = Tool(
    name="recipient",
    description=(
        "This can be used to visualize government spending that pertains to a specific recipient. "
        "This returns a list of recipients, their level, DUNS, UEI, and amount."
    ),
    inputSchema={
        "type": "object",
        "required": [],
        "properties": {
            "order": {"type": "string", "enum": ["asc", "desc"]},
            "sort": {"type": "string", "enum": ["name", "duns", "amount"]},
            "limit": {"type": "number"},
            "page": {"type": "number"},
            "keyword": {
                "type": "string",
                "description": (
                    "They keyword results are filtered by. Searches on name, UEI, or DUNS"
                ),
            },
            "award_type": {
                "type": "string",
                "enum": [
                    "all",
                    "contracts",
                    "grants",
                    "loans",
                    "direct_payments",
                    "other_financial_assistance",
                ],
            },
        },
    },
)

response_schema = {
    "type": "object",
    "required": [],
    "properties": {
        "page_metadata": {
            "type": "object",
            "required": ["page", "limit", "total"],
            "properties": {
                "page": {"type": "number"},
                "limit": {"type": "number"},
                "total": {"type": "number"},
            },
        },
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "duns", "uei", "id", "recipient_level"],
                "properties": {
                    "name": {
                        "type": ["string", "null"],
                        "description": "Name of the recipient. null when the name is not provided",
                    },
                    "duns": {
                        "type": ["string", "null"],
                        "description": (
                            "Recipient's DUNS (Data Universal Numbering System) number. "
                            "null when no DUNS is provided"
                        ),
                    },
                    "uei": {
                        "type": ["string", "null"],
                        "description": (
                            "Recipient's UEI (Unique Entity Identifier). "
                            "null when no UEI is provided"
                        ),
                    },
                    "amount": {
                        "type": "number",
                        "description": (
                            "The aggregate monetary value of all "
                            "transactions associated with this recipient "
                            "for the trailing 12 months."
                        ),
                    },
                    "recipient_level": {
                        "type": "string",
                        "enum": ["R", "P", "C"],
                        "description": (
                            "A letter representing the recipient level. "
                            "R for neither parent nor child. "
                            "P for Parent recipient, or C for child recipient"
                        ),
                    },
                },
            },
        },
    },
}


async def call_tool_recipient(arguments: dict[str, Any]):
    endpoint = "/api/v2/recipient/"
    order = arguments.get("order")
    sort = arguments.get("sort")
    limit = arguments.get("limit")
    page = arguments.get("page")
    keyword = arguments.get("keyword")
    award_type = arguments.get("award_type")

    payload = {}
    if order is not None:
        payload["order"] = order
    if sort is not None:
        payload["sort"] = sort
    if limit is not None:
        payload["limit"] = limit
    if page is not None:
        payload["page"] = page
    if keyword is not None:
        payload["keyword"] = keyword
    if award_type is not None:
        payload["award_type"] = award_type

    post_client = PostClient(endpoint, payload, response_schema)
    return await post_client.send()

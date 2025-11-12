from typing import Any

from mcp.types import Tool

from utils.http import PostClient

tool_federal_accounts = Tool(
    name="federal_accounts",
    description=(
        "This returns a list of federal accounts, their number, name, managing agency, "
        "and budgetary resources"
    ),
    inputSchema={
        "type": "object",
        "required": [],
        "properties": {
            "filters": {
                "type": "object",
                "required": [],
                "properties": {
                    "fy": {"type": "string"},
                    "agency_identifier": {"type": "string"},
                },
            },
            "sort": {
                "type": "object",
                "required": [],
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                    }
                },
            },
            "limit": {
                "type": "number",
                "description": "The number of results to include per page. The default is 50",
            },
            "keyword": {
                "type": "string",
                "description": (
                    "They keyword that you want to search on. "
                    "Can be used to search by name, number, managing agency, "
                    "and budgetary resources"
                ),
            },
        },
    },
)

response_schema = {
    "type": "object",
    "required": [
        "count",
        "limit",
        "hasNext",
        "page",
        "hasPrevious",
        "next",
        "fy",
        "results",
    ],
    "properties": {
        "previous": {"type": ["number", "null"]},
        "count": {"type": "number"},
        "limit": {"type": "number"},
        "hasNext": {"type": "boolean"},
        "page": {"type": "number"},
        "hasPrevious": {"type": "boolean"},
        "next": {"type": ["number", "null"]},
        "fy": {"type": "string"},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "account_name",
                    "account_number",
                    "account_id",
                    "managing_agency_acronym",
                    "agency_identifier",
                    "budgetary_resources",
                    "managing_agency",
                ],
                "properties": {
                    "account_name": {
                        "type": ["string", "null"],
                        "description": (
                            "Name of the federal account. "
                            "null when the name is not provided"
                        ),
                    },
                    "account_number": {
                        "type": ["string", "null"],
                        "description": (
                            "The number for the federal account. "
                            "null when no account number is provided"
                        ),
                    },
                    "account_id": {
                        "type": "number",
                        "description": "A unique identifier for the federal account",
                    },
                    "managing_agency_acronym": {"type": "string"},
                    "managing_agency": {"type": "string"},
                },
            },
        },
    },
}


async def call_tool_federal_accounts(arguments: dict[str, Any]):
    endpoint = "/api/v2/federal_accounts/"
    filters = arguments.get("filters")
    sort = arguments.get("sort")
    limit = arguments.get("limit")
    page = arguments.get("page")
    keyword = arguments.get("keyword")

    payload = {}
    if bool(filters):
        payload["filters"] = filters
    if bool(sort):
        payload["sort"] = sort
    if limit is not None:
        payload["limit"] = limit
    if page is not None:
        payload["page"] = page
    if keyword is not None:
        payload["keyword"] = keyword

    post_client = PostClient(endpoint, payload, response_schema)
    return await post_client.send()

from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import GetClient

tool_total_budgetary_resources = Tool(
    name="total_budgetary_resources",
    description=(
        "This is used to provide information on the federal budgetary resources of the government"
    ),
    inputSchema={
        "type": "object",
        "required": [],
        "properties": {
            "fiscal_year": {
                "type": "number",
                "description": "The fiscal year to retrieve, 2017 or later",
            },
            "fiscal_period": {
                "type": "number",
                "description": "The fiscal period",
            },
        },
    },
)

response_schema = {
    "type": "object",
    "properties": {
        "messages": {"type": "array", "items": {"type": "string"}},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "fiscal_year",
                    "fiscal_period",
                    "total_budgetary_resources",
                ],
                "properties": {
                    "fiscal_year": {
                        "type": "number",
                    },
                    "fiscal_period": {
                        "type": "number",
                    },
                    "total_budgetary_resources": {"type": "number"},
                },
            },
        },
    },
}


async def call_tool_total_budgetary_resources(arguments: dict[str, Any]):
    fiscal_year = arguments.get("fiscal_year")
    fiscal_period = arguments.get("fiscal_period")
    if fiscal_period is not None and fiscal_year is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="If fiscal_period is provided then fiscal_year must be provided as well",
            )
        )

    params = {}
    if fiscal_year is not None:
        params["fiscal_year"] = fiscal_year
    if fiscal_period is not None:
        params["fiscal_period"] = fiscal_period

    endpoint = "/api/v2/references/total_budgetary_resources/"
    get_client = GetClient(endpoint, params, response_schema)
    return await get_client.send()

from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from tools.v2.search.config import advanced_filter_object
from utils.http import PostClient

tool_spending_over_time = Tool(
    name="spending_over_time",
    description=(
        "This returns a list of aggregated award amounts grouped by time period "
        "in ascending order (earliest to most recent)"
    ),
    inputSchema={
        "type": "object",
        "required": ["group", "filters"],
        "properties": {
            "group": {
                "type": "string",
                "enum": ["calendar_year", "fiscal_year", "quarter", "month"],
                "default": "fiscal_year",
            },
            "filters": advanced_filter_object,
            "subawards": {
                "type": "boolean",
                "description": "True to group by sub-awards instead of prime awards.",
                "default": False,
            },
            "spending_level": {
                "type": "string",
                "enum": ["transactions", "awards", "subawards"],
                "description": (
                    "Group the spending by level. "
                    "This also determines what data source is used for the totals."
                ),
                "default": "transactions",
            }
        }
    }
)

response_schema = {
    "type": "object",
    "required": ["group", "spending_level", "results", "messages"],
    "properties": {
        "group": {
            "type": "string",
            "enum": ["calendar_year", "fiscal_year", "quarter", "month"],
        },
        "spending_level": {
            "type": "string",
            "enum": ["transactions", "awards", "subawards"],
        },
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "time_period",
                    "aggregated_amount",
                    "Contract_Obligations",
                    "Loan_Obligations",
                    "Idv_Obligations",
                    "Grant_Obligations",
                    "Direct_Obligations",
                    "Other_Obligations",
                    "total_outlays",
                    "Contract_Outlays",
                    "Loan_Outlays",
                    "Idv_Outlays",
                    "Grant_Outlays",
                    "Direct_Outlays",
                    "Other_Outlays"
                ],
                "properties": {
                    "time_period": {
                        "type": "object",
                        "properties": {
                            "calendar_year": { "type": "string" },
                            "fiscal_year": { "type": "string" },
                            "quarter": { "type": "string" },
                            "month": { "type": "string" },
                        }
                    },
                    "aggregated_amount": { "type": "number" },
                    "Contract_Obligations": { "type": "number" },
                    "Loan_Obligations": { "type": "number" },
                    "Idv_Obligations": { "type": "number" },
                    "Grant_Obligations": { "type": "number" },
                    "Direct_Obligations": { "type": "number" },
                    "Other_Obligations": { "type": "number" },
                    "total_outlays": { "type": ["number", "null"] },
                    "Contract_Outlays": { "type": ["number", "null"] },
                    "Loan_Outlays": { "type": ["number", "null"] },
                    "Idv_Outlays": { "type": ["number", "null"] },
                    "Grant_Outlays": { "type": ["number", "null"] },
                    "Direct_Outlays": { "type": ["number", "null"] },
                    "Other_Outlays": { "type": ["number", "null"] },
                }
            }
        },
        "messages": { "type": "array", "items": { "type": "string" } }
    }
}

async def call_tool_spending_over_time(arguments: dict[str, Any]):
    endpoint = "/api/v2/search/spending_over_time/"
    group = arguments.get("group")
    filters = arguments.get("filters")
    subawards = arguments.get("subawards")
    spending_level = arguments.get("spending_level")

    if not group:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="groups is a required argument",
        ))

    if not bool(filters):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="filters is a required argument",
        ))

    payload = {
        "group": group,
        "filters": filters,
    }

    if subawards is not None:
        payload["subawards"] = subawards
    if spending_level is not None:
        payload["spending_level"] = spending_level

    post_client = await PostClient(endpoint, payload, response_schema)
    return post_client.send()

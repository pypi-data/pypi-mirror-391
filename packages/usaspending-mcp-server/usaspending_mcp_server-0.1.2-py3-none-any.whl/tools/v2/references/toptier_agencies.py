from typing import Any

from mcp.types import Tool

from utils.http import GetClient

tool_toptier_agencies = Tool(
    name="toptier_agencies",
    description=(
        "This data can be used to better understand the different ways "
        "that a specific agency spends money"
    ),
    inputSchema={
        "type": "object",
        "required": [],
        "properties": {
            "sort": {
                "type": "string",
                "description": "A data field used to sort the response array",
                "enum": [
                    "agency_id",
                    "agency_name",
                    "active_fy",
                    "active_fq",
                    "outlay_amount",
                    "obligated_amount",
                    "budget_authority_amount",
                    "current_total_budget_authority_amount",
                    "percentage_of_total_budget_authority",
                ],
            },
            "order": {
                "type": "string",
                "description": "The direction that the sort field will be sorted in",
                "enum": ["asc", "desc"],
            },
        },
    },
)

response_schema = {
    "type": "object",
    "required": ["results"],
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "abbreviation",
                    "active_fq",
                    "active_fy",
                    "agency_id",
                    "agency_name",
                    "budget_authority_amount",
                    "congressional_justification_url",
                    "current_total_budget_authority_amount",
                    "obligated_amount",
                    "outlay_amount",
                    "percentage_of_total_budget_authority",
                    "toptier_code",
                    "agency_slug",
                ],
                "properties": {
                    "abbreviation": {"type": "string"},
                    "active_fq": {"type": "string"},
                    "active_fy": {"type": "string"},
                    "agency_id": {
                        "type": "number",
                        "description": (
                            "The unique identifier for the agency. "
                            "This is used in other endpoints when requesting "
                            "detailed information about this specific agency"
                        ),
                    },
                    "agency_name": {"type": "string"},
                    "budget_authority_amount": {"type": "number"},
                    "congressional_justification_url": {"type": ["string", "null"]},
                    "obligated_amount": {"type": "number"},
                    "outlay_amount": {"type": "number"},
                    "percentage_of_total_budget_authority": {
                        "type": "number",
                        "description": (
                            "This is the percentage of the agency's budget authority "
                            "compared to the total budget authority"
                        ),
                    },
                    "toptier_code": {"type": "string"},
                    "agency_slug": {
                        "type": "string",
                        "description": (
                            "The name of the agency in lowercase with dashed "
                            "to be used for profile link construction"
                        ),
                    },
                },
            },
        }
    },
}


async def call_tool_toptier_agencies(arguments: dict[str, Any]):
    sort = arguments.get("sort")
    order = arguments.get("desc")
    params = {}
    if sort is not None:
        params["sort"] = sort
    if order is not None:
        params["order"] = order

    endpoint = "/api/v2/references/toptier_agencies/"
    get_client = GetClient(endpoint, params, response_schema)
    return await get_client.send()

from copy import deepcopy
from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from tools.v2.search.config import advanced_filter_object
from utils.http import PostClient

award_advanced_filter_object = deepcopy(advanced_filter_object)
award_advanced_filter_object['required'] = ['award_type_codes']

spending_by_award_fields_enum = [
    "Award ID",
    "Recipient Name",
    "Recipient DUNS Number",
    "recipient_id",
    "Awarding Agency",
    "Awarding Agency Code",
    "Awarding Sub Agency",
    "Awarding Sub Agency Code",
    "Funding Agency",
    "Funding Agency Code",
    "Funding Sub Agency",
    "Funding Sub Agency Code",
    "Place of Performance City Code",
    "Place of Performance State Code",
    "Place of Performance Country Code",
    "Place of Performance Zip5",
    "Description",
    "Last Modified Date",
    "Base Obligation Date",
    "prime_award_recipient_id",
    "generated_internal_id",
    "def_codes",
    "COVID-19 Obligations",
    "COVID-19 Outlays",
    "Infrastructure Obligations",
    "Infrastructure Outlays",
    "Recipient UEI",
    "Recipient Location",
    "Primary Place of Performance",
]


spending_by_award_fields = {
    "type": "array",
    "default": spending_by_award_fields_enum,
    "items": {
        "type": "string",
    },
}

# Used in the request payload to sort results
spending_by_award_response_properties = [
    "internal_id",
    "Award Amount",
    "Total Outlays",
    "Award ID",
    "Award Type",
    "Awarding Agency Code",
    "Awarding Agency",
    "awarding_agency_id",
    "Awarding Sub Agency CodeAwarding Sub Agency",
    "Base Obligation DateCFDA NumberContract Award Type",
    "Description",
    "End Date",
    "Funding Agency Code",
    "Funding Agency",
    "Funding Sub Agency Code",
    "Funding Sub Agency",
    "generated_internal_id",
    "Issued Date",
    "Last Date to Order",
    "Last Modified Date",
    "Loan Value",
    "Period of Performance Current End Date",
    "Period of Performance Start Date",
    "Place of Performance City Code",
    "Place of Performance Country Code",
    "Place of Performance State Code",
    "Place of Performance Zip5",
    "COVID-19 Outlays",
    "COVID-19 Obligations",
    "Infrastructure Outlays",
    "Infrastructure Obligations",
    "def_codes",
    "Prime Award ID",
    "Prime Recipient Name",
    "prime_award_recipient_id",
    "prime_award_internal_id",
    "prime_award_generated_internal_id",
    "Recipient DUNS Number",
    "Recipient Name",
    "recipient_id",
    "SAI Number",
    "Start Date",
    "Sub-Award Amount",
    "Sub-Award Date",
    "Sub-Award ID",
    "Sub-Award Type",
    "Sub-Awardee Name",
    "Subsidy Cost",
    "agency_slug",
]

"""
We are going to take a different approach for this tool versus spending_by_geography.
I am not adding every single filter property.
Since I am worried a more complex input schema may overwhelm the LLM.
Weird, initially I didn't event supply recipient_search_text.
Regardless, the LLM still tried to use it in a query so I added it.
"""
tool_spending_by_award = Tool(
    name="spending_by_award",
    description=(
        "This allows for complex filtering for specific subsets of spending data. "
        "This accepts filters and fields, and returns the fields of the filtered awards."
    ),
    inputSchema={
        "type": "object",
        "required": ["filters", "fields"],
        "properties": {
            "filters": award_advanced_filter_object,
            "fields": spending_by_award_fields,
            "limit": {
                "type": "number",
                "description": "How many results are returned.",
                "default": 10,
            },
            "order": {
                "type": "string",
                "enum": ["asc", "desc"],
                "default": "desc",
                "description": "Indicates what direction results should be sorted by.",
            },
            "sort": {
                "type": "string",
                "description": "What value the results should be sorted by.",
                "enum": spending_by_award_response_properties,
            },
            "page": {"type": "string"},
            "subawards": {
                "type": "boolean",
                "description": "True when you want to group by Subawards instead of Awards",
                "default": False,
            },
            "spending_level": {
                "type": "string",
                "description": (
                    "Group the spending by level. "
                    "This also determines what data source is used for the totals"
                ),
                "enum": ["awards", "subawards"],
                "default": "awards",
            },
        },
    },
)

response_schema = {
    "type": "object",
    "required": ["spending_level", "limit", "results"],
    "properties": {
        "spending_level": {
            "type": "string",
            "enum": ["awards", "subawards"],
        },
        "limit": {"type": "number"},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["internal_id"],
                "properties": {
                    "internal_id": {"type": "number"},
                    "Award Amount": {"type": "number"},
                    "Total Outlays": {"type": "number"},
                    "Award ID": {"type": "string"},
                    "Award Type": {"type": ["string", "null"]},
                    "Awarding Agency Code": {"type": ["string", "null"]},
                    "Awarding Agency": {"type": ["string", "null"]},
                    "awarding_agency_id": {"type": ["number", "null"]},
                    "Awarding Sub Agency Code": {"type": ["string", "null"]},
                    "Awarding Sub Agency": {"type": ["string", "null"]},
                    "Base Obligation Date": {"type": "string"},
                    "CFDA Number": {"type": ["string", "null"]},
                    "Contract Award Type": {"type": "string"},
                    "Description": {"type": ["string", "null"]},
                    "End Date": {"type": "string"},
                    "Funding Agency Code": {"type": ["string", "null"]},
                    "Funding Agency": {"type": ["string", "null"]},
                    "Funding Sub Agency Code": {"type": ["string", "null"]},
                    "Funding Sub Agency": {"type": ["string", "null"]},
                    "generated_internal_id": {"type": "string"},
                    "Issued Date": {"type": ["string", "null"]},
                    "Last Date to Order": {"type": ["string", "null"]},
                    "Last Modified Date": {"type": "string"},
                    "Loan Value": {"type": ["number"]},
                    "Period of Performance Current End Date": {
                        "type": ["string", "null"]
                    },
                    "Period of Performance Start Date": {"type": "string"},
                    "Place of Performance City Code": {"type": "number"},
                    "Place of Performance Country Code": {"type": ["string", "null"]},
                    "Place of Performance State Code": {"type": ["number", "null"]},
                    "Place of Performance Zip5": {"type": "number"},
                    "COVID-19 Outlays": {"type": ["number"]},
                    "COVID-19 Obligations": {"type": ["number"]},
                    "Infrastructure Outlays": {"type": ["number"]},
                    "Infrastructure Obligations": {"type": ["number"]},
                    "def_codes": {"type": "array", "items": {"type": "string"}},
                    "Prime Award ID": {"type": ["string", "null"]},
                    "Prime Recipient Name": {"type": ["string", "null"]},
                    "prime_award_recipient_id": {"type": ["string", "null"]},
                    "prime_award_internal_id": {"type": ["string", "null"]},
                    "prime_award_generated_internal_id": {"type": ["string"]},
                    "Recipient DUNS Number": {"type": ["string", "null"]},
                    "Recipient Name": {"type": ["string", "null"]},
                    "recipient_id": {"type": ["string", "null"]},
                    "SAI Number": {"type": ["string", "null"]},
                    "Start Date": {"type": "string"},
                    "Sub-Award Amount": {"type": ["string"]},
                    "Sub-Award Date": {"type": ["string"]},
                    "Sub-Award ID": {"type": ["string"]},
                    "Sub-Award Type": {"type": ["string"]},
                    "Sub-Awardee Name": {"type": ["string"]},
                    "Subsidy Cost": {"type": ["number"]},
                    "agency_slug": {"type": ["string", "null"]},
                },
            },
        },
        "page_metadata": {
            "type": "object",
            "required": ["page", "hasNext"],
            "properties": {
                "page": {"type": "number"},
                "hasNext": {"type": "boolean"},
            },
        },
        "messages": {"type": "array", "items": {"type": "string"}},
    },
}


async def call_tool_spending_by_award(arguments: dict[str, Any]):
    endpoint = "/api/v2/search/spending_by_award/"
    filters = arguments.get("filters")
    fields = arguments.get("fields")
    limit = arguments.get("limit")
    order = arguments.get("order")
    page = arguments.get("page")
    sort = arguments.get("sort")
    subawards = arguments.get("subawards")
    spending_level = arguments.get("spending_level")

    if not bool(filters) or fields is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="filters and fields are required arguments",
            )
        )

    payload = {
        "filters": filters,
        "fields": fields,
    }

    if limit is not None:
        payload["limit"] = limit
    if order is not None:
        payload["order"] = order
    if page is not None:
        payload["page"] = page
    if sort is not None:
        payload["sort"] = sort
    if subawards is not None:
        payload["subawards"] = subawards
    if spending_level is not None:
        payload["spending_level"] = spending_level

    post_client = PostClient(endpoint, payload, response_schema)
    return await post_client.send()

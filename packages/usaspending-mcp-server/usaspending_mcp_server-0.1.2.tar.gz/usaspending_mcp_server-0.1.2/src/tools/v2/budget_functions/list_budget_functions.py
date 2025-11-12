from mcp.types import Tool

from utils.http import GetClient

tool_list_budget_functions = Tool(
    name="list_budget_functions",
    description="This retrieves a list of all Budget Functions ordered by their title",
    inputSchema={"type": "object", "properties": {}},
)

response_schema = {
    "type": "object",
    "required": ["results"],
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["budget_function_code", "budget_function_title"],
                "properties": {
                    "budget_function_code": {"type": "string"},
                    "budget_function_title": {"type": "string"},
                },
            },
        }
    },
}


async def call_tool_list_budget_functions():
    endpoint = "/api/v2/budget_functions/list_budget_functions/"
    get_client = GetClient(endpoint=endpoint, response_schema=response_schema)
    return await get_client.send()

from httpx import AsyncClient
from jsonschema import validate
from mcp.shared.exceptions import McpError
from mcp.types import (
    INTERNAL_ERROR,
    ErrorData,
    TextContent,
)


class HttpClient:
    api_url = "https://api.usaspending.gov"
    client = AsyncClient()

    def __init__(self, endpoint, payload, response_schema):
        self.endpoint = endpoint
        self.payload = payload
        self.response_schema = response_schema

    def validate_response(self, response):
        if self.response_schema is None:
            return

        try:
            payload = response.json()
            validate(instance=payload, schema=self.response_schema)
        except Exception as e:
            print(f"Warning the response did not contain the expected information {e}")
            pass

    def handle_response(self, response) -> list[TextContent]:
        if response.status_code >= 200 and response.status_code < 300:
            print(response.text)
            self.validate_response(response)
            return [
                TextContent(
                    type="text",
                    text=response.text,
                )
            ]
        else:
            print(
                f"Non 2xx status code received {response.status_code} "
                f"with response payload {response.text}"
            )
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=(
                        f"Received unacceptable status code {response.status_code} "
                        f"with response payload {response.text}"
                    ),
                )
            )


class PostClient(HttpClient):
    def __init__(self, endpoint, payload=None, response_schema=None):
        self.endpoint = endpoint
        self.payload = payload
        self.response_schema = response_schema

    async def send(self):
        try:
            print(
                f"Sending POST request to {self.endpoint} with request payload {self.payload}"
            )
            response = await self.client.post(
                f"{self.api_url}{self.endpoint}", json=self.payload
            )
            return self.handle_response(response)
        except Exception as e:
            print(e)
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"The following error occurred in the MCP server {e}",
                )
            ) from e


class GetClient(HttpClient):
    def __init__(self, endpoint, params=None, response_schema=None):
        self.endpoint = endpoint
        self.params = params
        self.response_schema = response_schema

    async def send(self):
        try:
            print(f"Sending GET request to {self.endpoint} with params {self.params}")
            response = await self.client.get(
                f"{self.api_url}{self.endpoint}", params=self.params
            )
            return self.handle_response(response)
        except Exception as e:
            print(e)
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"The following error occurred in the MCP server {e}",
                )
            ) from e

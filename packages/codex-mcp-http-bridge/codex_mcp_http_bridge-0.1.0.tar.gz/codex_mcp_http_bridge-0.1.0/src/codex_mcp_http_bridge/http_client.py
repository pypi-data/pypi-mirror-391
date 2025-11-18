"""
HTTP client for communicating with remote MCP servers.
"""

import asyncio
import logging
from typing import Any, Optional

import httpx
from pydantic import BaseModel

from .config import ServerConfig

logger = logging.getLogger(__name__)


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request format."""

    jsonrpc: str = "2.0"
    id: Optional[int | str] = None
    method: str
    params: Optional[dict[str, Any]] = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response format."""

    jsonrpc: str = "2.0"
    id: Optional[int | str] = None
    result: Optional[Any] = None
    error: Optional[dict[str, Any]] = None


class MCPHTTPClient:
    """HTTP client for MCP server communication with OAuth authentication."""

    def __init__(self, server_config: ServerConfig):
        """Initialize the HTTP client.

        Args:
            server_config: Server configuration including URL and access token
        """
        self.server_config = server_config
        self.client: Optional[httpx.AsyncClient] = None
        self._request_counter = 0

    async def __aenter__(self) -> "MCPHTTPClient":
        """Enter async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        await self.disconnect()

    async def connect(self) -> None:
        """Establish connection to the MCP server."""
        if self.client is not None:
            return  # Already connected

        headers = {
            "Authorization": f"Bearer {self.server_config.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "codex-mcp-http-bridge/0.1.0",
        }

        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(120.0),  # 2 minutes for long-running tools
            follow_redirects=True,
        )

        logger.info(f"Connected to MCP server: {self.server_config.url}")

    async def disconnect(self) -> None:
        """Close the connection to the MCP server."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None
            logger.info("Disconnected from MCP server")

    def _get_next_request_id(self) -> int:
        """Get the next request ID."""
        self._request_counter += 1
        return self._request_counter

    async def send_request(
        self,
        method: str,
        params: Optional[dict[str, Any]] = None,
        request_id: Optional[int | str] = None
    ) -> JSONRPCResponse:
        """Send a JSON-RPC request to the MCP server.

        Args:
            method: The JSON-RPC method name
            params: Optional parameters for the method
            request_id: Optional request ID (auto-generated if not provided)

        Returns:
            JSONRPCResponse from the server

        Raises:
            RuntimeError: If not connected
            httpx.HTTPError: If HTTP request fails
            ValueError: If response is invalid
        """
        if self.client is None:
            raise RuntimeError("Not connected. Call connect() first.")

        # Auto-generate request ID if not provided
        if request_id is None:
            request_id = self._get_next_request_id()

        # Build JSON-RPC request
        request = JSONRPCRequest(
            jsonrpc="2.0",
            id=request_id,
            method=method,
            params=params
        )

        logger.debug(f"Sending request: {method} (id={request_id})")

        try:
            # Send POST request
            response = await self.client.post(
                self.server_config.url,
                json=request.model_dump(mode="json", exclude_none=True)
            )

            # Handle HTTP errors
            if response.status_code == 401:
                raise ValueError(
                    "Authentication failed. Access token may be invalid or expired.\n"
                    "Run 'codex-mcp-http-bridge setup' to update your token."
                )
            elif response.status_code == 403:
                raise ValueError(
                    "Access forbidden. You may not have permission to access this server."
                )
            elif response.status_code == 404:
                raise ValueError(
                    "MCP server not found. Check the URL in your configuration."
                )
            elif response.status_code >= 500:
                raise ValueError(
                    f"Server error (HTTP {response.status_code}). The MCP server may be down."
                )

            response.raise_for_status()

            # Parse JSON-RPC response
            response_data = response.json()
            json_rpc_response = JSONRPCResponse(**response_data)

            # Check for JSON-RPC error
            if json_rpc_response.error:
                error_message = json_rpc_response.error.get("message", "Unknown error")
                error_code = json_rpc_response.error.get("code", -1)
                raise ValueError(
                    f"MCP server returned error (code {error_code}): {error_message}"
                )

            logger.debug(f"Received response for request {request_id}")
            return json_rpc_response

        except httpx.HTTPError as e:
            logger.error(f"HTTP error communicating with MCP server: {e}")
            raise
        except Exception as e:
            logger.error(f"Error sending request to MCP server: {e}")
            raise

    async def initialize(self, client_info: dict[str, Any]) -> dict[str, Any]:
        """Send initialize request to MCP server.

        Args:
            client_info: Client information including name and version

        Returns:
            Server capabilities and information
        """
        response = await self.send_request(
            method="initialize",
            params=client_info
        )

        if response.result is None:
            raise ValueError("Initialize response missing result")

        return response.result

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools from the MCP server.

        Returns:
            List of tool definitions
        """
        response = await self.send_request(
            method="tools/list",
            params={}
        )

        if response.result is None:
            raise ValueError("tools/list response missing result")

        return response.result.get("tools", [])

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> Any:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool execution result
        """
        response = await self.send_request(
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": arguments
            }
        )

        if response.result is None:
            raise ValueError("tools/call response missing result")

        return response.result

    async def list_resources(self) -> list[dict[str, Any]]:
        """List available resources from the MCP server.

        Returns:
            List of resource definitions
        """
        response = await self.send_request(
            method="resources/list",
            params={}
        )

        if response.result is None:
            raise ValueError("resources/list response missing result")

        return response.result.get("resources", [])

    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the MCP server.

        Args:
            uri: Resource URI

        Returns:
            Resource contents
        """
        response = await self.send_request(
            method="resources/read",
            params={"uri": uri}
        )

        if response.result is None:
            raise ValueError("resources/read response missing result")

        return response.result

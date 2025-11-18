"""
stdio MCP server that bridges requests to HTTP MCP servers.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Optional

from .config import ServerConfig
from .http_client import MCPHTTPClient

logger = logging.getLogger(__name__)


class MCPStdioServer:
    """stdio MCP server that proxies requests to HTTP MCP servers."""

    def __init__(self, server_config: ServerConfig):
        """Initialize the stdio server.

        Args:
            server_config: Configuration for the remote HTTP MCP server
        """
        self.server_config = server_config
        self.http_client: Optional[MCPHTTPClient] = None
        self.running = False

    async def start(self) -> None:
        """Start the stdio server and connect to the remote MCP server."""
        logger.info("Starting MCP stdio server...")
        logger.info(f"Connecting to: {self.server_config.url}")

        # Connect to remote MCP server
        self.http_client = MCPHTTPClient(self.server_config)
        await self.http_client.connect()

        self.running = True
        logger.info("MCP stdio server started successfully")

    async def stop(self) -> None:
        """Stop the stdio server and disconnect from the remote MCP server."""
        logger.info("Stopping MCP stdio server...")
        self.running = False

        if self.http_client:
            await self.http_client.disconnect()
            self.http_client = None

        logger.info("MCP stdio server stopped")

    def _read_message(self) -> Optional[dict[str, Any]]:
        """Read a JSON-RPC message from stdin.

        Returns:
            Parsed JSON message or None if EOF

        Raises:
            ValueError: If message is invalid JSON
        """
        try:
            line = sys.stdin.readline()

            if not line:
                # EOF reached
                return None

            line = line.strip()
            if not line:
                # Empty line, skip
                return self._read_message()

            try:
                message = json.loads(line)
                return message
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                logger.error(f"Line: {line}")
                # Send error response
                self._write_error_response(None, -32700, "Parse error")
                return self._read_message()

        except Exception as e:
            logger.error(f"Error reading from stdin: {e}")
            return None

    def _write_message(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.

        Args:
            message: JSON-RPC message to write
        """
        try:
            json_str = json.dumps(message, separators=(',', ':'))
            sys.stdout.write(json_str + "\n")
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Error writing to stdout: {e}", exc_info=True)

    def _write_response(
        self,
        request_id: Optional[int | str],
        result: Any
    ) -> None:
        """Write a JSON-RPC success response to stdout.

        Args:
            request_id: Request ID from the original request
            result: Result data
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        self._write_message(response)

    def _write_error_response(
        self,
        request_id: Optional[int | str],
        code: int,
        message: str,
        data: Optional[Any] = None
    ) -> None:
        """Write a JSON-RPC error response to stdout.

        Args:
            request_id: Request ID from the original request
            code: Error code
            message: Error message
            data: Optional additional error data
        """
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data

        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error
        }
        self._write_message(response)

    async def _handle_request(self, message: dict[str, Any]) -> None:
        """Handle a JSON-RPC request from stdin.

        Args:
            message: JSON-RPC request message
        """
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})

        if not method:
            self._write_error_response(
                request_id,
                -32600,
                "Invalid request: missing method"
            )
            return

        logger.debug(f"Handling request: {method} (id={request_id})")

        try:
            if self.http_client is None:
                raise RuntimeError("Not connected to remote MCP server")

            # Forward request to HTTP MCP server
            response = await self.http_client.send_request(
                method=method,
                params=params if params else None,
                request_id=request_id
            )

            # Check if response has error
            if response.error:
                self._write_error_response(
                    request_id,
                    response.error.get("code", -32603),
                    response.error.get("message", "Internal error"),
                    response.error.get("data")
                )
            else:
                # Send success response
                self._write_response(request_id, response.result)

        except ValueError as e:
            # Client-side error (auth, not found, etc.)
            logger.error(f"Error handling request: {e}")
            self._write_error_response(
                request_id,
                -32603,
                str(e)
            )
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error handling request: {e}", exc_info=True)
            self._write_error_response(
                request_id,
                -32603,
                f"Internal error: {str(e)}"
            )

    async def _handle_notification(self, message: dict[str, Any]) -> None:
        """Handle a JSON-RPC notification from stdin.

        Notifications don't have an ID and don't expect a response.

        Args:
            message: JSON-RPC notification message
        """
        method = message.get("method")
        params = message.get("params", {})

        if not method:
            logger.warning("Invalid notification: missing method")
            return

        logger.debug(f"Handling notification: {method}")

        try:
            if self.http_client is None:
                raise RuntimeError("Not connected to remote MCP server")

            # Forward notification to HTTP MCP server
            # Notifications don't have IDs and don't expect responses
            await self.http_client.send_request(
                method=method,
                params=params if params else None,
                request_id=None
            )

        except Exception as e:
            # Log error but don't send response (notifications are one-way)
            logger.error(f"Error handling notification: {e}", exc_info=True)

    async def run(self) -> None:
        """Run the stdio server main loop.

        Reads JSON-RPC messages from stdin and forwards them to the HTTP MCP server.
        """
        await self.start()

        try:
            while self.running:
                # Read message from stdin (blocking)
                # We use asyncio.to_thread to avoid blocking the event loop
                message = await asyncio.to_thread(self._read_message)

                if message is None:
                    # EOF or error, stop server
                    logger.info("EOF received, stopping server")
                    break

                # Check if it's a request or notification
                if "id" in message:
                    # Request - expects a response
                    await self._handle_request(message)
                else:
                    # Notification - no response expected
                    await self._handle_notification(message)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}", exc_info=True)
        finally:
            await self.stop()


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration.

    All logs go to stderr to avoid interfering with stdio JSON-RPC communication.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr  # IMPORTANT: Use stderr, not stdout
    )


async def run_stdio_server(server_config: ServerConfig, log_level: str = "INFO") -> None:
    """Run the stdio MCP server.

    Args:
        server_config: Configuration for the remote HTTP MCP server
        log_level: Logging level
    """
    setup_logging(log_level)

    server = MCPStdioServer(server_config)
    await server.run()

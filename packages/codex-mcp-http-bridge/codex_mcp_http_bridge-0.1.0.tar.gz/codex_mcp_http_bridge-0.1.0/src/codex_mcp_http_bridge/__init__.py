"""
Codex MCP HTTP Bridge

A stdio-to-HTTP bridge that allows OpenAI Codex to connect to remote MCP servers
via HTTPS with OAuth 2.1 authentication.
"""

__version__ = "0.1.0"
__author__ = "GuruCloudAI"
__email__ = "support@gurucloudai.com"

from .config import BridgeConfig, ServerConfig
from .http_client import MCPHTTPClient
from .stdio_server import MCPStdioServer

__all__ = [
    "BridgeConfig",
    "ServerConfig",
    "MCPHTTPClient",
    "MCPStdioServer",
]

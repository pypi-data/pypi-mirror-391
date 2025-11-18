"""
Configuration management for the MCP HTTP Bridge.
"""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ServerConfig(BaseModel):
    """Configuration for a single MCP server."""

    url: str = Field(..., description="MCP server URL (e.g., https://gurucloudai.com/mcp/{server_id}/mcp)")
    access_token: str = Field(..., description="OAuth Bearer token for authentication")
    description: Optional[str] = Field(None, description="Human-readable description of this server")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL is HTTPS (except localhost)."""
        if not v.startswith(("https://", "http://localhost", "http://127.0.0.1")):
            raise ValueError("MCP server URL must use HTTPS (except for localhost)")
        return v

    @field_validator("access_token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate that token is not empty."""
        if not v or not v.strip():
            raise ValueError("Access token cannot be empty")
        return v.strip()


class BridgeConfig(BaseModel):
    """Main configuration for the MCP HTTP Bridge."""

    servers: dict[str, ServerConfig] = Field(
        default_factory=dict,
        description="Map of server names to their configurations"
    )

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "BridgeConfig":
        """Load configuration from a JSON file.

        Args:
            config_path: Path to config file. If None, uses default location.

        Returns:
            BridgeConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if config_path is None:
            config_path = cls.get_default_config_path()

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Run 'codex-mcp-http-bridge setup' to create it."
            )

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading config: {e}")

    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to a JSON file.

        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            config_path = self.get_default_config_path()

        # Create parent directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config with nice formatting
        with open(config_path, "w") as f:
            json.dump(
                self.model_dump(mode="json", exclude_none=True),
                f,
                indent=2
            )

        # Set restrictive permissions (owner read/write only)
        os.chmod(config_path, 0o600)

    @staticmethod
    def get_default_config_path() -> Path:
        """Get the default configuration file path.

        Returns:
            Path to ~/.codex-mcp-bridge/config.json
        """
        return Path.home() / ".codex-mcp-bridge" / "config.json"

    @staticmethod
    def get_example_config() -> "BridgeConfig":
        """Get an example configuration for documentation purposes.

        Returns:
            Example BridgeConfig with placeholder values
        """
        return BridgeConfig(
            servers={
                "my-knowledge-base": ServerConfig(
                    url="https://www.gurucloudai.com/mcp/{server_id}/mcp",
                    access_token="your-personal-access-token-here",
                    description="My GuruCloudAI Knowledge Base"
                ),
                "my-database-server": ServerConfig(
                    url="https://www.gurucloudai.com/mcp/{another_server_id}/mcp",
                    access_token="same-or-different-token",
                    description="Database Tools"
                )
            }
        )

    def get_server(self, server_name: str) -> ServerConfig:
        """Get configuration for a specific server.

        Args:
            server_name: Name of the server

        Returns:
            ServerConfig for the requested server

        Raises:
            KeyError: If server not found in configuration
        """
        if server_name not in self.servers:
            available = ", ".join(self.servers.keys()) if self.servers else "none"
            raise KeyError(
                f"Server '{server_name}' not found in configuration. "
                f"Available servers: {available}"
            )
        return self.servers[server_name]

    def add_server(self, name: str, url: str, access_token: str, description: Optional[str] = None) -> None:
        """Add a new server to the configuration.

        Args:
            name: Unique name for this server
            url: MCP server URL
            access_token: OAuth Bearer token
            description: Optional description

        Raises:
            ValueError: If server name already exists
        """
        if name in self.servers:
            raise ValueError(f"Server '{name}' already exists in configuration")

        self.servers[name] = ServerConfig(
            url=url,
            access_token=access_token,
            description=description
        )

    def remove_server(self, name: str) -> None:
        """Remove a server from the configuration.

        Args:
            name: Name of the server to remove

        Raises:
            KeyError: If server not found
        """
        if name not in self.servers:
            raise KeyError(f"Server '{name}' not found in configuration")

        del self.servers[name]

    def list_servers(self) -> list[str]:
        """Get list of configured server names.

        Returns:
            List of server names
        """
        return list(self.servers.keys())

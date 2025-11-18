"""
Tests for configuration management.
"""

import json
import tempfile
from pathlib import Path

import pytest

from codex_mcp_http_bridge.config import BridgeConfig, ServerConfig


def test_server_config_valid():
    """Test creating a valid ServerConfig."""
    config = ServerConfig(
        url="https://example.com/mcp",
        access_token="test-token",
        description="Test server"
    )
    assert config.url == "https://example.com/mcp"
    assert config.access_token == "test-token"
    assert config.description == "Test server"


def test_server_config_localhost_allowed():
    """Test that localhost URLs are allowed."""
    config = ServerConfig(
        url="http://localhost:8000/mcp",
        access_token="test-token"
    )
    assert config.url == "http://localhost:8000/mcp"


def test_server_config_http_not_allowed():
    """Test that non-localhost HTTP URLs are rejected."""
    with pytest.raises(ValueError, match="must use HTTPS"):
        ServerConfig(
            url="http://example.com/mcp",
            access_token="test-token"
        )


def test_server_config_empty_token():
    """Test that empty tokens are rejected."""
    with pytest.raises(ValueError, match="cannot be empty"):
        ServerConfig(
            url="https://example.com/mcp",
            access_token=""
        )


def test_bridge_config_empty():
    """Test creating an empty BridgeConfig."""
    config = BridgeConfig()
    assert config.servers == {}
    assert config.list_servers() == []


def test_bridge_config_with_servers():
    """Test creating BridgeConfig with servers."""
    config = BridgeConfig(
        servers={
            "server1": ServerConfig(
                url="https://example.com/mcp/1",
                access_token="token1"
            ),
            "server2": ServerConfig(
                url="https://example.com/mcp/2",
                access_token="token2"
            )
        }
    )
    assert len(config.servers) == 2
    assert "server1" in config.servers
    assert "server2" in config.servers


def test_bridge_config_get_server():
    """Test getting a server from config."""
    config = BridgeConfig(
        servers={
            "test": ServerConfig(
                url="https://example.com/mcp",
                access_token="token"
            )
        }
    )
    server = config.get_server("test")
    assert server.url == "https://example.com/mcp"
    assert server.access_token == "token"


def test_bridge_config_get_server_not_found():
    """Test getting a non-existent server."""
    config = BridgeConfig()
    with pytest.raises(KeyError, match="Server 'missing' not found"):
        config.get_server("missing")


def test_bridge_config_add_server():
    """Test adding a server to config."""
    config = BridgeConfig()
    config.add_server(
        name="new-server",
        url="https://example.com/mcp",
        access_token="token",
        description="Test"
    )
    assert "new-server" in config.servers
    server = config.get_server("new-server")
    assert server.url == "https://example.com/mcp"
    assert server.description == "Test"


def test_bridge_config_add_duplicate_server():
    """Test that adding a duplicate server raises an error."""
    config = BridgeConfig()
    config.add_server("test", "https://example.com/mcp", "token")

    with pytest.raises(ValueError, match="already exists"):
        config.add_server("test", "https://example.com/mcp", "token")


def test_bridge_config_remove_server():
    """Test removing a server from config."""
    config = BridgeConfig()
    config.add_server("test", "https://example.com/mcp", "token")
    assert "test" in config.servers

    config.remove_server("test")
    assert "test" not in config.servers


def test_bridge_config_remove_nonexistent_server():
    """Test that removing a non-existent server raises an error."""
    config = BridgeConfig()
    with pytest.raises(KeyError, match="not found"):
        config.remove_server("missing")


def test_bridge_config_save_and_load():
    """Test saving and loading configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"

        # Create and save config
        config1 = BridgeConfig()
        config1.add_server(
            "test",
            "https://example.com/mcp",
            "secret-token",
            "Test server"
        )
        config1.save(config_path)

        # Load config
        config2 = BridgeConfig.load(config_path)

        # Verify
        assert len(config2.servers) == 1
        server = config2.get_server("test")
        assert server.url == "https://example.com/mcp"
        assert server.access_token == "secret-token"
        assert server.description == "Test server"


def test_bridge_config_load_not_found():
    """Test loading a non-existent config file."""
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        BridgeConfig.load(Path("/nonexistent/config.json"))


def test_bridge_config_load_invalid_json():
    """Test loading invalid JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config_path.write_text("{ invalid json")

        with pytest.raises(ValueError, match="Invalid JSON"):
            BridgeConfig.load(config_path)


def test_example_config():
    """Test that example config is valid."""
    config = BridgeConfig.get_example_config()
    assert len(config.servers) > 0
    for name, server in config.servers.items():
        assert server.url
        assert server.access_token
        assert server.description

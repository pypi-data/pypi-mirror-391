"""
Command-line interface for the MCP HTTP Bridge.
"""

import asyncio
import sys
from pathlib import Path

import click

from .config import BridgeConfig, ServerConfig
from .http_client import MCPHTTPClient
from .stdio_server import run_stdio_server


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Codex MCP HTTP Bridge - Connect Codex to remote MCP servers via HTTPS."""
    pass


@main.command()
@click.option(
    "--server",
    "-s",
    required=True,
    help="Name of the server to run (from config file)"
)
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    help="Logging level"
)
def run(server: str, log_level: str) -> None:
    """Run the bridge for a specific server.

    This command is typically called by Codex via stdio.
    """
    try:
        # Load configuration
        config = BridgeConfig.load()

        # Get server configuration
        server_config = config.get_server(server)

        # Run stdio server
        asyncio.run(run_stdio_server(server_config, log_level))

    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nRun 'codex-mcp-http-bridge setup' to create a configuration.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Fatal error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--config-path",
    "-c",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to config file (default: ~/.codex-mcp-bridge/config.json)"
)
def setup(config_path: Path | None) -> None:
    """Interactive setup wizard to configure MCP servers."""
    click.echo("🚀 Codex MCP HTTP Bridge Setup\n")

    try:
        # Try to load existing config
        try:
            config = BridgeConfig.load(config_path)
            click.echo("✓ Found existing configuration\n")
        except FileNotFoundError:
            config = BridgeConfig()
            click.echo("Creating new configuration\n")

        # Interactive setup
        while True:
            click.echo("\nWhat would you like to do?")
            click.echo("  1. Add a new server")
            click.echo("  2. List configured servers")
            click.echo("  3. Remove a server")
            click.echo("  4. Save and exit")

            choice = click.prompt("\nChoice", type=click.IntRange(1, 4))

            if choice == 1:
                # Add server
                click.echo("\n--- Add New Server ---")
                name = click.prompt("Server name (e.g., 'my-knowledge-base')")

                if name in config.servers:
                    if not click.confirm(f"Server '{name}' already exists. Overwrite?"):
                        continue

                url = click.prompt("MCP server URL")
                access_token = click.prompt("Access token (will be hidden)", hide_input=True)
                description = click.prompt("Description (optional)", default="", show_default=False)

                try:
                    server_config = ServerConfig(
                        url=url,
                        access_token=access_token,
                        description=description if description else None
                    )
                    config.servers[name] = server_config
                    click.echo(f"✓ Added server '{name}'")
                except Exception as e:
                    click.echo(f"✗ Error: {e}", err=True)

            elif choice == 2:
                # List servers
                if not config.servers:
                    click.echo("\nNo servers configured yet.")
                else:
                    click.echo("\n--- Configured Servers ---")
                    for name, srv in config.servers.items():
                        desc = f" - {srv.description}" if srv.description else ""
                        click.echo(f"  • {name}{desc}")
                        click.echo(f"    URL: {srv.url}")

            elif choice == 3:
                # Remove server
                if not config.servers:
                    click.echo("\nNo servers configured yet.")
                    continue

                click.echo("\n--- Remove Server ---")
                for i, name in enumerate(config.list_servers(), 1):
                    click.echo(f"  {i}. {name}")

                idx = click.prompt(
                    "Select server to remove",
                    type=click.IntRange(1, len(config.servers))
                )
                name = config.list_servers()[idx - 1]

                if click.confirm(f"Remove server '{name}'?"):
                    config.remove_server(name)
                    click.echo(f"✓ Removed server '{name}'")

            elif choice == 4:
                # Save and exit
                break

        # Save configuration
        config.save(config_path)
        config_file = config_path or BridgeConfig.get_default_config_path()
        click.echo(f"\n✓ Configuration saved to {config_file}")

        # Show next steps
        click.echo("\n📝 Next Steps:")
        click.echo("1. Test your connection:")
        for name in config.list_servers():
            click.echo(f"   codex-mcp-http-bridge test --server {name}")
        click.echo("\n2. Generate Codex configuration:")
        click.echo("   codex-mcp-http-bridge codex-config >> ~/.codex/config.toml")
        click.echo("\n3. Restart Codex to load the new servers")

    except KeyboardInterrupt:
        click.echo("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\nError during setup: {e}", err=True)
        sys.exit(1)


@main.command()
def list() -> None:
    """List all configured servers."""
    try:
        config = BridgeConfig.load()

        if not config.servers:
            click.echo("No servers configured.")
            click.echo("Run 'codex-mcp-http-bridge setup' to add servers.")
            return

        click.echo("Configured MCP servers:\n")
        for name, server in config.servers.items():
            desc = f" - {server.description}" if server.description else ""
            click.echo(f"  • {name}{desc}")
            click.echo(f"    URL: {server.url}")
            click.echo()

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("Run 'codex-mcp-http-bridge setup' to create a configuration.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--server",
    "-s",
    required=True,
    help="Name of the server to test"
)
async def test(server: str) -> None:
    """Test connection to an MCP server."""
    try:
        config = BridgeConfig.load()
        server_config = config.get_server(server)

        click.echo(f"Testing connection to '{server}'...")
        click.echo(f"URL: {server_config.url}\n")

        async with MCPHTTPClient(server_config) as client:
            # Test initialize
            click.echo("1. Testing initialize...")
            result = await client.initialize({
                "name": "codex-mcp-http-bridge-test",
                "version": "0.1.0"
            })
            click.echo(f"   ✓ Server name: {result.get('serverInfo', {}).get('name', 'Unknown')}")

            # Test list tools
            click.echo("\n2. Testing tools/list...")
            tools = await client.list_tools()
            click.echo(f"   ✓ Found {len(tools)} tools:")
            for tool in tools[:5]:  # Show first 5 tools
                click.echo(f"     - {tool.get('name', 'Unknown')}")
            if len(tools) > 5:
                click.echo(f"     ... and {len(tools) - 5} more")

            # Test list resources (optional)
            try:
                click.echo("\n3. Testing resources/list...")
                resources = await client.list_resources()
                click.echo(f"   ✓ Found {len(resources)} resources")
            except Exception:
                click.echo("   ℹ Server doesn't support resources")

        click.echo("\n✓ All tests passed!")

    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Test failed: {e}", err=True)
        sys.exit(1)


# Wrap async test command
@main.command(name="test")
@click.option("--server", "-s", required=True, help="Name of the server to test")
def test_sync(server: str) -> None:
    """Test connection to an MCP server."""
    asyncio.run(test(server))


@main.command(name="codex-config")
def codex_config() -> None:
    """Generate Codex configuration snippet."""
    try:
        config = BridgeConfig.load()

        if not config.servers:
            click.echo("No servers configured.", err=True)
            click.echo("Run 'codex-mcp-http-bridge setup' to add servers.", err=True)
            sys.exit(1)

        click.echo("# Add this to your ~/.codex/config.toml:\n")

        for name in config.list_servers():
            click.echo(f"[mcp_servers.{name}]")
            click.echo('command = "python"')
            click.echo(f'args = ["-m", "codex_mcp_http_bridge", "run", "--server", "{name}"]')
            click.echo('env = { LOG_LEVEL = "info" }')
            click.echo('startup_timeout_sec = 30')
            click.echo('tool_timeout_sec = 120')
            click.echo()

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("Run 'codex-mcp-http-bridge setup' to create a configuration.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional

import click
import uvicorn
import yaml
from rich.console import Console
from sqlalchemy import select

from .database import init_db, get_session
from .models import Settings
from .tunnel_client import TunnelClient
from .dashboard import app as dashboard_app
from .utils import normalize_server_url, generate_random_subdomain


console = Console()

# Default server URL - hardcoded
DEFAULT_SERVER_URL = "wss://tunnel.tunneloon.online"


def load_config(path: Optional[str]) -> dict:
    cfg_path = path or str(Path(__file__).with_name("client_config.yaml"))
    if Path(cfg_path).exists():
        with open(cfg_path, "r") as f:
            return yaml.safe_load(f)
    return {}


async def get_or_create_settings() -> tuple[Optional[str], Optional[int], str]:
    """Get server_url, local_port, and subdomain from Settings, or generate defaults."""
    async for session in get_session():
        res = await session.execute(select(Settings).order_by(Settings.id.asc()))
        settings = res.scalars().first()
        
        server_url = None
        local_port = None
        subdomain = None
        
        if settings:
            server_url = settings.server_url
            local_port = settings.local_port
            subdomain = settings.selected_subdomain
        
        # If missing, generate random subdomain
        if not subdomain:
            subdomain = generate_random_subdomain()
            if settings:
                settings.selected_subdomain = subdomain
                await session.commit()
            else:
                new_settings = Settings(selected_subdomain=subdomain)
                session.add(new_settings)
                await session.commit()
        
        return server_url, local_port, subdomain


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--server", "server", "-s", type=str, required=False, hidden=True, help="Server URL override (advanced, not recommended)")
@click.option("--port", "port", "-p", type=int, required=False, help="Local port to expose")
@click.option("--config", "config_path", type=str, required=False, help="Path to client_config.yaml (advanced)")
def cli(ctx: click.Context, server: Optional[str], port: Optional[int], config_path: Optional[str]):
    """Tunnel client for tunnel.tunneloon.online"""
    # If no subcommand was invoked, run start by default
    if ctx.invoked_subcommand is None:
        ctx.invoke(start, server=server, port=port, config_path=config_path)


@cli.command()
@click.option("--server", "server", "-s", type=str, required=False, hidden=True, help="Server URL override (advanced, not recommended)")
@click.option("--port", "port", "-p", type=int, required=False, help="Local port to expose")
@click.option("--config", "config_path", type=str, required=False, help="Path to client_config.yaml (advanced)")
def start(server: Optional[str], port: Optional[int], config_path: Optional[str]):
    """
    Start tunnel client and local dashboard.
    
    Simplest usage:
        tunnel-client --port 3000
    
    Server is pre-configured to tunnel.tunneloon.online.
    If port not specified, uses settings from dashboard.
    """
    cfg = load_config(config_path)
    
    # Load settings from DB
    async def load_settings():
        await init_db(cfg.get("database", {}).get("path"))
        return await get_or_create_settings()
    
    db_server_url, db_local_port, db_subdomain = asyncio.run(load_settings())
    
    # Server URL: CLI override -> DB -> default (hardcoded)
    if server:
        # Only allow override for advanced users
        server_url = normalize_server_url(server)
        console.print(f"[yellow]Warning:[/yellow] Using custom server URL: {server_url}")
    else:
        # Use default hardcoded server
        server_url = DEFAULT_SERVER_URL
    
    if port is None:
        port = db_local_port or cfg.get("client", {}).get("local_port")
    
    if not port:
        console.print("[red]Error:[/red] Local port is required. Use --port or configure in dashboard.")
        return
    
    # Use subdomain from DB (might be auto-generated)
    subdomain = db_subdomain or generate_random_subdomain()
    
    dashboard_enabled = cfg.get("dashboard", {}).get("enabled", True)
    dashboard_port = int(cfg.get("dashboard", {}).get("port", 8080))

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    
    # Save settings to DB for future use (server_url is not saved, it's hardcoded)
    async def save_settings():
        async for session in get_session():
            res = await session.execute(select(Settings).order_by(Settings.id.asc()))
            settings = res.scalars().first()
            if not settings:
                settings = Settings()
                session.add(settings)
            
            # Don't save server_url - it's hardcoded
            settings.local_port = port
            settings.selected_subdomain = subdomain
            await session.commit()
    
    asyncio.run(save_settings())
    
    console.print(f"[green]🚀 Starting tunnel...[/green]")
    console.print(f"[blue]Server:[/blue] {server_url}")
    console.print(f"[blue]WebSocket:[/blue] {server_url}/tunnel/connect")
    console.print(f"[blue]Subdomain:[/blue] {subdomain}")
    console.print(f"[blue]Public URL:[/blue] https://{subdomain}.tunnel.tunneloon.online")
    console.print(f"[blue]Local:[/blue] localhost:{port}")
    console.print(f"[yellow]Dashboard:[/yellow] http://127.0.0.1:{dashboard_port}")
    console.print(f"[dim]Managing tunnel via dashboard at http://127.0.0.1:{dashboard_port}[/dim]")

    async def runner():
        client = TunnelClient()
        tasks: list[asyncio.Task] = []
        tunnel_task = asyncio.create_task(client.connect(server_url, subdomain, port))
        tasks.append(tunnel_task)
        server_obj = None
        if dashboard_enabled:
            dashboard_app.state.local_port = port
            dashboard_app.state.tunnel_client = client  # Store reference for status checks
            dashboard_app.state.connection_status = "connecting"  # Initial status
            config = uvicorn.Config(dashboard_app, host="127.0.0.1", port=dashboard_port, log_level="info")
            server_obj = uvicorn.Server(config)
            server_task = asyncio.create_task(server_obj.serve())
            tasks.append(server_task)

        try:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        except asyncio.CancelledError:
            pass
        finally:
            await client.stop()
            if server_obj is not None:
                server_obj.should_exit = True
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        console.print("[red]Shutting down...[/red]")


@cli.command()
@click.option("--server", "server", "-S", type=str, required=False, default=None, hidden=True, help="Server URL override (advanced)")
def list(server: Optional[str]):
    """List registered domains via server API."""
    import httpx
    base_url = "https://tunnel.tunneloon.online"
    if server:
        base = server.replace("ws://", "http://").replace("wss://", "https://")
        base = base.replace("http://", "https://")
    else:
        base = base_url
    try:
        resp = httpx.get(f"{base}/api/domains", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        domains = data.get("domains", [])
        if not domains:
            console.print("[yellow]No domains found[/yellow]")
        else:
            console.print("[green]Domains:[/green] " + ", ".join(domains))
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    cli()



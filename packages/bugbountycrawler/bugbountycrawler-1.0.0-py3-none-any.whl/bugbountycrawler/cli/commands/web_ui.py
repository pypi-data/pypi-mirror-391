"""Web UI command for BugBountyCrawler CLI."""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
import uvicorn

from ...core.config import get_settings

console = Console()

app = typer.Typer(name="web", help="Start web UI")


@app.command()
def start(
    host: Optional[str] = typer.Option(None, "--host", help="Host to bind to"),
    port: Optional[int] = typer.Option(None, "--port", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
) -> None:
    """Start the web UI server."""
    
    try:
        settings = get_settings()
        
        # Use settings or command line arguments
        host = host or settings.web_host
        port = port or settings.web_port
        
        console.print(f"[blue]Starting web UI on {host}:{port}[/blue]")
        
        # Show startup info
        info_panel = Panel(
            f"Web UI Server\n\n"
            f"URL: http://{host}:{port}\n"
            f"Host: {host}\n"
            f"Port: {port}\n"
            f"Reload: {reload}\n\n"
            f"Press Ctrl+C to stop",
            title="BugBountyCrawler Web UI",
            border_style="blue"
        )
        console.print(info_panel)
        
        # Start server
        uvicorn.run(
            "bugbountycrawler.api.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Web UI stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting web UI: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

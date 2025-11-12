"""Database initialization command."""

import typer
from rich.console import Console
from rich.panel import Panel

from ...database.connection import init_database, reset_database
from ...core.logger import setup_logging, get_logger

console = Console()
logger = get_logger(__name__)

app = typer.Typer(name="init-db", help="Initialize database")


@app.command()
def init(
    reset: bool = typer.Option(False, "--reset", help="Reset database (drop and recreate)"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompts"),
) -> None:
    """Initialize the database."""
    
    try:
        # Setup logging
        from ...core.config import get_settings
        settings = get_settings()
        setup_logging(settings)
        
        if reset:
            if not force:
                if not typer.confirm("This will delete all existing data. Continue?"):
                    console.print("Operation cancelled.")
                    return
            
            console.print("[blue]Resetting database...[/blue]")
            reset_database()
            console.print("[green]Database reset successfully![/green]")
        else:
            console.print("[blue]Initializing database...[/blue]")
            init_database()
            console.print("[green]Database initialized successfully![/green]")
        
        # Show database info
        info_panel = Panel(
            "Database tables created:\n"
            "• users\n"
            "• programs\n"
            "• scans\n"
            "• targets\n"
            "• findings\n"
            "• scan_logs\n"
            "• audit_logs",
            title="Database Status",
            border_style="green"
        )
        console.print(info_panel)
        
    except Exception as e:
        console.print(f"[red]Error initializing database: {str(e)}[/red]")
        logger.error(f"Database initialization error: {str(e)}", exc_info=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

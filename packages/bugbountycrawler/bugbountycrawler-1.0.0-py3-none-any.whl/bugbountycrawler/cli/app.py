"""Main CLI application for BugBountyCrawler."""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .commands import scan, web_ui, init_db, create_user, list_programs, create_program

# Create console for rich output
console = Console()

# Create main app
app = typer.Typer(
    name="bugbounty",
    help="BugBountyCrawler - A production-ready, legal, modular BugBountyCrawler for ethical bug bounty hunting",
    add_completion=False,
    rich_markup_mode="rich",
)

# Add subcommands
app.add_typer(scan.app, name="scan", help="Scan targets for vulnerabilities")
app.add_typer(web_ui.app, name="web", help="Start web UI")
app.add_typer(init_db.app, name="init-db", help="Initialize database")
app.add_typer(create_user.app, name="create-user", help="Create user account")
app.add_typer(list_programs.app, name="list-programs", help="List bug bounty programs")
app.add_typer(create_program.app, name="create-program", help="Create bug bounty program")


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Show version and exit"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Enable verbose output"
    ),
) -> None:
    """
    BugBountyCrawler - Ethical Bug Bounty Hunting Tool
    
    A production-ready, legal, modular tool for automated reconnaissance
    and scanning in bug bounty programs. Prioritizes safety, accuracy,
    and responsible disclosure.
    
    ⚠️  LEGAL DISCLAIMER: Only use on targets you own or have explicit
    written permission to test. Comply with all applicable laws and
    regulations.
    """
    if version:
        from .. import __version__
        console.print(f"BugBountyCrawler version {__version__}")
        raise typer.Exit()
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)


@app.command()
def info() -> None:
    """Show information about BugBountyCrawler."""
    
    # Create info panel
    info_text = Text()
    info_text.append("BugBountyCrawler\n", style="bold blue")
    info_text.append("Version: 1.0.0\n", style="green")
    info_text.append("Author: BugBountyCrawler Team\n\n", style="green")
    
    info_text.append("Features:\n", style="bold yellow")
    info_text.append("• Legal scope enforcement\n", style="white")
    info_text.append("• Safe, non-destructive scanning\n", style="white")
    info_text.append("• Human-in-the-loop approval\n", style="white")
    info_text.append("• Rate limiting and politeness\n", style="white")
    info_text.append("• Comprehensive reporting\n", style="white")
    info_text.append("• Plugin architecture\n\n", style="white")
    
    info_text.append("Legal Notice:\n", style="bold red")
    info_text.append("Only use on authorized targets!\n", style="red")
    info_text.append("Comply with all applicable laws and regulations.\n", style="red")
    
    panel = Panel(
        info_text,
        title="BugBountyCrawler Information",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)


@app.command()
def status() -> None:
    """Show system status."""
    
    from ..core.config import get_settings
    from ..database.connection import get_database
    
    settings = get_settings()
    
    # Check database connection
    try:
        db = next(get_database())
        db_status = "✅ Connected"
    except Exception as e:
        db_status = f"❌ Error: {str(e)}"
    
    # Create status panel
    status_text = Text()
    status_text.append("System Status\n\n", style="bold blue")
    
    status_text.append("Database: ", style="bold")
    status_text.append(f"{db_status}\n", style="green" if "✅" in db_status else "red")
    
    status_text.append("Data Directory: ", style="bold")
    status_text.append(f"{settings.data_dir}\n", style="white")
    
    status_text.append("Reports Directory: ", style="bold")
    status_text.append(f"{settings.reports_dir}\n", style="white")
    
    status_text.append("Rate Limit: ", style="bold")
    status_text.append(f"{settings.default_rate_limit} req/s\n", style="white")
    
    status_text.append("Max Concurrent: ", style="bold")
    status_text.append(f"{settings.max_concurrent}\n", style="white")
    
    panel = Panel(
        status_text,
        title="BugBountyCrawler Status",
        border_style="green",
        padding=(1, 2)
    )
    
    console.print(panel)


if __name__ == "__main__":
    app()

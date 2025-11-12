"""List programs command."""

import typer
from rich.console import Console
from rich.table import Table

from ...database.connection import init_database, get_database
from ...models.program import Program
from ...core.logger import setup_logging, get_logger

console = Console()
logger = get_logger(__name__)

app = typer.Typer(name="list-programs", help="List bug bounty programs")


@app.command()
def list() -> None:
    """List all bug bounty programs."""
    
    try:
        # Setup
        from ...core.config import get_settings
        settings = get_settings()
        setup_logging(settings)
        init_database()
        
        # Get programs from database
        db = next(get_database())
        programs = db.query(Program).all()
        
        if not programs:
            console.print("[yellow]No programs found[/yellow]")
            return
        
        # Create table
        table = Table(title="Bug Bounty Programs")
        table.add_column("Name", style="cyan")
        table.add_column("Platform", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="red")
        table.add_column("Findings", style="blue")
        table.add_column("Created", style="magenta")
        
        for program in programs:
            status = "Active" if program.status == "active" else "Inactive"
            table.add_row(
                program.name,
                program.platform,
                program.program_type,
                status,
                str(program.total_findings),
                program.created_at.strftime("%Y-%m-%d")
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing programs: {str(e)}[/red]")
        logger.error(f"Program listing error: {str(e)}", exc_info=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

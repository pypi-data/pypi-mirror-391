"""Create program command."""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import json

from ...database.connection import init_database, get_database
from ...models.program import Program, ProgramScope
from ...core.logger import setup_logging, get_logger

console = Console()
logger = get_logger(__name__)

app = typer.Typer(name="create-program", help="Create bug bounty program")


@app.command()
def create(
    name: Optional[str] = typer.Option(None, "--name", help="Program name"),
    platform: Optional[str] = typer.Option(None, "--platform", help="Platform (HackerOne, Bugcrowd, etc.)"),
    scope_file: Optional[str] = typer.Option(None, "--scope-file", help="Path to scope file"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode"),
) -> None:
    """Create a new bug bounty program."""
    
    try:
        # Setup
        from ...core.config import get_settings
        settings = get_settings()
        setup_logging(settings)
        init_database()
        
        if interactive:
            # Interactive program creation
            name = name or Prompt.ask("Program name")
            platform = platform or Prompt.ask("Platform", choices=["HackerOne", "Bugcrowd", "Other"], default="Other")
            
            if scope_file:
                # Load scope from file
                from ...core.scope import load_scope_from_file
                scope_config = load_scope_from_file(scope_file)
                scope = ProgramScope(
                    domains=scope_config.domains,
                    ips=scope_config.ips,
                    urls=scope_config.urls,
                    exclusions=scope_config.exclusions,
                )
            else:
                # Create scope interactively
                console.print("[blue]Enter program scope (press Enter for empty):[/blue]")
                domains = Prompt.ask("Domains (comma-separated)", default="").split(",")
                domains = [d.strip() for d in domains if d.strip()]
                
                ips = Prompt.ask("IP ranges (comma-separated)", default="").split(",")
                ips = [ip.strip() for ip in ips if ip.strip()]
                
                urls = Prompt.ask("URL patterns (comma-separated)", default="").split(",")
                urls = [url.strip() for url in urls if url.strip()]
                
                exclusions = Prompt.ask("Exclusions (comma-separated)", default="").split(",")
                exclusions = [ex.strip() for ex in exclusions if ex.strip()]
                
                scope = ProgramScope(
                    domains=domains,
                    ips=ips,
                    urls=urls,
                    exclusions=exclusions,
                )
        else:
            # Non-interactive mode
            if not name or not platform:
                console.print("[red]Name and platform are required in non-interactive mode![/red]")
                raise typer.Exit(1)
            
            if scope_file:
                from ...core.scope import load_scope_from_file
                scope_config = load_scope_from_file(scope_file)
                scope = ProgramScope(
                    domains=scope_config.domains,
                    ips=scope_config.ips,
                    urls=scope_config.urls,
                    exclusions=scope_config.exclusions,
                )
            else:
                scope = ProgramScope()
        
        # Create program
        program = Program(
            name=name,
            platform=platform,
            scope=scope,
            status="active",
            program_type="public",
        )
        
        # Save to database
        db = next(get_database())
        db.add(program)
        db.commit()
        
        # Show success message
        success_panel = Panel(
            f"Program created successfully!\n\n"
            f"Name: {name}\n"
            f"Platform: {platform}\n"
            f"Domains: {len(scope.domains)}\n"
            f"IPs: {len(scope.ips)}\n"
            f"URLs: {len(scope.urls)}\n"
            f"Exclusions: {len(scope.exclusions)}",
            title="Program Created",
            border_style="green"
        )
        console.print(success_panel)
        
    except Exception as e:
        console.print(f"[red]Error creating program: {str(e)}[/red]")
        logger.error(f"Program creation error: {str(e)}", exc_info=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

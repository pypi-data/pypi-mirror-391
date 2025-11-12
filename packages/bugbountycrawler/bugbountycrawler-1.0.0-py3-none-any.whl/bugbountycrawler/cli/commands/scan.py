"""Scan command for BugBountyCrawler CLI."""

import typer
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.prompt import Confirm, Prompt
import asyncio
import json

from ...core.config import get_settings
from ...core.scope import create_scope_validator
from ...core.logger import setup_logging, get_logger
from ...database.connection import init_database, get_database
from ...scanners.manager import ScannerManager
from ...crawlers.manager import CrawlerManager

console = Console()
logger = get_logger(__name__)

app = typer.Typer(name="scan", help="Scan targets for vulnerabilities")


@app.command()
def start(
    scope_file: Path = typer.Argument(..., help="Path to scope file (YAML/JSON)"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Specific target to scan"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Custom scan configuration"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for results"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be scanned without actually scanning"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompts"),
) -> None:
    """Start a vulnerability scan."""
    
    try:
        # Initialize logging
        settings = get_settings()
        setup_logging(settings)
        
        # Load scope
        console.print(f"[blue]Loading scope from: {scope_file}[/blue]")
        scope_validator = create_scope_validator(scope_file)
        
        # Validate scope
        issues = scope_validator.validate_scope_file()
        if issues:
            console.print("[red]Scope validation issues:[/red]")
            for issue in issues:
                console.print(f"  • {issue}")
            
            if not force and not Confirm.ask("Continue anyway?"):
                raise typer.Exit(1)
        
        # Show scope summary
        scope_summary = scope_validator.get_scope_summary()
        console.print(f"[green]Program: {scope_summary['program_name']}[/green]")
        console.print(f"[green]Domains: {scope_summary['domains']}[/green]")
        console.print(f"[green]IPs: {scope_summary['ips']}[/green]")
        console.print(f"[green]URLs: {scope_summary['urls']}[/green]")
        console.print(f"[green]Exclusions: {scope_summary['exclusions']}[/green]")
        
        # Get targets
        if target:
            targets = [target]
        else:
            # Extract targets from scope
            targets = []
            targets.extend(scope_validator.config.domains)
            targets.extend(scope_validator.config.ips)
            targets.extend(scope_validator.config.urls)
        
        if not targets:
            console.print("[red]No targets found in scope![/red]")
            raise typer.Exit(1)
        
        # Validate targets are in scope
        valid_targets = []
        for t in targets:
            if scope_validator.is_in_scope(t):
                valid_targets.append(t)
            else:
                console.print(f"[yellow]Target not in scope: {t}[/yellow]")
        
        if not valid_targets:
            console.print("[red]No valid targets found![/red]")
            raise typer.Exit(1)
        
        console.print(f"[green]Found {len(valid_targets)} valid targets[/green]")
        
        if dry_run:
            console.print("\n[blue]Dry run - targets that would be scanned:[/blue]")
            for t in valid_targets:
                console.print(f"  • {t}")
            return
        
        # Confirmation
        if not force:
            if not Confirm.ask(f"Start scan of {len(valid_targets)} targets?"):
                console.print("Scan cancelled.")
                return
        
        # Initialize database
        init_database()
        
        # Run scan
        asyncio.run(run_scan(valid_targets, scope_validator, settings, output_dir))
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        logger.error(f"Scan error: {str(e)}", exc_info=True)
        raise typer.Exit(1)


async def run_scan(targets: List[str], scope_validator, settings, output_dir: Optional[Path]) -> None:
    """Run the actual scan."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        
        # Initialize managers
        scanner_manager = ScannerManager(settings)
        crawler_manager = CrawlerManager(settings)
        
        # Create scan task
        scan_task = progress.add_task("Initializing scan...", total=len(targets))
        
        # Process each target
        for i, target in enumerate(targets):
            progress.update(scan_task, description=f"Scanning {target}")
            
            try:
                # Validate target is still in scope
                if not scope_validator.is_in_scope(target):
                    console.print(f"[yellow]Skipping {target} - not in scope[/yellow]")
                    continue
                
                # Crawl target
                console.print(f"[blue]Crawling {target}...[/blue]")
                discovered_urls = await crawler_manager.crawl_target(target)
                
                # Scan discovered URLs
                console.print(f"[blue]Scanning {len(discovered_urls)} discovered URLs...[/blue]")
                findings = await scanner_manager.scan_urls(discovered_urls)
                
                # Report findings
                if findings:
                    console.print(f"[green]Found {len(findings)} potential issues[/green]")
                    for finding in findings:
                        console.print(f"  • {finding['title']} ({finding['severity']})")
                else:
                    console.print(f"[green]No issues found for {target}[/green]")
                
                progress.update(scan_task, advance=1)
                
            except Exception as e:
                console.print(f"[red]Error scanning {target}: {str(e)}[/red]")
                logger.error(f"Error scanning {target}: {str(e)}", exc_info=True)
                progress.update(scan_task, advance=1)
        
        progress.update(scan_task, description="Scan completed!")
    
    console.print("[green]Scan completed successfully![/green]")


@app.command()
def status(
    scan_id: Optional[str] = typer.Option(None, "--scan-id", help="Specific scan ID to check"),
) -> None:
    """Show scan status."""
    
    console.print("[blue]Scan Status[/blue]")
    
    # TODO: Implement scan status checking
    console.print("Scan status functionality coming soon!")


@app.command()
def stop(
    scan_id: str = typer.Argument(..., help="Scan ID to stop"),
) -> None:
    """Stop a running scan."""
    
    console.print(f"[blue]Stopping scan {scan_id}...[/blue]")
    
    # TODO: Implement scan stopping
    console.print("Scan stopping functionality coming soon!")


@app.command()
def list() -> None:
    """List all scans."""
    
    console.print("[blue]Available Scans[/blue]")
    
    # TODO: Implement scan listing
    console.print("Scan listing functionality coming soon!")


@app.command()
def results(
    scan_id: str = typer.Argument(..., help="Scan ID to show results for"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, csv)"),
) -> None:
    """Show scan results."""
    
    console.print(f"[blue]Results for scan {scan_id}[/blue]")
    
    # TODO: Implement results display
    console.print("Results display functionality coming soon!")


if __name__ == "__main__":
    app()

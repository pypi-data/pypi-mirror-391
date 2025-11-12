"""User creation command."""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import getpass
import hashlib
import secrets

from ...database.connection import init_database, get_database
from ...models.user import User, UserRole
from ...core.logger import setup_logging, get_logger

console = Console()
logger = get_logger(__name__)

app = typer.Typer(name="create-user", help="Create user account")


@app.command()
def create(
    username: Optional[str] = typer.Option(None, "--username", help="Username"),
    email: Optional[str] = typer.Option(None, "--email", help="Email address"),
    role: Optional[str] = typer.Option("viewer", "--role", help="User role (admin, analyst, viewer)"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode"),
) -> None:
    """Create a new user account."""
    
    try:
        # Setup
        from ...core.config import get_settings
        settings = get_settings()
        setup_logging(settings)
        init_database()
        
        if interactive:
            # Interactive user creation
            username = username or Prompt.ask("Username")
            email = email or Prompt.ask("Email address")
            role = role or Prompt.ask("Role", choices=["admin", "analyst", "viewer"], default="viewer")
        
        # Validate inputs
        if not username or not email:
            console.print("[red]Username and email are required![/red]")
            raise typer.Exit(1)
        
        if role not in ["admin", "analyst", "viewer"]:
            console.print("[red]Invalid role! Must be admin, analyst, or viewer[/red]")
            raise typer.Exit(1)
        
        # Get password
        if interactive:
            password = getpass.getpass("Password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            
            if password != confirm_password:
                console.print("[red]Passwords do not match![/red]")
                raise typer.Exit(1)
        else:
            password = getpass.getpass("Password: ")
        
        if len(password) < 8:
            console.print("[red]Password must be at least 8 characters long![/red]")
            raise typer.Exit(1)
        
        # Hash password
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        password_hash_hex = password_hash.hex()
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash_hex,
            salt=salt,
            role=UserRole(role),
            is_active=True,
            is_verified=True,
        )
        
        # Save to database
        db = next(get_database())
        db.add(user)
        db.commit()
        
        # Show success message
        success_panel = Panel(
            f"User created successfully!\n\n"
            f"Username: {username}\n"
            f"Email: {email}\n"
            f"Role: {role}\n"
            f"Status: Active",
            title="User Created",
            border_style="green"
        )
        console.print(success_panel)
        
    except Exception as e:
        console.print(f"[red]Error creating user: {str(e)}[/red]")
        logger.error(f"User creation error: {str(e)}", exc_info=True)
        raise typer.Exit(1)


@app.command()
def list() -> None:
    """List all users."""
    
    try:
        # Setup
        from ...core.config import get_settings
        settings = get_settings()
        setup_logging(settings)
        init_database()
        
        # Get users from database
        db = next(get_database())
        users = db.query(User).all()
        
        if not users:
            console.print("[yellow]No users found[/yellow]")
            return
        
        # Create table
        from rich.table import Table
        table = Table(title="Users")
        table.add_column("Username", style="cyan")
        table.add_column("Email", style="green")
        table.add_column("Role", style="yellow")
        table.add_column("Status", style="red")
        table.add_column("Created", style="blue")
        
        for user in users:
            status = "Active" if user.is_active else "Inactive"
            table.add_row(
                user.username,
                user.email,
                user.role.value,
                status,
                user.created_at.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing users: {str(e)}[/red]")
        logger.error(f"User listing error: {str(e)}", exc_info=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

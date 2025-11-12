"""CLI commands for BugBountyCrawler."""

from .scan import app as scan_app
from .web_ui import app as web_ui_app
from .init_db import app as init_db_app
from .create_user import app as create_user_app
from .list_programs import app as list_programs_app
from .create_program import app as create_program_app

__all__ = [
    "scan_app",
    "web_ui_app", 
    "init_db_app",
    "create_user_app",
    "list_programs_app",
    "create_program_app",
]

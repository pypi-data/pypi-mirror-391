"""
BugBountyCrawler - A production-ready, legal, modular BugBountyCrawler
for ethical bug bounty hunting.

This package provides comprehensive reconnaissance and scanning capabilities
while prioritizing safety, accuracy, and responsible disclosure.
"""

__version__ = "1.0.0"
__author__ = "BugBountyCrawler Team"
__email__ = "team@bugbountycrawler.dev"

from .core.config import Settings
from .core.scope import ScopeValidator
from .models.finding import Finding, FindingSeverity, FindingStatus

__all__ = [
    "Settings",
    "ScopeValidator", 
    "Finding",
    "FindingSeverity",
    "FindingStatus",
]

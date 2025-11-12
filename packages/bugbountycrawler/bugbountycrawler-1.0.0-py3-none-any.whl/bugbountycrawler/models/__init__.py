"""Data models for BugBountyCrawler."""

from .finding import Finding, FindingSeverity, FindingStatus, FindingType
from .scan import Scan, ScanStatus, ScanConfig
from .target import Target, TargetType, TargetStatus
from .program import Program, ProgramScope
from .user import User, UserRole

__all__ = [
    "Finding",
    "FindingSeverity", 
    "FindingStatus",
    "FindingType",
    "Scan",
    "ScanStatus",
    "ScanConfig",
    "Target",
    "TargetType",
    "TargetStatus",
    "Program",
    "ProgramScope",
    "User",
    "UserRole",
]


"""Scanners package for BugBountyCrawler."""

from .manager import ScannerManager
from .base import BaseScanner
from .security_headers import SecurityHeadersScanner
from .cors import CORSScanner
from .ssl import SSLScanner
from .directory_traversal import DirectoryTraversalScanner
from .information_disclosure import InformationDisclosureScanner
from .rate_limiting import RateLimitingScanner
from .open_redirect import OpenRedirectScanner
from .asset_discovery import AssetDiscoveryScanner
from .sql_injection import SQLInjectionScanner
from .xss import XSSScanner
from .idor import IDORScanner
from .authentication import AuthenticationScanner
from .api_security import APISecurityScanner
from .s3_bucket import S3BucketScanner
from .cloud_metadata import CloudMetadataScanner
from .iam import IAMScanner
from .network import NetworkScanner
from .kubernetes import KubernetesScanner
from .dns import DNSScanner
from .secret import SecretScanner

# NEW SCANNERS - Phase 3 Implementation
from .command_injection import CommandInjectionScanner
from .nosql_injection import NoSQLInjectionScanner
from .csrf import CSRFScanner
from .business_logic import BusinessLogicScanner
from .xxe import XXEScanner
from .dependency_sca import DependencySCAScanner
from .privacy_compliance import PrivacyComplianceScanner

# NEW SCANNERS - Phase 4 Mid-Term Implementation
from .sast import SASTScanner
from .mobile_security import MobileSecurityScanner

# NEW SCANNERS - Phase 5 Long-Term Implementation
from .fuzzer import FuzzingScanner

__all__ = [
    "ScannerManager",
    "BaseScanner",
    "SecurityHeadersScanner",
    "CORSScanner", 
    "SSLScanner",
    "DirectoryTraversalScanner",
    "InformationDisclosureScanner",
    "RateLimitingScanner",
    "OpenRedirectScanner",
    "AssetDiscoveryScanner",
    # Phase 1 - High Priority Web Vulnerabilities
    "SQLInjectionScanner",
    "XSSScanner",
    "IDORScanner",
    "AuthenticationScanner",
    "APISecurityScanner",
    # Phase 2 - Infrastructure & Cloud Vulnerabilities
    "S3BucketScanner",
    "CloudMetadataScanner",
    "IAMScanner",
    "NetworkScanner",
    "KubernetesScanner",
    "DNSScanner",
    "SecretScanner",
    # Phase 3 - Critical Gap Fillers (NEW)
    "CommandInjectionScanner",
    "NoSQLInjectionScanner",
    "CSRFScanner",
    "BusinessLogicScanner",
    "XXEScanner",
    "DependencySCAScanner",
    "PrivacyComplianceScanner",
    # Phase 4 - Mid-Term Advanced Features (NEW)
    "SASTScanner",
    "MobileSecurityScanner",
    # Phase 5 - Long-Term Advanced Features (NEW)
    "FuzzingScanner",
]

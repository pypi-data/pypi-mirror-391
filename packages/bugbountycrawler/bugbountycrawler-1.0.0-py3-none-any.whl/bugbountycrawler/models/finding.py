"""Finding models for BugBountyCrawler."""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class FindingSeverity(str, Enum):
    """Finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingStatus(str, Enum):
    """Finding status levels."""
    OPEN = "open"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    WONTFIX = "wontfix"
    DUPLICATE = "duplicate"


class Remediation(BaseModel):
    """Remediation information for findings."""
    title: str
    description: str
    steps: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    estimated_effort: str = "medium"  # low, medium, high
    priority: str = "medium"  # low, medium, high, critical


class FindingType(str, Enum):
    """Finding types."""
    # Web Application
    SQL_INJECTION = "sql_injection"
    NOSQL_INJECTION = "nosql_injection"
    COMMAND_INJECTION = "command_injection"
    XSS = "xss"
    CSRF = "csrf"
    XXE = "xxe"
    SSRF = "ssrf"
    IDOR = "idor"
    AUTHORIZATION_BYPASS = "authorization_bypass"
    AUTHENTICATION_BYPASS = "authentication_bypass"
    BUSINESS_LOGIC = "business_logic"
    
    # API
    API_MISCONFIGURATION = "api_misconfiguration"
    BROKEN_OBJECT_LEVEL_AUTHORIZATION = "bola"
    MASS_ASSIGNMENT = "mass_assignment"
    
    # Infrastructure
    SECURITY_HEADERS = "security_headers"
    CORS_MISCONFIGURATION = "cors_misconfiguration"
    SSL_TLS_ISSUES = "ssl_tls_issues"
    DNS_MISCONFIGURATION = "dns_misconfiguration"
    
    # Cloud
    CLOUD_MISCONFIGURATION = "cloud_misconfiguration"
    IAM_MISCONFIGURATION = "iam_misconfiguration"
    S3_MISCONFIGURATION = "s3_misconfiguration"
    METADATA_EXPOSURE = "metadata_exposure"
    
    # Data
    INFORMATION_DISCLOSURE = "information_disclosure"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    PII_EXPOSURE = "pii_exposure"
    
    # Compliance
    COMPLIANCE_VIOLATION = "compliance_violation"
    PRIVACY_VIOLATION = "privacy_violation"
    
    # Dependencies
    VULNERABLE_DEPENDENCY = "vulnerable_dependency"
    OUTDATED_DEPENDENCY = "outdated_dependency"
    
    # SAST / Code Analysis
    CODE_VULNERABILITY = "code_vulnerability"
    CRYPTOGRAPHIC_FAILURE = "cryptographic_failure"
    CONFIGURATION_ISSUE = "configuration_issue"
    
    # Mobile
    MOBILE_SECURITY = "mobile_security"
    INSECURE_STORAGE = "insecure_storage"
    CERTIFICATE_PINNING = "certificate_pinning"
    
    # Fuzzing & Protocol
    FUZZING_ANOMALY = "fuzzing_anomaly"
    PROTOCOL_VULNERABILITY = "protocol_vulnerability"
    
    # Other
    OPEN_REDIRECT = "open_redirect"
    DIRECTORY_TRAVERSAL = "directory_traversal"
    FILE_UPLOAD = "file_upload"
    RATE_LIMITING = "rate_limiting"
    SECRET_EXPOSURE = "secret_exposure"


class Finding(BaseModel):
    """Finding model."""
    
    # Core fields
    id: Optional[str] = None
    title: str
    description: str
    severity: FindingSeverity
    finding_type: FindingType
    
    # Location
    url: str
    method: str = "GET"
    parameter: Optional[str] = None
    
    # Risk assessment
    impact: str
    likelihood: str
    risk_score: float = Field(ge=0.0, le=10.0)
    
    # Technical details
    proof_of_concept: Optional[str] = None
    remediation: Optional[str] = None
    references: List[str] = Field(default_factory=list)
    
    # Metadata
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "open"  # open, confirmed, false_positive, resolved
    confidence: str = "high"  # low, medium, high
    
    # Additional fields
    cvss_score: Optional[float] = None
    cve_ids: List[str] = Field(default_factory=list)
    cwe_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        """Pydantic config."""
        use_enum_values = True

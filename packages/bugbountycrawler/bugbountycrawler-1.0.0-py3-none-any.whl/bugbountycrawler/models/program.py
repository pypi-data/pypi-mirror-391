"""Program data models for BugBountyCrawler."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class ProgramScope(BaseModel):
    """Program scope configuration."""
    
    domains: List[str] = Field(default_factory=list, description="Allowed domains")
    ips: List[str] = Field(default_factory=list, description="Allowed IP ranges")
    urls: List[str] = Field(default_factory=list, description="Allowed URL patterns")
    exclusions: List[str] = Field(default_factory=list, description="Excluded patterns")
    
    # Additional scope rules
    allow_subdomains: bool = Field(default=True, description="Allow subdomains")
    allow_ports: List[int] = Field(default_factory=list, description="Allowed ports")
    allow_protocols: List[str] = Field(default=["http", "https"], description="Allowed protocols")
    
    # Rate limiting
    max_requests_per_minute: int = Field(default=60, description="Max requests per minute")
    max_requests_per_hour: int = Field(default=1000, description="Max requests per hour")
    max_concurrent_requests: int = Field(default=5, description="Max concurrent requests")
    
    # Time restrictions
    allowed_hours: List[int] = Field(default=list(range(24)), description="Allowed hours (0-23)")
    allowed_days: List[int] = Field(default=list(range(7)), description="Allowed days (0-6, Monday=0)")
    
    @validator("allow_protocols")
    @classmethod
    def validate_protocols(cls, v: List[str]) -> List[str]:
        """Validate allowed protocols."""
        valid_protocols = ["http", "https", "ftp", "sftp", "ssh", "telnet", "smtp", "pop3", "imap"]
        for protocol in v:
            if protocol not in valid_protocols:
                raise ValueError(f"Invalid protocol: {protocol}. Must be one of {valid_protocols}")
        return v


class Program(BaseModel):
    """Bug bounty program model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Program ID")
    
    # Basic Information
    name: str = Field(..., description="Program name")
    description: Optional[str] = Field(None, description="Program description")
    url: Optional[str] = Field(None, description="Program URL")
    
    # Platform Information
    platform: str = Field(..., description="Platform (HackerOne, Bugcrowd, etc.)")
    program_id: Optional[str] = Field(None, description="Platform-specific program ID")
    program_url: Optional[str] = Field(None, description="Platform program URL")
    
    # Scope Configuration
    scope: ProgramScope = Field(default_factory=ProgramScope, description="Program scope")
    
    # Program Details
    status: str = Field(default="active", description="Program status")
    program_type: str = Field(default="public", description="Program type (public, private, invite-only)")
    bounty_range: Optional[str] = Field(None, description="Bounty range (e.g., $100-$5000)")
    average_bounty: Optional[float] = Field(None, description="Average bounty amount")
    
    # Contact Information
    contact_email: Optional[str] = Field(None, description="Contact email")
    security_team: Optional[str] = Field(None, description="Security team contact")
    
    # Statistics
    total_findings: int = Field(default=0, description="Total findings submitted")
    accepted_findings: int = Field(default=0, description="Accepted findings")
    total_payout: float = Field(default=0.0, description="Total payout received")
    average_response_time: Optional[float] = Field(None, description="Average response time in hours")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_scan: Optional[datetime] = Field(None, description="Last scan timestamp")
    
    # Additional Data
    tags: List[str] = Field(default_factory=list, description="Program tags")
    notes: Optional[str] = Field(None, description="Program notes")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw program data")
    
    def is_active(self) -> bool:
        """Check if program is active."""
        return self.status == "active"
    
    def is_public(self) -> bool:
        """Check if program is public."""
        return self.program_type == "public"
    
    def get_acceptance_rate(self) -> float:
        """Get acceptance rate percentage."""
        if self.total_findings == 0:
            return 0.0
        return (self.accepted_findings / self.total_findings) * 100.0
    
    def get_average_payout(self) -> float:
        """Get average payout per accepted finding."""
        if self.accepted_findings == 0:
            return 0.0
        return self.total_payout / self.accepted_findings
    
    def add_finding(self, accepted: bool = False, payout: float = 0.0) -> None:
        """Add a finding to program statistics."""
        self.total_findings += 1
        if accepted:
            self.accepted_findings += 1
            self.total_payout += payout
        self.updated_at = datetime.utcnow()
    
    def update_scan_time(self) -> None:
        """Update last scan timestamp."""
        self.last_scan = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def is_in_scope(self, target: str) -> bool:
        """Check if target is in program scope."""
        # This is a simplified check - in practice, you'd use the ScopeValidator
        target_lower = target.lower()
        
        # Check domain patterns
        for domain in self.scope.domains:
            if domain.startswith("*."):
                if target_lower.endswith(domain[2:]):
                    return True
            elif target_lower == domain:
                return True
        
        # Check URL patterns
        for url_pattern in self.scope.urls:
            if url_pattern.replace("*", "") in target_lower:
                return True
        
        return False
    
    def get_scope_summary(self) -> Dict[str, Any]:
        """Get a summary of the program scope."""
        return {
            "domains": len(self.scope.domains),
            "ips": len(self.scope.ips),
            "urls": len(self.scope.urls),
            "exclusions": len(self.scope.exclusions),
            "allow_subdomains": self.scope.allow_subdomains,
            "allowed_protocols": self.scope.allow_protocols,
            "rate_limits": {
                "per_minute": self.scope.max_requests_per_minute,
                "per_hour": self.scope.max_requests_per_hour,
                "concurrent": self.scope.max_concurrent_requests,
            }
        }
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

"""Target data models for BugBountyCrawler."""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from urllib.parse import urlparse
import uuid


class TargetType(str, Enum):
    """Target types."""
    DOMAIN = "domain"
    URL = "url"
    IP = "ip"
    IP_RANGE = "ip_range"
    API_ENDPOINT = "api_endpoint"


class TargetStatus(str, Enum):
    """Target status."""
    PENDING = "pending"
    ACTIVE = "active"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"
    EXCLUDED = "excluded"


class Target(BaseModel):
    """Target model for scanning."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Target ID")
    program_id: str = Field(..., description="Associated program ID")
    
    # Basic Information
    target: str = Field(..., description="Target value (URL, domain, IP)")
    target_type: TargetType = Field(..., description="Type of target")
    status: TargetStatus = Field(default=TargetStatus.PENDING, description="Target status")
    
    # Parsed Information
    domain: Optional[str] = Field(None, description="Parsed domain")
    ip_address: Optional[str] = Field(None, description="Parsed IP address")
    port: Optional[int] = Field(None, description="Port number")
    protocol: str = Field(default="https", description="Protocol (http/https)")
    path: str = Field(default="/", description="URL path")
    
    # Discovery Information
    discovered_by: Optional[str] = Field(None, description="How target was discovered")
    parent_target: Optional[str] = Field(None, description="Parent target ID")
    depth: int = Field(default=0, description="Discovery depth")
    
    # Technical Details
    title: Optional[str] = Field(None, description="Page title")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    content_type: Optional[str] = Field(None, description="Content type")
    content_length: Optional[int] = Field(None, description="Content length")
    server: Optional[str] = Field(None, description="Server header")
    technologies: List[str] = Field(default_factory=list, description="Detected technologies")
    
    # Security Information
    ssl_certificate: Optional[Dict[str, Any]] = Field(None, description="SSL certificate info")
    security_headers: Dict[str, str] = Field(default_factory=dict, description="Security headers")
    vulnerabilities: List[str] = Field(default_factory=list, description="Vulnerability IDs")
    
    # Scanning Results
    scan_count: int = Field(default=0, description="Number of times scanned")
    last_scanned: Optional[datetime] = Field(None, description="Last scan timestamp")
    response_time: Optional[float] = Field(None, description="Average response time")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Additional Data
    tags: List[str] = Field(default_factory=list, description="Target tags")
    notes: Optional[str] = Field(None, description="Target notes")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw target data")
    
    @validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        """Validate target format."""
        if not v or not v.strip():
            raise ValueError("Target cannot be empty")
        return v.strip()
    
    @validator("target_type", pre=True)
    @classmethod
    def determine_target_type(cls, v: str, values: Dict[str, Any]) -> TargetType:
        """Determine target type based on target value."""
        if "target" in values:
            target = values["target"]
            
            # Check if it's a URL
            if target.startswith(("http://", "https://")):
                return TargetType.URL
            
            # Check if it's an IP address
            try:
                import ipaddress
                ipaddress.ip_address(target)
                return TargetType.IP
            except ValueError:
                pass
            
            # Check if it's an IP range
            if "/" in target:
                try:
                    import ipaddress
                    ipaddress.ip_network(target, strict=False)
                    return TargetType.IP_RANGE
                except ValueError:
                    pass
            
            # Check if it's an API endpoint
            if any(keyword in target.lower() for keyword in ["/api/", "/v1/", "/v2/", "/graphql"]):
                return TargetType.API_ENDPOINT
            
            # Default to domain
            return TargetType.DOMAIN
        
        return v
    
    def parse_target(self) -> None:
        """Parse target and extract components."""
        if self.target_type == TargetType.URL:
            parsed = urlparse(self.target)
            self.domain = parsed.hostname
            self.protocol = parsed.scheme
            self.path = parsed.path or "/"
            if parsed.port:
                self.port = parsed.port
        elif self.target_type in [TargetType.IP, TargetType.IP_RANGE]:
            self.ip_address = self.target
        elif self.target_type == TargetType.DOMAIN:
            self.domain = self.target
        elif self.target_type == TargetType.API_ENDPOINT:
            parsed = urlparse(self.target if self.target.startswith(("http://", "https://")) else f"https://{self.target}")
            self.domain = parsed.hostname
            self.protocol = parsed.scheme
            self.path = parsed.path or "/"
    
    def get_base_url(self) -> str:
        """Get base URL for the target."""
        if self.target_type == TargetType.URL:
            parsed = urlparse(self.target)
            return f"{parsed.scheme}://{parsed.netloc}"
        elif self.domain:
            return f"{self.protocol}://{self.domain}"
        elif self.ip_address:
            port_suffix = f":{self.port}" if self.port else ""
            return f"{self.protocol}://{self.ip_address}{port_suffix}"
        else:
            return self.target
    
    def get_full_url(self) -> str:
        """Get full URL for the target."""
        if self.target_type == TargetType.URL:
            return self.target
        else:
            base_url = self.get_base_url()
            return f"{base_url}{self.path}"
    
    def is_accessible(self) -> bool:
        """Check if target is accessible."""
        return self.status_code is not None and 200 <= self.status_code < 400
    
    def is_secure(self) -> bool:
        """Check if target uses secure protocol."""
        return self.protocol == "https"
    
    def has_ssl_certificate(self) -> bool:
        """Check if target has SSL certificate."""
        return self.ssl_certificate is not None
    
    def get_technologies(self) -> List[str]:
        """Get detected technologies."""
        return self.technologies
    
    def add_technology(self, technology: str) -> None:
        """Add a detected technology."""
        if technology not in self.technologies:
            self.technologies.append(technology)
    
    def add_vulnerability(self, vulnerability_id: str) -> None:
        """Add a vulnerability ID."""
        if vulnerability_id not in self.vulnerabilities:
            self.vulnerabilities.append(vulnerability_id)
    
    def update_scan_info(self, status_code: int, response_time: float, **kwargs) -> None:
        """Update target with scan information."""
        self.status_code = status_code
        self.response_time = response_time
        self.scan_count += 1
        self.last_scanned = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Update other fields if provided
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

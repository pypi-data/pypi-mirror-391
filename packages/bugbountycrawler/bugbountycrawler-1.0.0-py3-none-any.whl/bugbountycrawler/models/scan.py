"""Scan data models for BugBountyCrawler."""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
import uuid


class ScanStatus(str, Enum):
    """Scan status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanType(str, Enum):
    """Scan types."""
    FULL = "full"
    QUICK = "quick"
    PASSIVE = "passive"
    ACTIVE = "active"
    CUSTOM = "custom"


class ScanConfig(BaseModel):
    """Scan configuration."""
    
    # Basic Settings
    scan_type: ScanType = Field(default=ScanType.FULL, description="Type of scan")
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum crawl depth")
    max_pages: int = Field(default=1000, ge=1, le=10000, description="Maximum pages to crawl")
    timeout: int = Field(default=30, ge=5, le=300, description="Request timeout in seconds")
    
    # Rate Limiting
    requests_per_second: float = Field(default=1.0, ge=0.1, le=100.0, description="Requests per second")
    max_concurrent: int = Field(default=5, ge=1, le=100, description="Maximum concurrent requests")
    delay_between_requests: float = Field(default=0.1, ge=0.0, le=10.0, description="Delay between requests")
    
    # Scanning Options
    enable_crawling: bool = Field(default=True, description="Enable web crawling")
    enable_subdomain_enumeration: bool = Field(default=True, description="Enable subdomain enumeration")
    enable_port_scanning: bool = Field(default=False, description="Enable port scanning")
    enable_vulnerability_scanning: bool = Field(default=True, description="Enable vulnerability scanning")
    enable_parameter_discovery: bool = Field(default=True, description="Enable parameter discovery")
    
    # JavaScript and SPA Support
    enable_javascript: bool = Field(default=True, description="Enable JavaScript execution")
    wait_for_dynamic_content: bool = Field(default=True, description="Wait for dynamic content")
    max_wait_time: int = Field(default=5, ge=0, le=30, description="Maximum wait time for dynamic content")
    
    # Headers and User Agent
    custom_headers: Dict[str, str] = Field(default_factory=dict, description="Custom HTTP headers")
    user_agent: Optional[str] = Field(None, description="Custom user agent")
    
    # Proxy Settings
    use_proxy: bool = Field(default=False, description="Use proxy for requests")
    proxy_url: Optional[str] = Field(None, description="Proxy URL")
    use_tor: bool = Field(default=False, description="Use Tor for requests")
    
    # Output Settings
    save_screenshots: bool = Field(default=True, description="Save screenshots")
    save_responses: bool = Field(default=False, description="Save full responses")
    generate_reports: bool = Field(default=True, description="Generate reports")
    
    # Safety Settings
    respect_robots_txt: bool = Field(default=True, description="Respect robots.txt")
    respect_rate_limits: bool = Field(default=True, description="Respect rate limits")
    require_approval: bool = Field(default=True, description="Require approval for findings")
    
    # Plugin Settings
    enabled_plugins: List[str] = Field(default_factory=list, description="Enabled plugins")
    plugin_config: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Plugin configuration")


class ScanProgress(BaseModel):
    """Scan progress tracking."""
    
    total_targets: int = Field(default=0, description="Total targets to scan")
    completed_targets: int = Field(default=0, description="Completed targets")
    total_pages: int = Field(default=0, description="Total pages discovered")
    crawled_pages: int = Field(default=0, description="Pages crawled")
    findings_discovered: int = Field(default=0, description="Findings discovered")
    errors_encountered: int = Field(default=0, description="Errors encountered")
    
    # Timing
    start_time: Optional[datetime] = Field(None, description="Scan start time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    last_activity: Optional[datetime] = Field(None, description="Last activity time")
    
    def get_percentage(self) -> float:
        """Get completion percentage."""
        if self.total_targets == 0:
            return 0.0
        return (self.completed_targets / self.total_targets) * 100.0
    
    def get_eta(self) -> Optional[datetime]:
        """Get estimated time of arrival."""
        if not self.start_time or self.completed_targets == 0:
            return None
        
        elapsed = datetime.utcnow() - self.start_time
        rate = self.completed_targets / elapsed.total_seconds()
        remaining = self.total_targets - self.completed_targets
        
        if rate > 0:
            eta_seconds = remaining / rate
            return datetime.utcnow() + timedelta(seconds=eta_seconds)
        
        return None


class Scan(BaseModel):
    """Scan model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Scan ID")
    program_id: str = Field(..., description="Associated program ID")
    
    # Basic Information
    name: str = Field(..., description="Scan name")
    description: Optional[str] = Field(None, description="Scan description")
    status: ScanStatus = Field(default=ScanStatus.PENDING, description="Scan status")
    scan_type: ScanType = Field(default=ScanType.FULL, description="Type of scan")
    
    # Configuration
    config: ScanConfig = Field(default_factory=ScanConfig, description="Scan configuration")
    
    # Progress Tracking
    progress: ScanProgress = Field(default_factory=ScanProgress, description="Scan progress")
    
    # Targets
    target_urls: List[str] = Field(default_factory=list, description="Target URLs")
    discovered_urls: List[str] = Field(default_factory=list, description="Discovered URLs")
    excluded_urls: List[str] = Field(default_factory=list, description="Excluded URLs")
    
    # Results
    findings: List[str] = Field(default_factory=list, description="Finding IDs")
    screenshots: List[str] = Field(default_factory=list, description="Screenshot file paths")
    reports: List[str] = Field(default_factory=list, description="Report file paths")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    # User Information
    created_by: str = Field(..., description="Created by user")
    approved_by: Optional[str] = Field(None, description="Approved by user")
    
    # Additional Data
    tags: List[str] = Field(default_factory=list, description="Scan tags")
    notes: Optional[str] = Field(None, description="Scan notes")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw scan data")
    
    def is_running(self) -> bool:
        """Check if scan is currently running."""
        return self.status == ScanStatus.RUNNING
    
    def is_completed(self) -> bool:
        """Check if scan is completed."""
        return self.status in [ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED]
    
    def get_duration(self) -> Optional[timedelta]:
        """Get scan duration."""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.utcnow()
        return end_time - self.started_at
    
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        if self.progress.total_targets == 0:
            return 0.0
        
        successful = self.progress.total_targets - self.progress.errors_encountered
        return (successful / self.progress.total_targets) * 100.0
    
    def add_finding(self, finding_id: str) -> None:
        """Add a finding to the scan."""
        if finding_id not in self.findings:
            self.findings.append(finding_id)
    
    def add_discovered_url(self, url: str) -> None:
        """Add a discovered URL to the scan."""
        if url not in self.discovered_urls:
            self.discovered_urls.append(url)
    
    def update_progress(self, **kwargs) -> None:
        """Update scan progress."""
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                setattr(self.progress, key, value)
        
        # Update last activity
        self.progress.last_activity = datetime.utcnow()
        
        # Update estimated completion
        self.progress.estimated_completion = self.progress.get_eta()
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            timedelta: lambda v: v.total_seconds()
        }

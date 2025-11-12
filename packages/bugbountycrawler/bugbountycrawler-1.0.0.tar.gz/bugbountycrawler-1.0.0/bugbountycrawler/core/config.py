"""Configuration management for BugBountyCrawler."""

import os
from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Database
    database_url: str = Field(
        default="sqlite:///./bugbounty.db",
        description="Database connection URL"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    encryption_key: str = Field(
        default="your-encryption-key-change-in-production",
        description="Key for encrypting sensitive data"
    )
    
    # Rate Limiting
    default_rate_limit: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Default requests per second"
    )
    max_concurrent: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum concurrent requests"
    )
    request_delay: float = Field(
        default=0.1,
        ge=0.0,
        le=10.0,
        description="Delay between requests in seconds"
    )
    
    # Scanning
    max_depth: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum crawl depth"
    )
    max_pages: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum pages to crawl"
    )
    timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Request timeout in seconds"
    )
    
    # User Agent
    user_agent: str = Field(
        default="BugBountyCrawler/1.0.0 (Ethical Security Testing)",
        description="User agent string"
    )
    
    # Proxy Settings
    proxy_url: Optional[str] = Field(
        default=None,
        description="Proxy URL (e.g., socks5://127.0.0.1:9050)"
    )
    use_tor: bool = Field(
        default=False,
        description="Use Tor for requests"
    )
    
    # Storage
    data_dir: Path = Field(
        default=Path("./data"),
        description="Directory for storing scan data"
    )
    reports_dir: Path = Field(
        default=Path("./reports"),
        description="Directory for storing reports"
    )
    
    # Remote Storage (Optional)
    s3_bucket: Optional[str] = Field(
        default=None,
        description="S3 bucket for remote storage"
    )
    s3_access_key: Optional[str] = Field(
        default=None,
        description="S3 access key"
    )
    s3_secret_key: Optional[str] = Field(
        default=None,
        description="S3 secret key"
    )
    s3_region: str = Field(
        default="us-east-1",
        description="S3 region"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_file: Optional[Path] = Field(
        default=None,
        description="Log file path"
    )
    
    # Web UI
    web_host: str = Field(
        default="127.0.0.1",
        description="Web UI host"
    )
    web_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Web UI port"
    )
    
    # Safety Features
    require_scope_confirmation: bool = Field(
        default=True,
        description="Require interactive scope confirmation"
    )
    auto_approve_findings: bool = Field(
        default=False,
        description="Auto-approve findings (NOT RECOMMENDED)"
    )
    max_findings_per_scan: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum findings per scan"
    )
    
    # Plugin Settings
    plugin_dir: Path = Field(
        default=Path("./plugins"),
        description="Directory for custom plugins"
    )
    allowed_plugins: List[str] = Field(
        default_factory=list,
        description="List of allowed plugin names"
    )
    sandbox_plugins: bool = Field(
        default=True,
        description="Run plugins in sandboxed environment"
    )
    
    @validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @validator("data_dir", "reports_dir", "plugin_dir")
    @classmethod
    def create_directories(cls, v: Path) -> Path:
        """Create directories if they don't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator("proxy_url")
    @classmethod
    def validate_proxy_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate proxy URL format."""
        if v is None:
            return v
        
        valid_schemes = ["http", "https", "socks4", "socks5"]
        if not any(v.startswith(f"{scheme}://") for scheme in valid_schemes):
            raise ValueError(f"proxy_url must start with one of {valid_schemes}")
        return v
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings

"""Base scanner class for BugBountyCrawler."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
import logging

from ..core.config import Settings
from ..core.rate_limiter import RateLimiter
from ..models.finding import Finding, FindingSeverity, FindingType

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Result of a scan operation."""
    
    url: str
    findings: List[Finding]
    errors: List[str]
    response_time: float
    status_code: int
    headers: Dict[str, str]
    content_length: int


class BaseScanner(ABC):
    """Base class for all scanners."""
    
    def __init__(self, settings: Settings, rate_limiter: Optional[RateLimiter] = None):
        """Initialize scanner."""
        self.settings = settings
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session: Optional[aiohttp.ClientSession] = None
        self.name = self.__class__.__name__
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
    
    async def setup(self) -> None:
        """Setup scanner resources."""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=self.settings.timeout)
        
        headers = {
            "User-Agent": self.settings.user_agent,
        }
        
        if self.settings.proxy_url:
            # Configure proxy
            pass  # TODO: Implement proxy support
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
    
    async def cleanup(self) -> None:
        """Cleanup scanner resources."""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def scan_url(self, url: str) -> ScanResult:
        """Scan a single URL."""
        pass
    
    async def scan_urls(self, urls: List[str]) -> List[ScanResult]:
        """Scan multiple URLs."""
        results = []
        
        for url in urls:
            try:
                result = await self.scan_url(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scanning {url}: {str(e)}")
                results.append(ScanResult(
                    url=url,
                    findings=[],
                    errors=[str(e)],
                    response_time=0.0,
                    status_code=0,
                    headers={},
                    content_length=0
                ))
        
        return results
    
    async def make_request(self, url: str, method: str = "GET", **kwargs) -> aiohttp.ClientResponse:
        """Make an HTTP request with rate limiting."""
        if not self.session:
            raise RuntimeError("Scanner not initialized. Use async context manager.")
        
        # Apply rate limiting
        parsed_url = urlparse(url)
        host = parsed_url.hostname or "unknown"
        
        await self.rate_limiter.acquire(host)
        
        try:
            response = await self.session.request(method, url, **kwargs)
            await self.rate_limiter.release(host, success=True)
            return response
        except Exception as e:
            await self.rate_limiter.release(host, success=False)
            raise e
    
    def create_finding(
        self,
        url: str,
        finding_type: FindingType,
        title: str,
        description: str,
        severity: FindingSeverity,
        **kwargs
    ) -> Finding:
        """Create a finding."""
        return Finding(
            scan_id=kwargs.get("scan_id", ""),
            target_id=kwargs.get("target_id", ""),
            title=title,
            description=description,
            severity=severity,
            finding_type=finding_type,
            url=url,
            method=kwargs.get("method", "GET"),
            parameter=kwargs.get("parameter"),
            payload=kwargs.get("payload"),
            response_code=kwargs.get("response_code"),
            impact=kwargs.get("impact", "Impact not specified"),
            likelihood=kwargs.get("likelihood", "medium"),
            risk_score=kwargs.get("risk_score", 5.0),
            tags=kwargs.get("tags", []),
            references=kwargs.get("references", []),
            raw_data=kwargs.get("raw_data", {}),
        )
    
    def is_safe_to_scan(self, url: str) -> bool:
        """Check if URL is safe to scan."""
        parsed = urlparse(url)
        
        # Check for dangerous file extensions
        dangerous_extensions = [
            ".exe", ".bat", ".cmd", ".com", ".pif", ".scr", ".vbs", ".js",
            ".jar", ".war", ".ear", ".zip", ".tar", ".gz", ".bz2", ".7z"
        ]
        
        path = parsed.path.lower()
        if any(path.endswith(ext) for ext in dangerous_extensions):
            return False
        
        # Check for sensitive paths
        sensitive_paths = [
            "/admin", "/wp-admin", "/administrator", "/phpmyadmin",
            "/.git", "/.svn", "/.env", "/config", "/backup"
        ]
        
        if any(path.startswith(sensitive) for sensitive in sensitive_paths):
            return False
        
        return True
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for consistent processing."""
        parsed = urlparse(url)
        
        # Remove fragment
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        
        return normalized
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.hostname or ""
    
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain."""
        domain1 = self.extract_domain(url1)
        domain2 = self.extract_domain(url2)
        return domain1 == domain2
    
    def get_scan_stats(self) -> Dict[str, Any]:
        """Get scanner statistics."""
        return {
            "name": self.name,
            "rate_limiter_stats": self.rate_limiter.get_stats(),
        }

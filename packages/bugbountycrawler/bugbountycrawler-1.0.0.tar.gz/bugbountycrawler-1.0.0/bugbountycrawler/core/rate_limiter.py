"""Rate limiting and politeness controls for BugBountyCrawler."""

import asyncio
import time
import random
from typing import Dict, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    requests_per_second: float = 1.0
    burst_size: int = 10
    min_delay: float = 0.1
    max_delay: float = 5.0
    jitter: float = 0.1  # Random jitter as percentage
    backoff_factor: float = 2.0
    max_backoff: float = 60.0


@dataclass
class HostLimits:
    """Rate limits for a specific host."""
    
    config: RateLimitConfig
    last_request: float = 0.0
    request_times: deque = field(default_factory=deque)
    consecutive_errors: int = 0
    backoff_until: float = 0.0
    
    def can_make_request(self) -> bool:
        """Check if we can make a request now."""
        now = time.time()
        
        # Check if we're in backoff period
        if now < self.backoff_until:
            return False
        
        # Remove old request times outside the window
        window_start = now - 1.0
        while self.request_times and self.request_times[0] < window_start:
            self.request_times.popleft()
        
        # Check if we're within rate limit
        return len(self.request_times) < self.config.requests_per_second
    
    def record_request(self) -> None:
        """Record a successful request."""
        now = time.time()
        self.last_request = now
        self.request_times.append(now)
        self.consecutive_errors = 0
    
    def record_error(self) -> None:
        """Record a request error and apply backoff."""
        self.consecutive_errors += 1
        
        if self.consecutive_errors > 0:
            # Apply exponential backoff
            backoff_time = min(
                self.config.min_delay * (self.config.backoff_factor ** self.consecutive_errors),
                self.config.max_backoff
            )
            self.backoff_until = time.time() + backoff_time
            logger.warning(f"Backing off {self.consecutive_errors} errors for {backoff_time:.2f}s")
    
    def get_delay(self) -> float:
        """Calculate delay before next request."""
        now = time.time()
        
        # If in backoff, return remaining backoff time
        if now < self.backoff_until:
            return self.backoff_until - now
        
        # Calculate delay based on rate limit
        if not self.request_times:
            return self.config.min_delay
        
        # Calculate time since last request
        time_since_last = now - self.last_request
        min_interval = 1.0 / self.config.requests_per_second
        
        if time_since_last >= min_interval:
            delay = self.config.min_delay
        else:
            delay = min_interval - time_since_last
        
        # Add jitter
        jitter = random.uniform(0, self.config.jitter * delay)
        delay += jitter
        
        # Clamp to min/max delay
        return max(self.config.min_delay, min(delay, self.config.max_delay))


class RateLimiter:
    """Rate limiter with per-host controls and backoff."""
    
    def __init__(self, default_config: Optional[RateLimitConfig] = None):
        """Initialize rate limiter."""
        self.default_config = default_config or RateLimitConfig()
        self.host_limits: Dict[str, HostLimits] = {}
        self.global_semaphore = asyncio.Semaphore(10)  # Global concurrency limit
        self._lock = asyncio.Lock()
    
    def _get_host_limits(self, host: str) -> HostLimits:
        """Get or create host limits for a host."""
        if host not in self.host_limits:
            self.host_limits[host] = HostLimits(config=self.default_config)
        return self.host_limits[host]
    
    async def acquire(self, host: str) -> None:
        """Acquire permission to make a request to a host."""
        async with self._lock:
            host_limits = self._get_host_limits(host)
            
            # Wait for rate limit
            while not host_limits.can_make_request():
                delay = host_limits.get_delay()
                logger.debug(f"Rate limiting {host}: waiting {delay:.2f}s")
                await asyncio.sleep(delay)
            
            # Wait for global concurrency limit
            await self.global_semaphore.acquire()
    
    async def release(self, host: str, success: bool = True) -> None:
        """Release a request slot and record the result."""
        async with self._lock:
            host_limits = self._get_host_limits(host)
            
            if success:
                host_limits.record_request()
            else:
                host_limits.record_error()
            
            self.global_semaphore.release()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass
    
    def get_stats(self) -> Dict[str, Dict[str, any]]:
        """Get rate limiting statistics."""
        stats = {}
        for host, limits in self.host_limits.items():
            stats[host] = {
                "requests_per_second": limits.config.requests_per_second,
                "consecutive_errors": limits.consecutive_errors,
                "backoff_until": limits.backoff_until,
                "recent_requests": len(limits.request_times),
                "last_request": limits.last_request,
            }
        return stats
    
    def reset_host(self, host: str) -> None:
        """Reset rate limits for a specific host."""
        if host in self.host_limits:
            del self.host_limits[host]
    
    def reset_all(self) -> None:
        """Reset all rate limits."""
        self.host_limits.clear()


class PolitenessController:
    """Controls politeness and respectful scanning behavior."""
    
    def __init__(self, rate_limiter: RateLimiter):
        """Initialize politeness controller."""
        self.rate_limiter = rate_limiter
        self.respect_robots_txt = True
        self.respect_retry_after = True
        self.user_agent = "BugBountyCrawler/1.0.0 (Ethical Security Testing)"
        self.scanned_hosts: Set[str] = set()
        self.host_scan_times: Dict[str, float] = {}
        self.min_scan_interval = 3600  # 1 hour between full scans
    
    async def should_scan_host(self, host: str) -> bool:
        """Check if we should scan a host based on politeness rules."""
        now = time.time()
        
        # Check if we've scanned this host recently
        if host in self.host_scan_times:
            time_since_scan = now - self.host_scan_times[host]
            if time_since_scan < self.min_scan_interval:
                logger.info(f"Skipping {host}: scanned {time_since_scan:.0f}s ago")
                return False
        
        return True
    
    async def record_host_scan(self, host: str) -> None:
        """Record that we've scanned a host."""
        self.host_scan_times[host] = time.time()
        self.scanned_hosts.add(host)
    
    async def get_scan_delay(self, host: str) -> float:
        """Get recommended delay before scanning a host."""
        # Base delay from rate limiter
        host_limits = self.rate_limiter._get_host_limits(host)
        base_delay = host_limits.get_delay()
        
        # Add extra delay for hosts we've scanned before
        if host in self.scanned_hosts:
            base_delay *= 2  # Double delay for repeat scans
        
        return base_delay
    
    def should_respect_robots_txt(self, url: str) -> bool:
        """Check if we should respect robots.txt for a URL."""
        if not self.respect_robots_txt:
            return False
        
        # Don't respect robots.txt for specific paths that are commonly scanned
        sensitive_paths = ["/admin", "/api", "/.well-known", "/security"]
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        return not any(path.startswith(sensitive) for sensitive in sensitive_paths)
    
    async def check_retry_after(self, response_headers: Dict[str, str]) -> Optional[float]:
        """Check for Retry-After header and return delay if present."""
        if not self.respect_retry_after:
            return None
        
        retry_after = response_headers.get("retry-after")
        if not retry_after:
            return None
        
        try:
            # Parse Retry-After header (can be seconds or HTTP date)
            if retry_after.isdigit():
                return float(retry_after)
            else:
                # Try to parse as HTTP date
                from email.utils import parsedate_to_datetime
                retry_time = parsedate_to_datetime(retry_after)
                delay = (retry_time - datetime.now()).total_seconds()
                return max(0, delay)
        except (ValueError, TypeError):
            logger.warning(f"Invalid Retry-After header: {retry_after}")
            return None


"""Scanner manager for BugBountyCrawler."""

import asyncio
from typing import List, Dict, Any, Optional
import logging

from .base import BaseScanner, ScanResult
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
from ..core.config import Settings
from ..core.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class ScannerManager:
    """Manages multiple scanners and coordinates scanning operations."""
    
    def __init__(self, settings: Settings):
        """Initialize scanner manager."""
        self.settings = settings
        self.rate_limiter = RateLimiter()
        self.scanners: List[BaseScanner] = []
        self._initialize_scanners()
    
    def _initialize_scanners(self) -> None:
        """Initialize all available scanners."""
        scanner_classes = [
            SecurityHeadersScanner,
            CORSScanner,
            SSLScanner,
            DirectoryTraversalScanner,
            InformationDisclosureScanner,
            RateLimitingScanner,
            OpenRedirectScanner,
            AssetDiscoveryScanner,
            # Phase 1 - High Priority Web Vulnerabilities
            SQLInjectionScanner,
            XSSScanner,
            IDORScanner,
            AuthenticationScanner,
            APISecurityScanner,
            # Phase 2 - Infrastructure & Cloud Vulnerabilities
            S3BucketScanner,
            CloudMetadataScanner,
            IAMScanner,
            NetworkScanner,
            KubernetesScanner,
            DNSScanner,
            SecretScanner,
        ]
        
        for scanner_class in scanner_classes:
            try:
                scanner = scanner_class(self.settings, self.rate_limiter)
                self.scanners.append(scanner)
                logger.info(f"Initialized scanner: {scanner.name}")
            except Exception as e:
                logger.error(f"Failed to initialize scanner {scanner_class.__name__}: {str(e)}")
    
    async def scan_url(self, url: str) -> List[ScanResult]:
        """Scan a single URL with all enabled scanners."""
        results = []
        
        # Run scanners concurrently
        tasks = []
        for scanner in self.scanners:
            if self._is_scanner_enabled(scanner):
                task = asyncio.create_task(self._scan_with_scanner(scanner, url))
                tasks.append(task)
        
        # Wait for all scans to complete
        if tasks:
            scan_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in scan_results:
                if isinstance(result, Exception):
                    logger.error(f"Scanner error: {str(result)}")
                elif isinstance(result, ScanResult):
                    results.append(result)
        
        return results
    
    async def scan_urls(self, urls: List[str]) -> List[ScanResult]:
        """Scan multiple URLs with all enabled scanners."""
        all_results = []
        
        # Process URLs in batches to avoid overwhelming the target
        batch_size = self.settings.max_concurrent
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            
            # Scan batch concurrently
            tasks = [self.scan_url(url) for url in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch scan error: {str(result)}")
                elif isinstance(result, list):
                    all_results.extend(result)
            
            # Add delay between batches
            if i + batch_size < len(urls):
                await asyncio.sleep(self.settings.request_delay)
        
        return all_results
    
    async def _scan_with_scanner(self, scanner: BaseScanner, url: str) -> ScanResult:
        """Scan URL with a specific scanner."""
        try:
            async with scanner:
                return await scanner.scan_url(url)
        except Exception as e:
            logger.error(f"Error with scanner {scanner.name}: {str(e)}")
            return ScanResult(
                url=url,
                findings=[],
                errors=[str(e)],
                response_time=0.0,
                status_code=0,
                headers={},
                content_length=0
            )
    
    def _is_scanner_enabled(self, scanner: BaseScanner) -> bool:
        """Check if scanner is enabled."""
        # Check if scanner is in allowed list
        if self.settings.allowed_plugins:
            return scanner.name in self.settings.allowed_plugins
        
        # Default: enable all scanners
        return True
    
    def get_enabled_scanners(self) -> List[str]:
        """Get list of enabled scanner names."""
        return [scanner.name for scanner in self.scanners if self._is_scanner_enabled(scanner)]
    
    def enable_scanner(self, scanner_name: str) -> bool:
        """Enable a specific scanner."""
        for scanner in self.scanners:
            if scanner.name == scanner_name:
                # Add to allowed plugins if not already there
                if scanner_name not in self.settings.allowed_plugins:
                    self.settings.allowed_plugins.append(scanner_name)
                return True
        return False
    
    def disable_scanner(self, scanner_name: str) -> bool:
        """Disable a specific scanner."""
        if scanner_name in self.settings.allowed_plugins:
            self.settings.allowed_plugins.remove(scanner_name)
            return True
        return False
    
    def get_scanner_stats(self) -> Dict[str, Any]:
        """Get statistics for all scanners."""
        stats = {
            "total_scanners": len(self.scanners),
            "enabled_scanners": len(self.get_enabled_scanners()),
            "scanner_names": [scanner.name for scanner in self.scanners],
            "enabled_scanner_names": self.get_enabled_scanners(),
        }
        
        # Add individual scanner stats
        for scanner in self.scanners:
            if self._is_scanner_enabled(scanner):
                stats[f"{scanner.name}_stats"] = scanner.get_scan_stats()
        
        return stats
    
    async def cleanup(self) -> None:
        """Cleanup scanner manager resources."""
        # Cleanup rate limiter
        if hasattr(self.rate_limiter, 'cleanup'):
            await self.rate_limiter.cleanup()
        
        logger.info("Scanner manager cleaned up")

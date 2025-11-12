"""Web crawler for BugBountyCrawler."""

import asyncio
from typing import List, Dict, Any
import aiohttp
from urllib.parse import urlparse

from .base import BaseCrawler, CrawlResult

class WebCrawler(BaseCrawler):
    """Standard web crawler for static content."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize web crawler."""
        super().__init__(settings, rate_limiter)
        self.name = "WebCrawler"
    
    async def crawl_url(self, url: str, depth: int = 0) -> CrawlResult:
        """Crawl a single URL."""
        discovered_urls = []
        forms = []
        parameters = []
        technologies = []
        status_code = 0
        response_time = 0.0
        content_length = 0
        errors = []
        
        try:
            # Make request
            response = await self.make_request(url)
            status_code = response.status
            response_time = response.headers.get("X-Response-Time", 0.0)
            content_length = int(response.headers.get("Content-Length", 0))
            
            # Only process successful responses
            if status_code == 200:
                # Get response content
                html = await response.text()
                
                # Extract links
                discovered_urls = self._extract_links(html, url)
                
                # Extract forms
                forms = self._extract_forms(html, url)
                
                # Extract parameters from URL
                parameters = self._extract_parameters(url)
                
                # Detect technologies
                technologies = self._detect_technologies(html, dict(response.headers))
                
                # Filter discovered URLs
                discovered_urls = self._filter_discovered_urls(discovered_urls, url)
        
        except Exception as e:
            errors.append(str(e))
        
        return CrawlResult(
            url=url,
            discovered_urls=discovered_urls,
            forms=forms,
            parameters=parameters,
            technologies=technologies,
            status_code=status_code,
            response_time=response_time,
            content_length=content_length,
            errors=errors
        )
    
    def _filter_discovered_urls(self, urls: List[str], base_url: str) -> List[str]:
        """Filter discovered URLs to only include relevant ones."""
        filtered_urls = []
        base_domain = urlparse(base_url).netloc
        
        for url in urls:
            # Check if URL is valid
            if not self._is_valid_url(url):
                continue
            
            # Check if URL should be excluded
            if self._should_exclude_url(url):
                continue
            
            # Check if URL is from the same domain
            url_domain = urlparse(url).netloc
            if url_domain != base_domain:
                continue
            
            # Check if URL is already discovered
            if url in self.discovered_urls:
                continue
            
            filtered_urls.append(url)
        
        return filtered_urls
    
    def _is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain."""
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        return domain1 == domain2





















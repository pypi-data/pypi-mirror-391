"""Base crawler class for BugBountyCrawler."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
import re
import logging

from ..core.config import Settings
from ..core.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """Result of a crawl operation."""
    
    url: str
    discovered_urls: List[str]
    forms: List[Dict[str, Any]]
    parameters: List[str]
    technologies: List[str]
    status_code: int
    response_time: float
    content_length: int
    errors: List[str]


class BaseCrawler(ABC):
    """Base class for all crawlers."""
    
    def __init__(self, settings: Settings, rate_limiter: Optional[RateLimiter] = None):
        """Initialize crawler."""
        self.settings = settings
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session: Optional[aiohttp.ClientSession] = None
        self.name = self.__class__.__name__
        
        # Crawl state
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.max_depth = settings.max_depth
        self.max_pages = settings.max_pages
        
        # URL patterns to exclude
        self.exclude_patterns = [
            r"\\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$",
            r"\\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|tar|gz)$",
            r"\\.(mp3|mp4|avi|mov|wmv|flv|webm)$",
            r"/admin/",
            r"/wp-admin/",
            r"/administrator/",
            r"/phpmyadmin/",
            r"/\\.git/",
            r"/\\.svn/",
            r"/config/",
            r"/backup/",
            r"/logs/",
            r"/tmp/",
            r"/var/log/",
        ]
        
        # Compile exclude patterns
        self.compiled_exclude_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.exclude_patterns]
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
    
    async def setup(self) -> None:
        """Setup crawler resources."""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=self.settings.timeout)
        
        headers = {
            "User-Agent": self.settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
    
    async def cleanup(self) -> None:
        """Cleanup crawler resources."""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def crawl_url(self, url: str, depth: int = 0) -> CrawlResult:
        """Crawl a single URL."""
        pass
    
    async def crawl_target(self, target: str) -> List[str]:
        """Crawl a target and return discovered URLs."""
        self.visited_urls.clear()
        self.discovered_urls.clear()
        
        # Normalize target URL
        if not target.startswith(("http://", "https://")):
            target = f"https://{target}"
        
        # Start crawling
        await self._crawl_recursive(target, 0)
        
        return list(self.discovered_urls)
    
    async def _crawl_recursive(self, url: str, depth: int) -> None:
        """Recursively crawl URLs."""
        # Check depth limit
        if depth > self.max_depth:
            return
        
        # Check page limit
        if len(self.visited_urls) >= self.max_pages:
            return
        
        # Check if URL should be excluded
        if self._should_exclude_url(url):
            return
        
        # Check if already visited
        if url in self.visited_urls:
            return
        
        # Mark as visited
        self.visited_urls.add(url)
        
        try:
            # Crawl URL
            result = await self.crawl_url(url, depth)
            
            # Add discovered URLs
            for discovered_url in result.discovered_urls:
                if self._is_valid_url(discovered_url):
                    self.discovered_urls.add(discovered_url)
            
            # Recursively crawl discovered URLs
            for discovered_url in result.discovered_urls:
                if self._is_valid_url(discovered_url) and discovered_url not in self.visited_urls:
                    await self._crawl_recursive(discovered_url, depth + 1)
        
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
    
    def _should_exclude_url(self, url: str) -> bool:
        """Check if URL should be excluded from crawling."""
        for pattern in self.compiled_exclude_patterns:
            if pattern.search(url):
                return True
        return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling."""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalize URL relative to base URL."""
        try:
            # Handle relative URLs
            if not url.startswith(("http://", "https://")):
                url = urljoin(base_url, url)
            
            # Parse and normalize
            parsed = urlparse(url)
            
            # Remove fragment
            normalized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                ""
            ))
            
            return normalized
        except:
            return url
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        links = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract href attributes
            for tag in soup.find_all(['a', 'link']):
                href = tag.get('href')
                if href:
                    normalized_url = self._normalize_url(href, base_url)
                    if self._is_valid_url(normalized_url):
                        links.append(normalized_url)
            
            # Extract src attributes
            for tag in soup.find_all(['img', 'script', 'iframe', 'embed', 'object']):
                src = tag.get('src')
                if src:
                    normalized_url = self._normalize_url(src, base_url)
                    if self._is_valid_url(normalized_url):
                        links.append(normalized_url)
            
            # Extract action attributes from forms
            for form in soup.find_all('form'):
                action = form.get('action')
                if action:
                    normalized_url = self._normalize_url(action, base_url)
                    if self._is_valid_url(normalized_url):
                        links.append(normalized_url)
        
        except Exception as e:
            logger.error(f"Error extracting links from {base_url}: {str(e)}")
        
        return links
    
    def _extract_forms(self, html: str, base_url: str) -> List[Dict[str, Any]]:
        """Extract forms from HTML content."""
        forms = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for form in soup.find_all('form'):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET').upper(),
                    'enctype': form.get('enctype', 'application/x-www-form-urlencoded'),
                    'inputs': []
                }
                
                # Extract form inputs
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        'name': input_tag.get('name', ''),
                        'type': input_tag.get('type', 'text'),
                        'value': input_tag.get('value', ''),
                        'required': input_tag.has_attr('required'),
                        'placeholder': input_tag.get('placeholder', ''),
                    }
                    
                    # Extract options for select elements
                    if input_tag.name == 'select':
                        options = []
                        for option in input_tag.find_all('option'):
                            options.append({
                                'value': option.get('value', ''),
                                'text': option.get_text(strip=True)
                            })
                        input_data['options'] = options
                    
                    form_data['inputs'].append(input_data)
                
                # Normalize action URL
                if form_data['action']:
                    form_data['action'] = self._normalize_url(form_data['action'], base_url)
                
                forms.append(form_data)
        
        except Exception as e:
            logger.error(f"Error extracting forms from {base_url}: {str(e)}")
        
        return forms
    
    def _extract_parameters(self, url: str) -> List[str]:
        """Extract parameters from URL."""
        parameters = []
        
        try:
            parsed = urlparse(url)
            if parsed.query:
                # Parse query string
                from urllib.parse import parse_qs
                query_params = parse_qs(parsed.query)
                parameters.extend(query_params.keys())
        except:
            pass
        
        return parameters
    
    def _detect_technologies(self, html: str, headers: Dict[str, str]) -> List[str]:
        """Detect technologies used on the page."""
        technologies = []
        
        # Check HTML content for technology indicators
        html_lower = html.lower()
        
        # JavaScript frameworks
        if 'react' in html_lower or 'reactjs' in html_lower:
            technologies.append('React')
        if 'angular' in html_lower or 'ng-' in html_lower:
            technologies.append('Angular')
        if 'vue' in html_lower or 'vuejs' in html_lower:
            technologies.append('Vue.js')
        if 'jquery' in html_lower:
            technologies.append('jQuery')
        
        # Server technologies
        if 'php' in html_lower or '<?php' in html_lower:
            technologies.append('PHP')
        if 'asp.net' in html_lower or 'aspx' in html_lower:
            technologies.append('ASP.NET')
        if 'jsp' in html_lower or 'java' in html_lower:
            technologies.append('Java')
        if 'python' in html_lower or 'django' in html_lower or 'flask' in html_lower:
            technologies.append('Python')
        
        # Check headers for technology indicators
        server = headers.get('Server', '').lower()
        if 'apache' in server:
            technologies.append('Apache')
        elif 'nginx' in server:
            technologies.append('Nginx')
        elif 'iis' in server:
            technologies.append('IIS')
        
        # Check for specific headers
        if 'X-Powered-By' in headers:
            technologies.append(headers['X-Powered-By'])
        
        return list(set(technologies))  # Remove duplicates
    
    async def make_request(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make an HTTP request with rate limiting."""
        if not self.session:
            raise RuntimeError("Crawler not initialized. Use async context manager.")
        
        # Apply rate limiting
        parsed_url = urlparse(url)
        host = parsed_url.hostname or "unknown"
        
        await self.rate_limiter.acquire(host)
        
        try:
            response = await self.session.request("GET", url, **kwargs)
            await self.rate_limiter.release(host, success=True)
            return response
        except Exception as e:
            await self.rate_limiter.release(host, success=False)
            raise e





















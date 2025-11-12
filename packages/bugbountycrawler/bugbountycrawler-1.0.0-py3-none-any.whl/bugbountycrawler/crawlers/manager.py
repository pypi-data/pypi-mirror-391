"""Crawler manager for BugBountyCrawler."""

import asyncio
from typing import List, Dict, Any, Optional
import logging

from .base import BaseCrawler, CrawlResult
from .web_crawler import WebCrawler
from .spa_crawler import SPACrawler
from ..core.config import Settings
from ..core.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class CrawlerManager:
    """Manages multiple crawlers and coordinates crawling operations."""
    
    def __init__(self, settings: Settings):
        """Initialize crawler manager."""
        self.settings = settings
        self.rate_limiter = RateLimiter()
        self.crawlers: List[BaseCrawler] = []
        self._initialize_crawlers()
    
    def _initialize_crawlers(self) -> None:
        """Initialize all available crawlers."""
        crawler_classes = [
            WebCrawler,
            SPACrawler,
        ]
        
        for crawler_class in crawler_classes:
            try:
                crawler = crawler_class(self.settings, self.rate_limiter)
                self.crawlers.append(crawler)
                logger.info(f"Initialized crawler: {crawler.name}")
            except Exception as e:
                logger.error(f"Failed to initialize crawler {crawler_class.__name__}: {str(e)}")
    
    async def crawl_target(self, target: str) -> List[str]:
        """Crawl a target and return discovered URLs."""
        all_discovered_urls = set()
        
        # Try each crawler
        for crawler in self.crawlers:
            if self._is_crawler_enabled(crawler):
                try:
                    async with crawler:
                        discovered_urls = await crawler.crawl_target(target)
                        all_discovered_urls.update(discovered_urls)
                        logger.info(f"Crawler {crawler.name} discovered {len(discovered_urls)} URLs")
                except Exception as e:
                    logger.error(f"Error with crawler {crawler.name}: {str(e)}")
        
        return list(all_discovered_urls)
    
    async def crawl_url(self, url: str) -> CrawlResult:
        """Crawl a single URL with the best available crawler."""
        # Choose the best crawler for the URL
        crawler = self._choose_best_crawler(url)
        
        if not crawler:
            raise RuntimeError("No suitable crawler available")
        
        async with crawler:
            return await crawler.crawl_url(url)
    
    def _choose_best_crawler(self, url: str) -> Optional[BaseCrawler]:
        """Choose the best crawler for a URL."""
        # For now, prefer SPA crawler if JavaScript is enabled
        if self.settings.enable_javascript:
            for crawler in self.crawlers:
                if isinstance(crawler, SPACrawler) and self._is_crawler_enabled(crawler):
                    return crawler
        
        # Fall back to web crawler
        for crawler in self.crawlers:
            if isinstance(crawler, WebCrawler) and self._is_crawler_enabled(crawler):
                return crawler
        
        return None
    
    def _is_crawler_enabled(self, crawler: BaseCrawler) -> bool:
        """Check if crawler is enabled."""
        # Check if crawler is in allowed list
        if self.settings.allowed_plugins:
            return crawler.name in self.settings.allowed_plugins
        
        # Default: enable all crawlers
        return True
    
    def get_enabled_crawlers(self) -> List[str]:
        """Get list of enabled crawler names."""
        return [crawler.name for crawler in self.crawlers if self._is_crawler_enabled(crawler)]
    
    def enable_crawler(self, crawler_name: str) -> bool:
        """Enable a specific crawler."""
        for crawler in self.crawlers:
            if crawler.name == crawler_name:
                # Add to allowed plugins if not already there
                if crawler_name not in self.settings.allowed_plugins:
                    self.settings.allowed_plugins.append(crawler_name)
                return True
        return False
    
    def disable_crawler(self, crawler_name: str) -> bool:
        """Disable a specific crawler."""
        if crawler_name in self.settings.allowed_plugins:
            self.settings.allowed_plugins.remove(crawler_name)
            return True
        return False
    
    def get_crawler_stats(self) -> Dict[str, Any]:
        """Get statistics for all crawlers."""
        stats = {
            "total_crawlers": len(self.crawlers),
            "enabled_crawlers": len(self.get_enabled_crawlers()),
            "crawler_names": [crawler.name for crawler in self.crawlers],
            "enabled_crawler_names": self.get_enabled_crawlers(),
        }
        
        # Add individual crawler stats
        for crawler in self.crawlers:
            if self._is_crawler_enabled(crawler):
                stats[f"{crawler.name}_stats"] = crawler.get_scan_stats()
        
        return stats
    
    async def cleanup(self) -> None:
        """Cleanup crawler manager resources."""
        # Cleanup rate limiter
        if hasattr(self.rate_limiter, 'cleanup'):
            await self.rate_limiter.cleanup()
        
        logger.info("Crawler manager cleaned up")





















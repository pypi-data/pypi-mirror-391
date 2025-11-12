"""SPA (Single Page Application) crawler for BugBountyCrawler."""

import asyncio
from typing import List, Dict, Any
from urllib.parse import urlparse

from .base import BaseCrawler, CrawlResult

class SPACrawler(BaseCrawler):
    """Crawler for Single Page Applications using Playwright."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize SPA crawler."""
        super().__init__(settings, rate_limiter)
        self.name = "SPACrawler"
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def setup(self) -> None:
        """Setup SPA crawler resources."""
        await super().setup()
        
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            
            # Create browser context
            self.context = await self.browser.new_context(
                user_agent=self.settings.user_agent,
                viewport={'width': 1920, 'height': 1080}
            )
        
        except ImportError:
            raise RuntimeError("Playwright not installed. Install with: pip install playwright && playwright install")
        except Exception as e:
            raise RuntimeError(f"Failed to setup Playwright: {str(e)}")
    
    async def cleanup(self) -> None:
        """Cleanup SPA crawler resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        await super().cleanup()
    
    async def crawl_url(self, url: str, depth: int = 0) -> CrawlResult:
        """Crawl a single URL using Playwright."""
        discovered_urls = []
        forms = []
        parameters = []
        technologies = []
        status_code = 0
        response_time = 0.0
        content_length = 0
        errors = []
        
        try:
            if not self.context:
                raise RuntimeError("Browser context not initialized")
            
            # Create new page
            page = await self.context.new_page()
            
            # Set up event listeners
            page.on("response", lambda response: self._handle_response(response))
            
            # Navigate to URL
            start_time = asyncio.get_event_loop().time()
            response = await page.goto(url, wait_until="networkidle", timeout=self.settings.timeout * 1000)
            end_time = asyncio.get_event_loop().time()
            
            response_time = end_time - start_time
            status_code = response.status if response else 0
            
            # Wait for dynamic content if enabled
            if self.settings.wait_for_dynamic_content:
                await asyncio.sleep(self.settings.max_wait_time)
            
            # Get page content
            html = await page.content()
            content_length = len(html)
            
            # Extract links
            discovered_urls = await self._extract_links_js(page, url)
            
            # Extract forms
            forms = await self._extract_forms_js(page, url)
            
            # Extract parameters from URL
            parameters = self._extract_parameters(url)
            
            # Detect technologies
            technologies = await self._detect_technologies_js(page, html)
            
            # Filter discovered URLs
            discovered_urls = self._filter_discovered_urls(discovered_urls, url)
            
            # Close page
            await page.close()
        
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
    
    async def _extract_links_js(self, page, base_url: str) -> List[str]:
        """Extract links using JavaScript execution."""
        try:
            # Execute JavaScript to extract all links
            links = await page.evaluate("""
                () => {
                    const links = [];
                    
                    // Get all anchor tags
                    document.querySelectorAll('a[href]').forEach(a => {
                        links.push(a.href);
                    });
                    
                    // Get all form actions
                    document.querySelectorAll('form[action]').forEach(form => {
                        links.push(form.action);
                    });
                    
                    // Get all iframe sources
                    document.querySelectorAll('iframe[src]').forEach(iframe => {
                        links.push(iframe.src);
                    });
                    
                    // Get all script sources
                    document.querySelectorAll('script[src]').forEach(script => {
                        links.push(script.src);
                    });
                    
                    // Get all image sources
                    document.querySelectorAll('img[src]').forEach(img => {
                        links.push(img.src);
                    });
                    
                    return links;
                }
            """)
            
            # Normalize URLs
            normalized_links = []
            for link in links:
                normalized = self._normalize_url(link, base_url)
                if self._is_valid_url(normalized):
                    normalized_links.append(normalized)
            
            return normalized_links
        
        except Exception as e:
            print(f"Error extracting links with JavaScript: {str(e)}")
            return []
    
    async def _extract_forms_js(self, page, base_url: str) -> List[Dict[str, Any]]:
        """Extract forms using JavaScript execution."""
        try:
            # Execute JavaScript to extract all forms
            forms = await page.evaluate("""
                () => {
                    const forms = [];
                    
                    document.querySelectorAll('form').forEach(form => {
                        const formData = {
                            action: form.action || '',
                            method: (form.method || 'GET').toUpperCase(),
                            enctype: form.enctype || 'application/x-www-form-urlencoded',
                            inputs: []
                        };
                        
                        // Extract form inputs
                        form.querySelectorAll('input, textarea, select').forEach(input => {
                            const inputData = {
                                name: input.name || '',
                                type: input.type || 'text',
                                value: input.value || '',
                                required: input.required || false,
                                placeholder: input.placeholder || ''
                            };
                            
                            // Extract options for select elements
                            if (input.tagName === 'SELECT') {
                                const options = [];
                                input.querySelectorAll('option').forEach(option => {
                                    options.push({
                                        value: option.value || '',
                                        text: option.textContent.trim()
                                    });
                                });
                                inputData.options = options;
                            }
                            
                            formData.inputs.push(inputData);
                        });
                        
                        forms.push(formData);
                    });
                    
                    return forms;
                }
            """)
            
            # Normalize action URLs
            for form in forms:
                if form['action']:
                    form['action'] = self._normalize_url(form['action'], base_url)
            
            return forms
        
        except Exception as e:
            print(f"Error extracting forms with JavaScript: {str(e)}")
            return []
    
    async def _detect_technologies_js(self, page, html: str) -> List[str]:
        """Detect technologies using JavaScript execution."""
        technologies = []
        
        try:
            # Check for JavaScript frameworks
            framework_checks = await page.evaluate("""
                () => {
                    const frameworks = [];
                    
                    // Check for React
                    if (window.React || document.querySelector('[data-reactroot]')) {
                        frameworks.push('React');
                    }
                    
                    // Check for Angular
                    if (window.angular || document.querySelector('[ng-app]')) {
                        frameworks.push('Angular');
                    }
                    
                    // Check for Vue
                    if (window.Vue || document.querySelector('[v-if]')) {
                        frameworks.push('Vue.js');
                    }
                    
                    // Check for jQuery
                    if (window.jQuery || window.$) {
                        frameworks.push('jQuery');
                    }
                    
                    // Check for other libraries
                    if (window.lodash) {
                        frameworks.push('Lodash');
                    }
                    
                    if (window.moment) {
                        frameworks.push('Moment.js');
                    }
                    
                    return frameworks;
                }
            """)
            
            technologies.extend(framework_checks)
            
            # Also check HTML content for server-side technologies
            html_technologies = self._detect_technologies(html, {})
            technologies.extend(html_technologies)
            
            # Remove duplicates
            return list(set(technologies))
        
        except Exception as e:
            print(f"Error detecting technologies with JavaScript: {str(e)}")
            return []
    
    def _handle_response(self, response):
        """Handle response events from Playwright."""
        # This can be used to track network requests
        pass





















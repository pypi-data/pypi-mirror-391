"""Open redirect scanner for BugBountyCrawler."""

import re
from typing import List, Dict, Any
from urllib.parse import urlparse, urljoin, parse_qs
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class OpenRedirectScanner(BaseScanner):
    """Scanner for open redirect vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize open redirect scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "OpenRedirectScanner"
        
        # Common redirect parameters
        self.redirect_params = [
            'redirect', 'url', 'next', 'return', 'continue', 'goto', 'target',
            'destination', 'r', 'u', 'link', 'href', 'src', 'dest', 'forward',
            'callback', 'ret', 'returnTo', 'return_to', 'returnUrl', 'return_url',
            'redirectTo', 'redirect_to', 'redirectUrl', 'redirect_url',
            'nextUrl', 'next_url', 'continueUrl', 'continue_url',
            'targetUrl', 'target_url', 'destUrl', 'dest_url',
            'location', 'path', 'uri', 'page', 'view', 'action'
        ]
        
        # Malicious redirect targets
        self.malicious_targets = [
            'https://evil.com',
            'https://attacker.com',
            'https://malicious.com',
            'https://phishing.com',
            '//evil.com',
            '/\\evil.com',
            '\\evil.com',
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            'vbscript:msgbox(1)',
            'file:///etc/passwd',
            'ftp://evil.com',
            '\\\\evil.com\\share',
            'https://google.com',
            'https://facebook.com',
            'https://twitter.com',
            'https://youtube.com'
        ]
        
        # Protocol bypass techniques
        self.protocol_bypasses = [
            '//',
            '\\\\',
            '/\\',
            '\\/',
            'javascript:',
            'data:',
            'vbscript:',
            'file:',
            'ftp:',
            'gopher:',
            'ldap:',
            'jar:',
            'php:',
            'vbs:',
            'about:',
            'chrome:',
            'chrome-extension:'
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for open redirect vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Make initial request to get baseline
            baseline_response = await self.make_request(url)
            response_time = baseline_response.headers.get("X-Response-Time", 0.0)
            status_code = baseline_response.status
            headers = dict(baseline_response.headers)
            content_length = int(baseline_response.headers.get("Content-Length", 0))
            
            # Test 1: Direct parameter testing
            param_findings = await self._test_redirect_parameters(url)
            findings.extend(param_findings)
            
            # Test 2: Form-based redirects
            form_findings = await self._test_form_redirects(url)
            findings.extend(form_findings)
            
            # Test 3: Header-based redirects
            header_findings = await self._test_header_redirects(url)
            findings.extend(header_findings)
            
            # Test 4: URL parsing bypasses
            bypass_findings = await self._test_url_bypasses(url)
            findings.extend(bypass_findings)
            
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
    
    async def _test_redirect_parameters(self, url: str) -> List[Finding]:
        """Test URL parameters for open redirect vulnerabilities."""
        findings = []
        
        # Parse existing URL parameters
        parsed_url = urlparse(url)
        existing_params = parse_qs(parsed_url.query)
        
        # Test each redirect parameter
        for param in self.redirect_params:
            for target in self.malicious_targets:
                try:
                    # Test direct parameter injection
                    test_url = f"{url}?{param}={target}"
                    response = await self.make_request(test_url, allow_redirects=False)
                    
                    # Check for redirect
                    redirect_found = await self._check_redirect_response(response, target, param)
                    if redirect_found:
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.OPEN_REDIRECT,
                            title=f"Open Redirect via {param} Parameter",
                            description=f"Open redirect vulnerability found in {param} parameter. Redirects to: {target}",
                            severity=FindingSeverity.MEDIUM,
                            impact="Open redirect can be used for phishing attacks and credential theft",
                            likelihood="high",
                            risk_score=7.0,
                            references=[
                                "https://owasp.org/www-community/attacks/Unvalidated_Redirects_and_Forwards_Cheat_Sheet",
                                "https://cwe.mitre.org/data/definitions/601.html"
                            ],
                            raw_data={
                                "parameter": param,
                                "malicious_target": target,
                                "test_url": test_url,
                                "redirect_location": response.headers.get('Location', ''),
                                "status_code": response.status
                            }
                        )
                        findings.append(finding)
                        break  # Found vulnerability, no need to test other targets for this param
                
                except Exception as e:
                    continue  # Skip failed tests
        
        return findings
    
    async def _test_form_redirects(self, url: str) -> List[Finding]:
        """Test form-based redirects."""
        findings = []
        
        try:
            # Get the page content to find forms
            response = await self.make_request(url)
            content = await response.text()
            
            # Look for forms with redirect functionality
            form_patterns = [
                r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>',
                r'<input[^>]*name=["\'](redirect|url|next|return)["\'][^>]*>',
                r'<input[^>]*type=["\']hidden["\'][^>]*name=["\'](redirect|url|next|return)["\'][^>]*>'
            ]
            
            for pattern in form_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Found potential redirect form
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.OPEN_REDIRECT,
                        title="Potential Form-Based Redirect",
                        description="Form found that may contain redirect functionality",
                        severity=FindingSeverity.LOW,
                        impact="Forms with redirect parameters may be vulnerable to open redirect attacks",
                        likelihood="medium",
                        risk_score=4.0,
                        references=[
                            "https://owasp.org/www-community/attacks/Unvalidated_Redirects_and_Forwards_Cheat_Sheet"
                        ],
                        raw_data={
                            "form_pattern": pattern,
                            "matches": matches,
                            "content_snippet": content[:500] if len(content) > 500 else content
                        }
                    )
                    findings.append(finding)
        
        except Exception as e:
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.OPEN_REDIRECT,
                title="Form Redirect Test Failed",
                description=f"Form redirect test failed: {str(e)}",
                severity=FindingSeverity.LOW,
                impact="Unable to test form-based redirects",
                likelihood="low",
                risk_score=1.0,
                raw_data={"error": str(e), "test_type": "form_redirects"}
            )
            findings.append(finding)
        
        return findings
    
    async def _test_header_redirects(self, url: str) -> List[Finding]:
        """Test header-based redirects."""
        findings = []
        
        # Common redirect headers
        redirect_headers = [
            'X-Redirect-To',
            'X-Forward-To',
            'X-Forward-URL',
            'X-Original-URL',
            'X-Rewrite-URL',
            'X-Redirect',
            'X-Location',
            'X-Forward',
            'X-Return-URL',
            'X-Callback-URL'
        ]
        
        for header in redirect_headers:
            for target in self.malicious_targets[:5]:  # Test fewer targets for headers
                try:
                    headers = {header: target}
                    response = await self.make_request(url, headers=headers, allow_redirects=False)
                    
                    redirect_found = await self._check_redirect_response(response, target, header)
                    if redirect_found:
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.OPEN_REDIRECT,
                            title=f"Open Redirect via {header} Header",
                            description=f"Open redirect vulnerability found via {header} header. Redirects to: {target}",
                            severity=FindingSeverity.HIGH,
                            impact="Header-based open redirect can be used for advanced phishing attacks",
                            likelihood="medium",
                            risk_score=8.0,
                            references=[
                                "https://owasp.org/www-community/attacks/Unvalidated_Redirects_and_Forwards_Cheat_Sheet"
                            ],
                            raw_data={
                                "header": header,
                                "malicious_target": target,
                                "redirect_location": response.headers.get('Location', ''),
                                "status_code": response.status
                            }
                        )
                        findings.append(finding)
                        break
                
                except Exception as e:
                    continue
        
        return findings
    
    async def _test_url_bypasses(self, url: str) -> List[Finding]:
        """Test URL parsing bypass techniques."""
        findings = []
        
        # Test URL parsing bypasses
        bypass_payloads = [
            '//evil.com',
            '/\\evil.com',
            '\\evil.com',
            '//\\evil.com',
            '\\//evil.com',
            '/%2F%2Fevil.com',
            '/%5C%5Cevil.com',
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            'vbscript:msgbox(1)'
        ]
        
        for payload in bypass_payloads:
            try:
                # Test with different parameters
                for param in self.redirect_params[:5]:  # Test fewer parameters for bypasses
                    test_url = f"{url}?{param}={payload}"
                    response = await self.make_request(test_url, allow_redirects=False)
                    
                    redirect_found = await self._check_redirect_response(response, payload, param)
                    if redirect_found:
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.OPEN_REDIRECT,
                            title=f"Open Redirect via URL Bypass",
                            description=f"Open redirect vulnerability found using URL parsing bypass. Payload: {payload}",
                            severity=FindingSeverity.HIGH,
                            impact="URL parsing bypass can be used to bypass redirect validation",
                            likelihood="high",
                            risk_score=8.5,
                            references=[
                                "https://owasp.org/www-community/attacks/Unvalidated_Redirects_and_Forwards_Cheat_Sheet",
                                "https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Open%20Redirect"
                            ],
                            raw_data={
                                "parameter": param,
                                "bypass_payload": payload,
                                "test_url": test_url,
                                "redirect_location": response.headers.get('Location', ''),
                                "status_code": response.status
                            }
                        )
                        findings.append(finding)
                        break  # Found vulnerability, move to next payload
            
            except Exception as e:
                continue
        
        return findings
    
    async def _check_redirect_response(self, response, target: str, source: str) -> bool:
        """Check if response contains a redirect to the target."""
        if not response:
            return False
        
        # Check Location header
        location = response.headers.get('Location', '').lower()
        if location and target.lower() in location:
            return True
        
        # Check Refresh header
        refresh = response.headers.get('Refresh', '').lower()
        if refresh and target.lower() in refresh:
            return True
        
        # Check meta refresh in content
        if response.status == 200:
            try:
                content = await response.text()
                if content:
                    # Look for meta refresh
                    meta_refresh_pattern = r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*url=([^"\']*)["\'][^>]*>'
                    matches = re.findall(meta_refresh_pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        if target.lower() in match.lower():
                            return True
                    
                    # Look for JavaScript redirects
                    js_redirect_patterns = [
                        r'window\.location\s*=\s*["\']([^"\']*)["\']',
                        r'window\.location\.href\s*=\s*["\']([^"\']*)["\']',
                        r'location\.href\s*=\s*["\']([^"\']*)["\']',
                        r'location\.replace\s*\(\s*["\']([^"\']*)["\']'
                    ]
                    
                    for pattern in js_redirect_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if target.lower() in match.lower():
                                return True
            
            except Exception:
                pass
        
        # Check for 3xx status codes with redirect
        if response.status in [301, 302, 303, 307, 308]:
            return True
        
        return False
    
    def _extract_parameters_from_url(self, url: str) -> Dict[str, List[str]]:
        """Extract parameters from URL."""
        try:
            parsed = urlparse(url)
            return parse_qs(parsed.query)
        except Exception:
            return {}
    
    def _build_test_url(self, base_url: str, param: str, value: str) -> str:
        """Build test URL with parameter."""
        separator = '&' if '?' in base_url else '?'
        return f"{base_url}{separator}{param}={value}"

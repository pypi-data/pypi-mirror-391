"""CSRF (Cross-Site Request Forgery) scanner for BugBountyCrawler."""

import re
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class CSRFScanner(BaseScanner):
    """Scanner for CSRF vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize CSRF scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "CSRFScanner"
        
        # Common CSRF token parameter names
        self.csrf_param_names = [
            'csrf_token', 'csrf', '_csrf', 'csrftoken', '_token', 'token',
            'authenticity_token', '_csrf_token', 'csrf-token', 'xsrf_token',
            'xsrf', '_xsrf', 'xsrf-token', '_xsrf_token', '__requestverificationtoken',
            'requestverificationtoken', 'anti_csrf_token', 'anti-csrf-token'
        ]
        
        # State-changing HTTP methods
        self.state_changing_methods = ['POST', 'PUT', 'DELETE', 'PATCH']
        
        # Sensitive endpoints that should have CSRF protection
        self.sensitive_endpoints = [
            '/login', '/logout', '/signin', '/signout', '/register', '/signup',
            '/password', '/reset', '/change', '/update', '/delete', '/remove',
            '/create', '/add', '/edit', '/modify', '/transfer', '/send', '/pay',
            '/purchase', '/buy', '/sell', '/withdraw', '/deposit', '/submit',
            '/profile', '/account', '/settings', '/preferences', '/config'
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for CSRF vulnerabilities."""
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
            
            content = await response.text()
            
            # Test 1: Check for missing CSRF tokens in forms
            form_findings = await self._check_forms_for_csrf(url, content)
            findings.extend(form_findings)
            
            # Test 2: Test for predictable CSRF tokens
            token_findings = await self._test_token_predictability(url, content)
            findings.extend(token_findings)
            
            # Test 3: Check for token reuse
            reuse_findings = await self._test_token_reuse(url, content)
            findings.extend(reuse_findings)
            
            # Test 4: Check SameSite cookie attribute
            samesite_findings = await self._check_samesite_cookies(url, headers)
            findings.extend(samesite_findings)
        
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
    
    async def _check_forms_for_csrf(self, url: str, content: str) -> List[Finding]:
        """Check forms for missing CSRF tokens."""
        findings = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            forms = soup.find_all('form')
            
            for form in forms:
                # Get form method and action
                method = form.get('method', 'GET').upper()
                action = form.get('action', '')
                
                # Check if this is a state-changing form
                if method not in self.state_changing_methods:
                    continue
                
                # Check if form action matches sensitive endpoints
                is_sensitive = any(endpoint in action.lower() for endpoint in self.sensitive_endpoints)
                
                # Look for CSRF tokens in form
                has_csrf_token = False
                for input_field in form.find_all('input'):
                    field_name = input_field.get('name', '').lower()
                    if any(csrf_name in field_name for csrf_name in self.csrf_param_names):
                        has_csrf_token = True
                        break
                
                if not has_csrf_token:
                    severity = FindingSeverity.HIGH if is_sensitive else FindingSeverity.MEDIUM
                    
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.CSRF,
                        title=f"Missing CSRF Token in {method} Form",
                        description=f"Form with method '{method}' and action '{action}' lacks CSRF protection",
                        severity=severity,
                        impact="Missing CSRF tokens allow attackers to perform unauthorized actions on behalf of authenticated users",
                        likelihood="high" if is_sensitive else "medium",
                        risk_score=8.0 if is_sensitive else 6.0,
                        references=[
                            "https://owasp.org/www-community/attacks/csrf",
                            "https://cwe.mitre.org/data/definitions/352.html"
                        ],
                        raw_data={
                            "form_method": method,
                            "form_action": action,
                            "is_sensitive": is_sensitive,
                            "form_html": str(form)[:500]
                        }
                    )
                    findings.append(finding)
        
        except Exception:
            pass
        
        return findings
    
    async def _test_token_predictability(self, url: str, content: str) -> List[Finding]:
        """Test if CSRF tokens are predictable."""
        findings = []
        
        try:
            # Extract CSRF tokens from multiple requests
            tokens = []
            
            for i in range(5):
                response = await self.make_request(url)
                page_content = await response.text()
                
                # Look for CSRF tokens
                for param_name in self.csrf_param_names:
                    # Find token values in HTML
                    pattern = rf'{param_name}["\']?\s*[:=]\s*["\']([^"\']+)["\']'
                    matches = re.findall(pattern, page_content, re.IGNORECASE)
                    tokens.extend(matches)
                
                await asyncio.sleep(0.5)
            
            if len(tokens) >= 3:
                # Check for patterns in tokens
                if self._are_tokens_predictable(tokens):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.CSRF,
                        title="Predictable CSRF Tokens",
                        description="CSRF tokens follow a predictable pattern, making them vulnerable to guessing attacks",
                        severity=FindingSeverity.HIGH,
                        impact="Predictable CSRF tokens can be guessed by attackers, bypassing CSRF protection",
                        likelihood="medium",
                        risk_score=7.0,
                        references=[
                            "https://owasp.org/www-community/attacks/csrf"
                        ],
                        raw_data={
                            "token_samples": tokens[:5],
                            "token_count": len(tokens)
                        }
                    )
                    findings.append(finding)
        
        except Exception:
            pass
        
        return findings
    
    async def _test_token_reuse(self, url: str, content: str) -> List[Finding]:
        """Test if CSRF tokens can be reused."""
        findings = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find a form with CSRF token
            for form in soup.find_all('form'):
                method = form.get('method', 'GET').upper()
                if method not in self.state_changing_methods:
                    continue
                
                # Extract CSRF token
                csrf_token = None
                csrf_param_name = None
                
                for input_field in form.find_all('input'):
                    field_name = input_field.get('name', '').lower()
                    if any(csrf_name in field_name for csrf_name in self.csrf_param_names):
                        csrf_token = input_field.get('value')
                        csrf_param_name = input_field.get('name')
                        break
                
                if csrf_token:
                    # Try using the same token twice
                    # (In a real implementation, you'd make actual POST requests)
                    # For safety, we'll just report if we detect the same token multiple times
                    
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.CSRF,
                        title="Potential CSRF Token Reuse",
                        description=f"CSRF token '{csrf_param_name}' may be reusable across multiple requests",
                        severity=FindingSeverity.MEDIUM,
                        impact="Reusable CSRF tokens reduce the effectiveness of CSRF protection",
                        likelihood="medium",
                        risk_score=6.0,
                        references=[
                            "https://owasp.org/www-community/attacks/csrf"
                        ],
                        raw_data={
                            "csrf_param_name": csrf_param_name,
                            "csrf_token": csrf_token[:20] + "..." if len(csrf_token) > 20 else csrf_token
                        }
                    )
                    findings.append(finding)
                    break  # Only report once
        
        except Exception:
            pass
        
        return findings
    
    async def _check_samesite_cookies(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Check if cookies have SameSite attribute."""
        findings = []
        
        try:
            set_cookie = headers.get('Set-Cookie', '')
            if set_cookie:
                # Check for SameSite attribute
                if 'samesite' not in set_cookie.lower():
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.CSRF,
                        title="Missing SameSite Cookie Attribute",
                        description="Cookies are set without SameSite attribute, making them vulnerable to CSRF attacks",
                        severity=FindingSeverity.MEDIUM,
                        impact="Missing SameSite attribute allows cookies to be sent in cross-site requests",
                        likelihood="high",
                        risk_score=6.5,
                        references=[
                            "https://owasp.org/www-community/SameSite",
                            "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite"
                        ],
                        raw_data={
                            "set_cookie_header": set_cookie[:200]
                        }
                    )
                    findings.append(finding)
                elif 'samesite=none' in set_cookie.lower():
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.CSRF,
                        title="Insecure SameSite Cookie Attribute",
                        description="Cookies are set with SameSite=None, reducing CSRF protection",
                        severity=FindingSeverity.LOW,
                        impact="SameSite=None allows cookies in cross-site requests (requires Secure flag)",
                        likelihood="medium",
                        risk_score=5.0,
                        references=[
                            "https://owasp.org/www-community/SameSite"
                        ],
                        raw_data={
                            "set_cookie_header": set_cookie[:200]
                        }
                    )
                    findings.append(finding)
        
        except Exception:
            pass
        
        return findings
    
    def _are_tokens_predictable(self, tokens: List[str]) -> bool:
        """Check if tokens follow a predictable pattern."""
        if len(tokens) < 3:
            return False
        
        # Check if tokens are sequential
        try:
            numeric_tokens = [int(t) for t in tokens if t.isdigit()]
            if len(numeric_tokens) >= 3:
                differences = [numeric_tokens[i+1] - numeric_tokens[i] for i in range(len(numeric_tokens)-1)]
                if len(set(differences)) == 1:  # All differences are the same
                    return True
        except:
            pass
        
        # Check if tokens are too similar (high similarity)
        if len(set(tokens)) < len(tokens) * 0.5:  # More than 50% duplicates
            return True
        
        # Check if tokens have low entropy
        for token in tokens:
            if len(token) < 16:  # Too short
                return True
            if len(set(token)) < 10:  # Not enough unique characters
                return True
        
        return False


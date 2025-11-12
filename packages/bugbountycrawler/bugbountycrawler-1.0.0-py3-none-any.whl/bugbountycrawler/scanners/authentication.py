"""Authentication scanner for BugBountyCrawler."""

import re
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class AuthenticationScanner(BaseScanner):
    """Scanner for authentication vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize authentication scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "AuthenticationScanner"
        
        # Common weak passwords
        self.weak_passwords = [
            'password', '123456', 'password123', 'admin', 'root', 'guest',
            'user', 'test', 'demo', 'default', 'changeme', 'password1',
            '123456789', 'qwerty', 'abc123', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'hello', 'login', 'pass', 'pass123',
            '12345', '1234', '111111', '000000', '123123', '654321',
            'superman', 'qazwsx', 'michael', 'football', 'iloveyou',
            'welcome123', 'admin123', 'root123', 'test123', 'demo123',
            'password1', 'password12', 'password123', 'changeme123',
            '12345678', '1234567890', 'qwerty123', 'abc123456',
            'letmein123', 'welcome123', 'monkey123', 'dragon123',
            'master123', 'hello123', 'login123', 'pass123456',
        ]
        
        # Common default credentials
        self.default_credentials = [
            ('admin', 'admin'), ('admin', 'password'), ('admin', '123456'),
            ('root', 'root'), ('root', 'password'), ('root', '123456'),
            ('administrator', 'administrator'), ('administrator', 'password'),
            ('user', 'user'), ('user', 'password'), ('user', '123456'),
            ('guest', 'guest'), ('guest', 'password'), ('guest', '123456'),
            ('test', 'test'), ('test', 'password'), ('test', '123456'),
            ('demo', 'demo'), ('demo', 'password'), ('demo', '123456'),
            ('default', 'default'), ('default', 'password'), ('default', '123456'),
            ('service', 'service'), ('service', 'password'), ('service', '123456'),
            ('support', 'support'), ('support', 'password'), ('support', '123456'),
            ('info', 'info'), ('info', 'password'), ('info', '123456'),
            ('webmaster', 'webmaster'), ('webmaster', 'password'),
            ('postmaster', 'postmaster'), ('postmaster', 'password'),
            ('nobody', 'nobody'), ('nobody', 'password'),
            ('apache', 'apache'), ('apache', 'password'),
            ('nginx', 'nginx'), ('nginx', 'password'),
            ('mysql', 'mysql'), ('mysql', 'password'),
            ('postgres', 'postgres'), ('postgres', 'password'),
            ('oracle', 'oracle'), ('oracle', 'password'),
        ]
        
        # Session-related parameters
        self.session_params = [
            'session_id', 'sessionid', 'session', 'sess', 'sid', 'jsessionid',
            'phpsessid', 'aspsessionid', 'cfid', 'cftoken', 'aspnet_sessionid',
            'session_token', 'auth_token', 'access_token', 'bearer_token',
            'csrf_token', 'csrf', 'xsrf_token', 'xsrf', 'authenticity_token',
            'remember_token', 'remember_me', 'stay_logged_in', 'auto_login',
            'persistent_login', 'session_cookie', 'auth_cookie', 'login_cookie',
        ]
        
        # Authentication bypass techniques
        self.bypass_techniques = [
            'admin', 'administrator', 'root', 'superuser', 'manager', 'moderator',
            'user', 'guest', 'anonymous', 'public', 'default', 'test', 'demo',
            'null', 'empty', 'blank', 'none', 'undefined', 'false', 'true',
            '1', '0', '-1', '999', '999999', 'admin@', 'admin@example.com',
            'admin%00', 'admin%20', 'admin%09', 'admin%0a', 'admin%0d',
            'admin%27', 'admin%22', 'admin%5c', 'admin%2f', 'admin%3a',
            'admin%3b', 'admin%3d', 'admin%26', 'admin%7c', 'admin%21',
            'admin%40', 'admin%23', 'admin%24', 'admin%25', 'admin%5e',
            'admin%26', 'admin%2a', 'admin%28', 'admin%29', 'admin%2b',
            'admin%2d', 'admin%3d', 'admin%5b', 'admin%5d', 'admin%7b',
            'admin%7d', 'admin%7c', 'admin%5c', 'admin%3a', 'admin%3b',
            'admin%22', 'admin%27', 'admin%3c', 'admin%3e', 'admin%2c',
            'admin%2e', 'admin%2f', 'admin%3f', 'admin%60', 'admin%7e',
        ]
        
        # Session fixation indicators
        self.session_fixation_indicators = [
            r'session_id\s*=\s*[a-zA-Z0-9]+',
            r'sessionid\s*=\s*[a-zA-Z0-9]+',
            r'session\s*=\s*[a-zA-Z0-9]+',
            r'sess\s*=\s*[a-zA-Z0-9]+',
            r'sid\s*=\s*[a-zA-Z0-9]+',
            r'jsessionid\s*=\s*[a-zA-Z0-9]+',
            r'phpsessid\s*=\s*[a-zA-Z0-9]+',
            r'aspsessionid\s*=\s*[a-zA-Z0-9]+',
            r'cfid\s*=\s*[a-zA-Z0-9]+',
            r'cftoken\s*=\s*[a-zA-Z0-9]+',
            r'aspnet_sessionid\s*=\s*[a-zA-Z0-9]+',
        ]
        
        # Weak session token patterns
        self.weak_token_patterns = [
            r'^[0-9]+$',  # Numeric only
            r'^[a-zA-Z]+$',  # Alphabetic only
            r'^[a-zA-Z0-9]{1,8}$',  # Short tokens
            r'^[a-zA-Z0-9]{32}$',  # MD5-like but might be weak
            r'^[a-zA-Z0-9]{40}$',  # SHA1-like but might be weak
            r'^[a-zA-Z0-9]{64}$',  # SHA256-like but might be weak
            r'^[A-Za-z0-9+/]{20,}={0,2}$',  # Base64-like but might be weak
            r'^[A-Za-z0-9_-]{10,}$',  # Alphanumeric with special chars but might be weak
        ]
        
        # Predictable session token patterns
        self.predictable_patterns = [
            r'^[0-9]{1,10}$',  # Sequential numbers
            r'^[a-zA-Z]{1,10}$',  # Sequential letters
            r'^[a-zA-Z0-9]{1,10}$',  # Sequential alphanumeric
            r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$',  # Date patterns
            r'^[0-9]{2}:[0-9]{2}:[0-9]{2}$',  # Time patterns
            r'^[0-9]{4}[0-9]{2}[0-9]{2}$',  # Date without separators
            r'^[0-9]{2}[0-9]{2}[0-9]{2}$',  # Time without separators
            r'^[0-9]{10}$',  # Timestamp-like
            r'^[0-9]{13}$',  # Millisecond timestamp-like
            r'^[0-9]{16}$',  # Microsecond timestamp-like
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for authentication vulnerabilities."""
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
            
            # Test for authentication bypass
            bypass_findings = await self._test_authentication_bypass(url, headers)
            findings.extend(bypass_findings)
            
            # Test for weak password handling
            weak_password_findings = await self._test_weak_password_handling(url)
            findings.extend(weak_password_findings)
            
            # Test for session management issues
            session_findings = await self._test_session_management(url, headers)
            findings.extend(session_findings)
            
            # Test for predictable session tokens
            predictable_findings = await self._test_predictable_tokens(url, headers)
            findings.extend(predictable_findings)
            
            # Test for missing authentication
            missing_auth_findings = await self._test_missing_authentication(url, headers)
            findings.extend(missing_auth_findings)
            
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
    
    async def _test_authentication_bypass(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Test for authentication bypass vulnerabilities."""
        findings = []
        
        # Test common authentication bypass techniques
        for bypass_technique in self.bypass_techniques[:10]:  # Test first 10 techniques
            try:
                # Create headers with bypass technique
                test_headers = headers.copy()
                test_headers['Authorization'] = f'Bearer {bypass_technique}'
                test_headers['X-Forwarded-User'] = bypass_technique
                test_headers['X-Remote-User'] = bypass_technique
                test_headers['X-User'] = bypass_technique
                test_headers['X-Auth-User'] = bypass_technique
                test_headers['X-Login-User'] = bypass_technique
                test_headers['X-Admin-User'] = bypass_technique
                test_headers['X-Root-User'] = bypass_technique
                test_headers['X-Super-User'] = bypass_technique
                test_headers['X-Manager-User'] = bypass_technique
                test_headers['X-Moderator-User'] = bypass_technique
                
                response = await self.make_request(url, headers=test_headers)
                content = await response.text()
                
                # Check if bypass was successful
                if self._is_authentication_bypass_successful(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.AUTHENTICATION_BYPASS,
                        title=f"Authentication Bypass - Header Manipulation",
                        description=f"Authentication bypass detected using header manipulation technique: {bypass_technique}",
                        severity=FindingSeverity.CRITICAL,
                        impact="Authentication bypass can lead to unauthorized access to sensitive resources and administrative functions",
                        likelihood="medium",
                        risk_score=9.5,
                        references=[
                            "https://owasp.org/www-community/attacks/Authentication_Bypass",
                            "https://cwe.mitre.org/data/definitions/287.html"
                        ],
                        raw_data={
                            "bypass_technique": bypass_technique,
                            "headers_used": list(test_headers.keys()),
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "bypass_type": "header_manipulation"
                        }
                    )
                    findings.append(finding)
                    break  # Found vulnerability, no need to test more techniques
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_weak_password_handling(self, url: str) -> List[Finding]:
        """Test for weak password handling vulnerabilities."""
        findings = []
        
        # Test common weak passwords
        for password in self.weak_passwords[:10]:  # Test first 10 passwords
            try:
                # Create test data with weak password
                test_data = {
                    'password': password,
                    'passwd': password,
                    'pwd': password,
                    'pass': password,
                    'login_password': password,
                    'user_password': password,
                    'admin_password': password,
                    'root_password': password,
                }
                
                # Test with different usernames
                for username in ['admin', 'administrator', 'root', 'user', 'test']:
                    test_data['username'] = username
                    test_data['user'] = username
                    test_data['login'] = username
                    test_data['email'] = f'{username}@example.com'
                    
                    response = await self.make_request(url, method='POST', data=test_data)
                    content = await response.text()
                    
                    # Check if weak password was accepted
                    if self._is_weak_password_accepted(content, response.status):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.AUTHENTICATION_BYPASS,
                            title=f"Weak Password Accepted - {username}/{password}",
                            description=f"Weak password '{password}' was accepted for username '{username}'",
                            severity=FindingSeverity.HIGH,
                            impact="Weak password acceptance can lead to unauthorized access through brute force attacks",
                            likelihood="high",
                            risk_score=8.0,
                            references=[
                                "https://owasp.org/www-community/attacks/Weak_Password_Policy",
                                "https://cwe.mitre.org/data/definitions/521.html"
                            ],
                            raw_data={
                                "username": username,
                                "password": password,
                                "response_status": response.status,
                                "response_content": content[:500] if len(content) > 500 else content,
                                "weak_password_type": "common_password"
                            }
                        )
                        findings.append(finding)
                        break  # Found vulnerability, no need to test more passwords
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_session_management(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Test for session management vulnerabilities."""
        findings = []
        
        # Check for session fixation indicators
        for indicator in self.session_fixation_indicators:
            if re.search(indicator, str(headers), re.IGNORECASE):
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.SESSION_MANAGEMENT,
                    title="Session Fixation Vulnerability",
                    description=f"Session fixation vulnerability detected. Session token pattern: {indicator}",
                    severity=FindingSeverity.HIGH,
                    impact="Session fixation can lead to session hijacking and unauthorized access",
                    likelihood="medium",
                    risk_score=7.5,
                    references=[
                        "https://owasp.org/www-community/attacks/Session_Fixation",
                        "https://cwe.mitre.org/data/definitions/384.html"
                    ],
                    raw_data={
                        "indicator": indicator,
                        "headers": headers,
                        "session_management_type": "session_fixation"
                    }
                )
                findings.append(finding)
                break  # Found vulnerability, no need to test more indicators
        
        return findings
    
    async def _test_predictable_tokens(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Test for predictable session tokens."""
        findings = []
        
        # Check for predictable token patterns in headers
        for header_name, header_value in headers.items():
            if any(session_param in header_name.lower() for session_param in self.session_params):
                for pattern in self.predictable_patterns:
                    if re.match(pattern, header_value):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.SESSION_MANAGEMENT,
                            title=f"Predictable Session Token - {header_name}",
                            description=f"Predictable session token detected in header '{header_name}'. Pattern: {pattern}",
                            severity=FindingSeverity.HIGH,
                            impact="Predictable session tokens can lead to session hijacking and unauthorized access",
                            likelihood="high",
                            risk_score=8.0,
                            references=[
                                "https://owasp.org/www-community/attacks/Session_Prediction",
                                "https://cwe.mitre.org/data/definitions/330.html"
                            ],
                            raw_data={
                                "header_name": header_name,
                                "header_value": header_value,
                                "pattern": pattern,
                                "session_management_type": "predictable_token"
                            }
                        )
                        findings.append(finding)
                        break  # Found vulnerability, no need to test more patterns
        
        return findings
    
    async def _test_missing_authentication(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Test for missing authentication."""
        findings = []
        
        # Check if sensitive endpoints are accessible without authentication
        sensitive_paths = ['/admin', '/administrator', '/root', '/manager', '/moderator', '/api/admin', '/api/users', '/api/accounts']
        
        for path in sensitive_paths:
            try:
                test_url = f"{url.rstrip('/')}{path}"
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check if sensitive endpoint is accessible without authentication
                if self._is_sensitive_endpoint_accessible(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.AUTHENTICATION_BYPASS,
                        title=f"Missing Authentication - {path}",
                        description=f"Sensitive endpoint '{path}' is accessible without authentication",
                        severity=FindingSeverity.HIGH,
                        impact="Missing authentication on sensitive endpoints can lead to unauthorized access to sensitive resources",
                        likelihood="high",
                        risk_score=8.5,
                        references=[
                            "https://owasp.org/www-community/attacks/Authentication_Bypass",
                            "https://cwe.mitre.org/data/definitions/287.html"
                        ],
                        raw_data={
                            "endpoint": path,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "authentication_type": "missing_authentication"
                        }
                    )
                    findings.append(finding)
                    break  # Found vulnerability, no need to test more endpoints
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    def _is_authentication_bypass_successful(self, content: str, status_code: int) -> bool:
        """Check if authentication bypass was successful."""
        # Check for success indicators
        success_indicators = [
            r'200\s+OK',
            r'Content-Type:\s*application/json',
            r'Content-Type:\s*text/html',
            r'"success":\s*true',
            r'"status":\s*"success"',
            r'"error":\s*false',
            r'"authenticated":\s*true',
            r'"authorized":\s*true',
            r'"access":\s*"granted"',
            r'"permission":\s*"allowed"',
            r'"admin":\s*true',
            r'"administrator":\s*true',
            r'"root":\s*true',
            r'"superuser":\s*true',
            r'"manager":\s*true',
            r'"moderator":\s*true',
        ]
        
        for indicator in success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _is_weak_password_accepted(self, content: str, status_code: int) -> bool:
        """Check if weak password was accepted."""
        # Check for success indicators
        success_indicators = [
            r'"success":\s*true',
            r'"status":\s*"success"',
            r'"error":\s*false',
            r'"login":\s*"successful"',
            r'"authentication":\s*"successful"',
            r'"access":\s*"granted"',
            r'"welcome"',
            r'"dashboard"',
            r'"profile"',
            r'"account"',
            r'"user"',
            r'"admin"',
            r'"administrator"',
            r'"root"',
            r'"manager"',
            r'"moderator"',
        ]
        
        for indicator in success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _is_sensitive_endpoint_accessible(self, content: str, status_code: int) -> bool:
        """Check if sensitive endpoint is accessible without authentication."""
        # Check for success indicators
        success_indicators = [
            r'200\s+OK',
            r'Content-Type:\s*application/json',
            r'Content-Type:\s*text/html',
            r'"success":\s*true',
            r'"status":\s*"success"',
            r'"error":\s*false',
            r'"admin"',
            r'"administrator"',
            r'"root"',
            r'"manager"',
            r'"moderator"',
            r'"user"',
            r'"account"',
            r'"profile"',
            r'"dashboard"',
            r'"control"',
            r'"management"',
            r'"settings"',
            r'"configuration"',
            r'"system"',
        ]
        
        for indicator in success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False

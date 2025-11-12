"""Information disclosure scanner for BugBountyCrawler."""

import re
from typing import List, Dict, Any
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType

class InformationDisclosureScanner(BaseScanner):
    """Scanner for information disclosure vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize information disclosure scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "InformationDisclosureScanner"
        
        # Sensitive information patterns
        self.sensitive_patterns = {
            "api_key": [
                r"api[_-]?key['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9+/=]{20,})['\"]?",
                r"apikey['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9+/=]{20,})['\"]?",
            ],
            "jwt_token": [
                r"eyJ[A-Za-z0-9+/=]+\.[A-Za-z0-9+/=]+\.[A-Za-z0-9+/=]+",
            ],
            "aws_access_key": [
                r"AKIA[0-9A-Z]{16}",
                r"aws[_-]?access[_-]?key['\"]?\s*[:=]\s*['\"]?([A-Z0-9]{20})['\"]?",
            ],
            "aws_secret_key": [
                r"aws[_-]?secret[_-]?key['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
            ],
            "database_url": [
                r"mysql://[^\\s]+",
                r"postgres://[^\\s]+",
                r"mongodb://[^\\s]+",
                r"redis://[^\\s]+",
            ],
            "password": [
                r"password['\"]?\s*[:=]\s*['\"]?([^'\"\\s]{8,})['\"]?",
                r"pwd['\"]?\s*[:=]\s*['\"]?([^'\"\\s]{8,})['\"]?",
            ],
            "email": [
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
            ],
            "credit_card": [
                r"\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\\b",
            ],
            "ssn": [
                r"\\b\\d{3}-\\d{2}-\\d{4}\\b",
            ],
            "private_key": [
                r"-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----",
            ],
            "certificate": [
                r"-----BEGIN CERTIFICATE-----",
            ],
        }
        
        # File paths that might contain sensitive information
        self.sensitive_paths = [
            "/.env",
            "/.env.local",
            "/.env.production",
            "/config/database.yml",
            "/config/secrets.yml",
            "/.git/config",
            "/.svn/entries",
            "/backup/",
            "/logs/",
            "/tmp/",
            "/var/log/",
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for information disclosure."""
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
            
            # Get response content
            content = await response.text()
            
            # Check for sensitive information in content
            content_findings = self._check_content_for_sensitive_info(url, content)
            findings.extend(content_findings)
            
            # Check for sensitive information in headers
            header_findings = self._check_headers_for_sensitive_info(url, headers)
            findings.extend(header_findings)
            
            # Check for sensitive file paths
            path_findings = await self._check_sensitive_paths(url)
            findings.extend(path_findings)
            
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
    
    def _check_content_for_sensitive_info(self, url: str, content: str) -> List[Finding]:
        """Check response content for sensitive information."""
        findings = []
        
        for info_type, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                if matches:
                    # Redact sensitive information for display
                    redacted_matches = []
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0] if match[0] else match[1]
                        
                        if len(match) > 10:
                            redacted = match[:4] + "..." + match[-4:]
                        else:
                            redacted = "***REDACTED***"
                        redacted_matches.append(redacted)
                    
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        title=f"Sensitive {info_type.replace('_', ' ').title()} Exposed",
                        description=f"Sensitive {info_type.replace('_', ' ')} found in response content: {', '.join(redacted_matches)}",
                        severity=FindingSeverity.HIGH,
                        impact=f"Exposed {info_type.replace('_', ' ')} may lead to unauthorized access",
                        likelihood="high",
                        risk_score=8.0,
                        references=[
                            "https://owasp.org/www-community/vulnerabilities/Information_exposure",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "info_type": info_type,
                            "pattern": pattern,
                            "matches_count": len(matches),
                            "redacted_matches": redacted_matches
                        }
                    )
                    findings.append(finding)
        
        return findings
    
    def _check_headers_for_sensitive_info(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Check response headers for sensitive information."""
        findings = []
        
        # Check for sensitive headers
        sensitive_headers = [
            "X-API-Key",
            "X-Auth-Token",
            "X-Access-Token",
            "Authorization",
            "X-Forwarded-For",
            "X-Real-IP",
            "X-Original-IP",
        ]
        
        for header_name in sensitive_headers:
            if header_name in headers:
                header_value = headers[header_name]
                
                # Redact sensitive value
                if len(header_value) > 10:
                    redacted_value = header_value[:4] + "..." + header_value[-4:]
                else:
                    redacted_value = "***REDACTED***"
                
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.INFORMATION_DISCLOSURE,
                    title=f"Sensitive Header Exposed: {header_name}",
                    description=f"Sensitive header {header_name} is exposed in response: {redacted_value}",
                    severity=FindingSeverity.MEDIUM,
                    impact=f"Exposed {header_name} header may leak sensitive information",
                    likelihood="medium",
                    risk_score=6.0,
                    references=[
                        "https://owasp.org/www-community/vulnerabilities/Information_exposure"
                    ],
                    raw_data={
                        "header_name": header_name,
                        "header_value": redacted_value
                    }
                )
                findings.append(finding)
        
        return findings
    
    async def _check_sensitive_paths(self, url: str) -> List[Finding]:
        """Check for sensitive file paths."""
        findings = []
        
        from urllib.parse import urljoin
        
        for path in self.sensitive_paths:
            try:
                test_url = urljoin(url, path)
                
                # Make request to sensitive path
                response = await self.make_request(test_url)
                
                if response.status == 200:
                    content = await response.text()
                    
                    # Check if content looks like sensitive information
                    if self._looks_like_sensitive_file(content, path):
                        finding = self.create_finding(
                            url=test_url,
                            finding_type=FindingType.INFORMATION_DISCLOSURE,
                            title=f"Sensitive File Exposed: {path}",
                            description=f"Sensitive file {path} is accessible and contains sensitive information",
                            severity=FindingSeverity.HIGH,
                            impact=f"Exposed {path} file may contain sensitive configuration or data",
                            likelihood="high",
                            risk_score=8.0,
                            references=[
                                "https://owasp.org/www-community/vulnerabilities/Information_exposure"
                            ],
                            raw_data={
                                "exposed_path": path,
                                "response_code": response.status,
                                "content_length": len(content)
                            }
                        )
                        findings.append(finding)
            
            except Exception:
                # Continue with next path
                continue
        
        return findings
    
    def _looks_like_sensitive_file(self, content: str, path: str) -> bool:
        """Check if content looks like a sensitive file."""
        content_lower = content.lower()
        
        # Check for common sensitive file indicators
        sensitive_indicators = [
            "password",
            "secret",
            "key",
            "token",
            "api",
            "database",
            "mysql",
            "postgres",
            "redis",
            "mongodb",
            "aws",
            "azure",
            "google",
            "private",
            "certificate",
        ]
        
        # Count how many indicators are present
        indicator_count = sum(1 for indicator in sensitive_indicators if indicator in content_lower)
        
        # If more than 2 indicators are present, it's likely sensitive
        return indicator_count >= 2


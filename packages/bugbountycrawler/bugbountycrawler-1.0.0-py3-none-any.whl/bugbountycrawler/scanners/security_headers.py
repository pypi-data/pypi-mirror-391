"""Security headers scanner for BugBountyCrawler."""

import re
from typing import List, Dict, Any
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType

class SecurityHeadersScanner(BaseScanner):
    """Scanner for security header misconfigurations."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize security headers scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "SecurityHeadersScanner"
        
        # Security headers to check
        self.security_headers = {
            "Strict-Transport-Security": {
                "required": True,
                "severity": FindingSeverity.HIGH,
                "description": "Missing HSTS header allows downgrade attacks",
                "recommended_value": "max-age=31536000; includeSubDomains; preload"
            },
            "Content-Security-Policy": {
                "required": True,
                "severity": FindingSeverity.MEDIUM,
                "description": "Missing CSP header allows XSS attacks",
                "recommended_value": "default-src 'self'"
            },
            "X-Frame-Options": {
                "required": True,
                "severity": FindingSeverity.MEDIUM,
                "description": "Missing X-Frame-Options allows clickjacking",
                "recommended_value": "DENY"
            },
            "X-Content-Type-Options": {
                "required": True,
                "severity": FindingSeverity.LOW,
                "description": "Missing X-Content-Type-Options allows MIME sniffing",
                "recommended_value": "nosniff"
            },
            "Referrer-Policy": {
                "required": False,
                "severity": FindingSeverity.LOW,
                "description": "Missing Referrer-Policy may leak sensitive information",
                "recommended_value": "strict-origin-when-cross-origin"
            },
            "Permissions-Policy": {
                "required": False,
                "severity": FindingSeverity.LOW,
                "description": "Missing Permissions-Policy allows unnecessary permissions",
                "recommended_value": "geolocation=(), microphone=(), camera=()"
            }
        }
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for security header issues."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Make request
            response = await self.make_request(url)
            response_time = response.headers.get("X-Response-Time", 0.0)
            status_code = response.status
            headers = dict(response.headers)
            content_length = int(response.headers.get("Content-Length", 0))
            
            # Check security headers
            findings = await self._check_security_headers(url, headers)
            
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
    
    async def _check_security_headers(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Check for security header issues."""
        findings = []
        
        for header_name, config in self.security_headers.items():
            header_value = headers.get(header_name, "")
            
            if not header_value:
                if config["required"]:
                    # Missing required header
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.SECURITY_HEADERS,
                        title=f"Missing {header_name} Header",
                        description=f"The {header_name} header is missing. {config['description']}",
                        severity=config["severity"],
                        impact=f"Missing {header_name} header may allow security attacks",
                        likelihood="high",
                        risk_score=8.0 if config["severity"] == FindingSeverity.HIGH else 5.0,
                        references=[
                            "https://owasp.org/www-project-secure-headers/",
                            "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers"
                        ],
                        raw_data={
                            "header_name": header_name,
                            "header_value": None,
                            "recommended_value": config["recommended_value"]
                        }
                    )
                    findings.append(finding)
            else:
                # Check header value for issues
                value_issues = self._check_header_value(header_name, header_value)
                if value_issues:
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.SECURITY_HEADERS,
                        title=f"Insecure {header_name} Header Configuration",
                        description=f"The {header_name} header has insecure configuration: {value_issues}",
                        severity=FindingSeverity.MEDIUM,
                        impact=f"Insecure {header_name} configuration may allow security attacks",
                        likelihood="medium",
                        risk_score=6.0,
                        references=[
                            "https://owasp.org/www-project-secure-headers/",
                            "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers"
                        ],
                        raw_data={
                            "header_name": header_name,
                            "header_value": header_value,
                            "issues": value_issues,
                            "recommended_value": config["recommended_value"]
                        }
                    )
                    findings.append(finding)
        
        return findings
    
    def _check_header_value(self, header_name: str, header_value: str) -> List[str]:
        """Check header value for security issues."""
        issues = []
        
        if header_name == "Strict-Transport-Security":
            if "max-age" not in header_value:
                issues.append("Missing max-age directive")
            elif not re.search(r"max-age=\d+", header_value):
                issues.append("Invalid max-age value")
            
            if "includeSubDomains" not in header_value:
                issues.append("Missing includeSubDomains directive")
        
        elif header_name == "Content-Security-Policy":
            if "default-src" not in header_value:
                issues.append("Missing default-src directive")
            elif "'unsafe-inline'" in header_value:
                issues.append("Contains unsafe-inline directive")
            elif "'unsafe-eval'" in header_value:
                issues.append("Contains unsafe-eval directive")
            elif "*" in header_value:
                issues.append("Contains wildcard (*) directive")
        
        elif header_name == "X-Frame-Options":
            if header_value.upper() not in ["DENY", "SAMEORIGIN"]:
                issues.append("Invalid X-Frame-Options value")
        
        elif header_name == "X-Content-Type-Options":
            if header_value.lower() != "nosniff":
                issues.append("Should be 'nosniff'")
        
        elif header_name == "Referrer-Policy":
            valid_policies = [
                "no-referrer", "no-referrer-when-downgrade", "origin",
                "origin-when-cross-origin", "same-origin", "strict-origin",
                "strict-origin-when-cross-origin", "unsafe-url"
            ]
            if header_value not in valid_policies:
                issues.append(f"Invalid Referrer-Policy value: {header_value}")
        
        return issues

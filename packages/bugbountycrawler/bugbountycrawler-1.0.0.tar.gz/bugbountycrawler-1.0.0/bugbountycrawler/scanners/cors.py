"""CORS scanner for BugBountyCrawler."""

import re
from typing import List, Dict, Any
from urllib.parse import urlparse
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType

class CORSScanner(BaseScanner):
    """Scanner for CORS misconfigurations."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize CORS scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "CORSScanner"
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for CORS issues."""
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
            
            # Check CORS headers
            cors_findings = await self._check_cors_headers(url, headers)
            findings.extend(cors_findings)
            
            # Test CORS with preflight request
            preflight_findings = await self._test_cors_preflight(url)
            findings.extend(preflight_findings)
            
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
    
    async def _check_cors_headers(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Check for CORS header issues."""
        findings = []
        
        # Check Access-Control-Allow-Origin
        acao = headers.get("Access-Control-Allow-Origin", "")
        if acao:
            if acao == "*":
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.CORS_MISCONFIGURATION,
                    title="CORS Wildcard Origin",
                    description="Access-Control-Allow-Origin is set to '*' which allows any origin to make requests",
                    severity=FindingSeverity.HIGH,
                    impact="Allows any website to make cross-origin requests, potentially leading to data theft",
                    likelihood="high",
                    risk_score=8.0,
                    references=[
                        "https://owasp.org/www-community/attacks/CORS_OriginHeaderScrutiny",
                        "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS"
                    ],
                    raw_data={
                        "header_name": "Access-Control-Allow-Origin",
                        "header_value": acao,
                        "issue": "wildcard_origin"
                    }
                )
                findings.append(finding)
            
            elif not self._is_valid_origin(acao):
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.CORS_MISCONFIGURATION,
                    title="Invalid CORS Origin",
                    description=f"Access-Control-Allow-Origin has invalid value: {acao}",
                    severity=FindingSeverity.MEDIUM,
                    impact="Invalid CORS configuration may allow unauthorized access",
                    likelihood="medium",
                    risk_score=6.0,
                    references=[
                        "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS"
                    ],
                    raw_data={
                        "header_name": "Access-Control-Allow-Origin",
                        "header_value": acao,
                        "issue": "invalid_origin"
                    }
                )
                findings.append(finding)
        
        # Check Access-Control-Allow-Credentials
        acac = headers.get("Access-Control-Allow-Credentials", "")
        if acac.lower() == "true" and acao == "*":
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.CORS_MISCONFIGURATION,
                title="CORS Credentials with Wildcard Origin",
                description="Access-Control-Allow-Credentials is true with wildcard origin, which is not allowed",
                severity=FindingSeverity.CRITICAL,
                impact="Allows any website to make authenticated requests, leading to complete account takeover",
                likelihood="high",
                risk_score=9.0,
                references=[
                    "https://owasp.org/www-community/attacks/CORS_OriginHeaderScrutiny",
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS"
                ],
                raw_data={
                    "header_name": "Access-Control-Allow-Credentials",
                    "header_value": acac,
                    "access_control_allow_origin": acao,
                    "issue": "credentials_with_wildcard"
                }
            )
            findings.append(finding)
        
        # Check Access-Control-Allow-Methods
        acam = headers.get("Access-Control-Allow-Methods", "")
        if acam:
            dangerous_methods = ["DELETE", "PUT", "PATCH"]
            for method in dangerous_methods:
                if method in acam:
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.CORS_MISCONFIGURATION,
                        title="CORS Allows Dangerous Methods",
                        description=f"Access-Control-Allow-Methods includes dangerous method: {method}",
                        severity=FindingSeverity.MEDIUM,
                        impact=f"Allows cross-origin {method} requests which may lead to data modification",
                        likelihood="medium",
                        risk_score=6.0,
                        references=[
                            "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS"
                        ],
                        raw_data={
                            "header_name": "Access-Control-Allow-Methods",
                            "header_value": acam,
                            "dangerous_method": method,
                            "issue": "dangerous_methods"
                        }
                    )
                    findings.append(finding)
        
        return findings
    
    async def _test_cors_preflight(self, url: str) -> List[Finding]:
        """Test CORS preflight request."""
        findings = []
        
        try:
            # Make preflight request
            headers = {
                "Origin": "https://evil.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            response = await self.make_request(url, method="OPTIONS", headers=headers)
            
            # Check if preflight was successful
            if response.status == 200:
                response_headers = dict(response.headers)
                acao = response_headers.get("Access-Control-Allow-Origin", "")
                
                if acao == "*" or acao == "https://evil.com":
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.CORS_MISCONFIGURATION,
                        title="CORS Preflight Allows Unauthorized Origin",
                        description="CORS preflight request from unauthorized origin was successful",
                        severity=FindingSeverity.HIGH,
                        impact="Allows unauthorized origins to make cross-origin requests",
                        likelihood="high",
                        risk_score=8.0,
                        references=[
                            "https://owasp.org/www-community/attacks/CORS_OriginHeaderScrutiny"
                        ],
                        raw_data={
                            "test_origin": "https://evil.com",
                            "access_control_allow_origin": acao,
                            "issue": "unauthorized_preflight"
                        }
                    )
                    findings.append(finding)
        
        except Exception as e:
            # Preflight test failed, which is actually good
            pass
        
        return findings
    
    def _is_valid_origin(self, origin: str) -> bool:
        """Check if origin is valid."""
        if origin == "*":
            return True
        
        # Check if it's a valid URL
        try:
            parsed = urlparse(origin)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc

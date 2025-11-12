"""Privacy and Compliance scanner for BugBountyCrawler."""

import re
import asyncio
from typing import List, Dict, Any
from urllib.parse import urlparse
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class PrivacyComplianceScanner(BaseScanner):
    """Scanner for privacy and compliance issues (GDPR, CCPA, PII)."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize privacy/compliance scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "PrivacyComplianceScanner"
        
        # PII patterns
        self.pii_patterns = {
            'credit_card': [
                r'\b4[0-9]{12}(?:[0-9]{3})?\b',  # Visa
                r'\b5[1-5][0-9]{14}\b',  # MasterCard
                r'\b3[47][0-9]{13}\b',  # American Express
                r'\b6(?:011|5[0-9]{2})[0-9]{12}\b',  # Discover
            ],
            'ssn': [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN format
                r'\b\d{9}\b',  # SSN without dashes (less reliable)
            ],
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            ],
            'phone': [
                r'\b\+?1?[-.]?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',  # US phone
                r'\b\+?[0-9]{1,3}?[-. ]?\(?([0-9]{2,4})\)?[-. ]?([0-9]{3,4})[-. ]?([0-9]{4,5})\b',  # International
            ],
            'ip_address': [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',  # IPv4
                r'\b(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}\b',  # IPv6
            ],
            'api_key': [
                r'\bapi[_-]?key[_-]?[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'\btoken[_-]?[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
            ],
            'password': [
                r'\bpassword[_-]?[:=]\s*["\']?([^"\']{8,})["\']?',
                r'\bpwd[_-]?[:=]\s*["\']?([^"\']{8,})["\']?',
            ],
        }
        
        # GDPR compliance checks
        self.gdpr_requirements = {
            'cookie_consent': [
                'cookie consent',
                'cookie policy',
                'accept cookies',
                'cookie banner',
                'gdpr'
            ],
            'privacy_policy': [
                'privacy policy',
                'data protection',
                'personal data',
                'data processing'
            ],
            'data_deletion': [
                'delete account',
                'remove data',
                'right to be forgotten',
                'data deletion'
            ],
            'data_export': [
                'download data',
                'export data',
                'data portability',
                'get my data'
            ]
        }
        
        # Sensitive data in logs
        self.log_patterns = [
            r'password[:=]\s*[^,\s]+',
            r'api_key[:=]\s*[^,\s]+',
            r'secret[:=]\s*[^,\s]+',
            r'token[:=]\s*[^,\s]+',
            r'credit_card[:=]\s*[^,\s]+',
        ]
        
        # Data retention indicators
        self.retention_keywords = [
            'retention', 'storage period', 'data retention', 
            'keep data', 'store data', 'delete after'
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for privacy and compliance issues."""
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
            
            content = await response.text()
            
            # Test 1: Check for PII exposure
            pii_findings = await self._check_pii_exposure(url, content)
            findings.extend(pii_findings)
            
            # Test 2: Check GDPR compliance
            gdpr_findings = await self._check_gdpr_compliance(url, content)
            findings.extend(gdpr_findings)
            
            # Test 3: Check for sensitive data in logs
            log_findings = await self._check_sensitive_logs(url, content)
            findings.extend(log_findings)
            
            # Test 4: Check cookie attributes
            cookie_findings = await self._check_cookie_privacy(url, headers)
            findings.extend(cookie_findings)
        
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
    
    async def _check_pii_exposure(self, url: str, content: str) -> List[Finding]:
        """Check for exposed PII in responses."""
        findings = []
        
        for pii_type, patterns in self.pii_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content)
                
                if matches:
                    # Filter out false positives
                    if pii_type == 'email' and len(matches) < 5:
                        continue  # Likely legitimate email addresses
                    
                    severity = FindingSeverity.CRITICAL if pii_type in ['credit_card', 'ssn', 'password'] else FindingSeverity.HIGH
                    
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        title=f"PII Exposure: {pii_type.replace('_', ' ').title()}",
                        description=f"Found {len(matches)} instances of {pii_type} exposed in response",
                        severity=severity,
                        impact=f"Exposure of {pii_type} violates privacy regulations and puts users at risk",
                        likelihood="high",
                        risk_score=9.0 if severity == FindingSeverity.CRITICAL else 8.0,
                        references=[
                            "https://owasp.org/www-community/vulnerabilities/Information_exposure",
                            "https://gdpr-info.eu/",
                            "https://oag.ca.gov/privacy/ccpa"
                        ],
                        raw_data={
                            "pii_type": pii_type,
                            "count": len(matches),
                            "samples": [str(m)[:10] + "..." for m in matches[:3]],  # Redacted samples
                        }
                    )
                    findings.append(finding)
                    break  # Only report once per PII type
        
        return findings
    
    async def _check_gdpr_compliance(self, url: str, content: str) -> List[Finding]:
        """Check for GDPR compliance requirements."""
        findings = []
        
        content_lower = content.lower()
        
        # Check for cookie consent
        if not any(keyword in content_lower for keyword in self.gdpr_requirements['cookie_consent']):
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.COMPLIANCE_VIOLATION,
                title="Missing Cookie Consent Banner (GDPR)",
                description="No cookie consent mechanism detected, required by GDPR",
                severity=FindingSeverity.MEDIUM,
                impact="Missing cookie consent violates GDPR Article 7 and can result in fines",
                likelihood="high",
                risk_score=6.0,
                references=[
                    "https://gdpr-info.eu/art-7-gdpr/",
                    "https://gdpr-info.eu/recitals/no-32/"
                ],
                raw_data={
                    "compliance_issue": "cookie_consent",
                    "regulation": "GDPR"
                }
            )
            findings.append(finding)
        
        # Check for privacy policy
        if not any(keyword in content_lower for keyword in self.gdpr_requirements['privacy_policy']):
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.COMPLIANCE_VIOLATION,
                title="Missing Privacy Policy Link (GDPR)",
                description="No privacy policy link detected, required by GDPR",
                severity=FindingSeverity.MEDIUM,
                impact="Missing privacy policy violates GDPR Article 13 transparency requirements",
                likelihood="high",
                risk_score=6.0,
                references=[
                    "https://gdpr-info.eu/art-13-gdpr/"
                ],
                raw_data={
                    "compliance_issue": "privacy_policy",
                    "regulation": "GDPR"
                }
            )
            findings.append(finding)
        
        # Check for data deletion option
        if 'account' in content_lower or 'profile' in content_lower:
            if not any(keyword in content_lower for keyword in self.gdpr_requirements['data_deletion']):
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.COMPLIANCE_VIOLATION,
                    title="Missing Data Deletion Option (GDPR Right to Erasure)",
                    description="No data deletion/account removal option detected",
                    severity=FindingSeverity.MEDIUM,
                    impact="Missing data deletion violates GDPR Article 17 (Right to Erasure)",
                    likelihood="medium",
                    risk_score=5.5,
                    references=[
                        "https://gdpr-info.eu/art-17-gdpr/"
                    ],
                    raw_data={
                        "compliance_issue": "data_deletion",
                        "regulation": "GDPR"
                    }
                )
                findings.append(finding)
        
        return findings
    
    async def _check_sensitive_logs(self, url: str, content: str) -> List[Finding]:
        """Check for sensitive data in logs/debug output."""
        findings = []
        
        # Check for log-like patterns
        if any(keyword in content.lower() for keyword in ['debug', 'log', 'trace', 'error', 'stack']):
            for pattern in self.log_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        title="Sensitive Data in Logs/Debug Output",
                        description="Sensitive information (passwords, tokens, keys) detected in log/debug output",
                        severity=FindingSeverity.HIGH,
                        impact="Exposed sensitive data in logs can lead to credential compromise",
                        likelihood="medium",
                        risk_score=7.0,
                        references=[
                            "https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure"
                        ],
                        raw_data={
                            "issue_type": "sensitive_logs",
                            "pattern_matched": pattern
                        }
                    )
                    findings.append(finding)
                    break  # Only report once
        
        return findings
    
    async def _check_cookie_privacy(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """Check cookie privacy attributes."""
        findings = []
        
        set_cookie = headers.get('Set-Cookie', '')
        if set_cookie:
            # Check for HttpOnly
            if 'httponly' not in set_cookie.lower():
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.COMPLIANCE_VIOLATION,
                    title="Missing HttpOnly Cookie Flag",
                    description="Cookies set without HttpOnly flag, accessible to JavaScript",
                    severity=FindingSeverity.MEDIUM,
                    impact="Missing HttpOnly flag increases risk of XSS-based cookie theft",
                    likelihood="high",
                    risk_score=6.0,
                    references=[
                        "https://owasp.org/www-community/HttpOnly"
                    ],
                    raw_data={
                        "set_cookie_header": set_cookie[:200]
                    }
                )
                findings.append(finding)
            
            # Check for Secure flag
            if 'secure' not in set_cookie.lower() and url.startswith('https://'):
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.COMPLIANCE_VIOLATION,
                    title="Missing Secure Cookie Flag on HTTPS",
                    description="Cookies set without Secure flag on HTTPS connection",
                    severity=FindingSeverity.MEDIUM,
                    impact="Missing Secure flag allows cookies to be sent over unencrypted connections",
                    likelihood="medium",
                    risk_score=5.5,
                    references=[
                        "https://owasp.org/www-community/controls/SecureCookieAttribute"
                    ],
                    raw_data={
                        "set_cookie_header": set_cookie[:200]
                    }
                )
                findings.append(finding)
        
        return findings


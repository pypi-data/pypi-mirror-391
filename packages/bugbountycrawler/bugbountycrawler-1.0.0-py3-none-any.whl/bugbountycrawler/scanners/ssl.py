"""SSL/TLS scanner for BugBountyCrawler."""

import ssl
import socket
from typing import List, Dict, Any
from urllib.parse import urlparse
import asyncio

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType

class SSLScanner(BaseScanner):
    """Scanner for SSL/TLS issues."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize SSL scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "SSLScanner"
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for SSL/TLS issues."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Make initial request to get headers
            response = await self.make_request(url)
            response_time = response.headers.get("X-Response-Time", 0.0)
            status_code = response.status
            headers = dict(response.headers)
            content_length = int(response.headers.get("Content-Length", 0))
            
            # Check SSL/TLS if HTTPS
            if url.startswith("https://"):
                ssl_findings = await self._check_ssl_certificate(url)
                findings.extend(ssl_findings)
            
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
    
    async def _check_ssl_certificate(self, url: str) -> List[Finding]:
        """Check SSL certificate for issues."""
        findings = []
        
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            port = parsed.port or 443
            
            # Get certificate
            cert = await self._get_certificate(hostname, port)
            if not cert:
                return findings
            
            # Check certificate validity
            validity_findings = self._check_certificate_validity(url, cert)
            findings.extend(validity_findings)
            
            # Check certificate strength
            strength_findings = self._check_certificate_strength(url, cert)
            findings.extend(strength_findings)
            
            # Check certificate chain
            chain_findings = self._check_certificate_chain(url, cert)
            findings.extend(chain_findings)
            
        except Exception as e:
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.SSL_TLS_ISSUES,
                title="SSL Certificate Error",
                description=f"Error checking SSL certificate: {str(e)}",
                severity=FindingSeverity.MEDIUM,
                impact="SSL certificate issues may allow man-in-the-middle attacks",
                likelihood="medium",
                risk_score=6.0,
                raw_data={"error": str(e)}
            )
            findings.append(finding)
        
        return findings
    
    async def _get_certificate(self, hostname: str, port: int) -> Dict[str, Any]:
        """Get SSL certificate information."""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    return {
                        "cert": cert,
                        "cipher": cipher,
                        "version": version,
                        "hostname": hostname
                    }
        except Exception:
            return None
    
    def _check_certificate_validity(self, url: str, cert_info: Dict[str, Any]) -> List[Finding]:
        """Check certificate validity."""
        findings = []
        cert = cert_info["cert"]
        
        # Check if certificate is expired
        import datetime
        not_after = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        if not_after < datetime.datetime.now():
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.SSL_TLS_ISSUES,
                title="Expired SSL Certificate",
                description=f"SSL certificate expired on {cert['notAfter']}",
                severity=FindingSeverity.HIGH,
                impact="Expired certificate allows man-in-the-middle attacks",
                likelihood="high",
                risk_score=8.0,
                references=[
                    "https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"
                ],
                raw_data={
                    "not_after": cert["notAfter"],
                    "issue": "expired_certificate"
                }
            )
            findings.append(finding)
        
        # Check if certificate is self-signed
        issuer = cert.get("issuer", {})
        subject = cert.get("subject", {})
        
        issuer_org = None
        subject_org = None
        
        for item in issuer:
            if item[0][0] == "organizationName":
                issuer_org = item[0][1]
                break
        
        for item in subject:
            if item[0][0] == "organizationName":
                subject_org = item[0][1]
                break
        
        if issuer_org == subject_org and issuer_org:
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.SSL_TLS_ISSUES,
                title="Self-Signed SSL Certificate",
                description="SSL certificate is self-signed",
                severity=FindingSeverity.MEDIUM,
                impact="Self-signed certificate may allow man-in-the-middle attacks",
                likelihood="medium",
                risk_score=6.0,
                references=[
                    "https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"
                ],
                raw_data={
                    "issuer": issuer_org,
                    "subject": subject_org,
                    "issue": "self_signed_certificate"
                }
            )
            findings.append(finding)
        
        return findings
    
    def _check_certificate_strength(self, url: str, cert_info: Dict[str, Any]) -> List[Finding]:
        """Check certificate cryptographic strength."""
        findings = []
        cipher = cert_info["cipher"]
        version = cert_info["version"]
        
        # Check TLS version
        if version in ["TLSv1", "TLSv1.1"]:
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.SSL_TLS_ISSUES,
                title="Weak TLS Version",
                description=f"TLS version {version} is deprecated and vulnerable",
                severity=FindingSeverity.HIGH,
                impact="Weak TLS version allows downgrade attacks",
                likelihood="high",
                risk_score=8.0,
                references=[
                    "https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"
                ],
                raw_data={
                    "tls_version": version,
                    "issue": "weak_tls_version"
                }
            )
            findings.append(finding)
        
        # Check cipher strength
        if cipher:
            cipher_name = cipher[0]
            key_length = cipher[2]
            
            if key_length < 128:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.SSL_TLS_ISSUES,
                    title="Weak Cipher Suite",
                    description=f"Cipher {cipher_name} uses weak key length: {key_length} bits",
                    severity=FindingSeverity.MEDIUM,
                    impact="Weak cipher allows cryptographic attacks",
                    likelihood="medium",
                    risk_score=6.0,
                    references=[
                        "https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"
                    ],
                    raw_data={
                        "cipher": cipher_name,
                        "key_length": key_length,
                        "issue": "weak_cipher"
                    }
                )
                findings.append(finding)
        
        return findings
    
    def _check_certificate_chain(self, url: str, cert_info: Dict[str, Any]) -> List[Finding]:
        """Check certificate chain."""
        findings = []
        
        # This is a simplified check - in practice, you'd want to verify the entire chain
        cert = cert_info["cert"]
        
        # Check if certificate has proper chain
        if "issuer" not in cert or not cert["issuer"]:
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.SSL_TLS_ISSUES,
                title="Incomplete Certificate Chain",
                description="SSL certificate chain is incomplete",
                severity=FindingSeverity.MEDIUM,
                impact="Incomplete certificate chain may cause trust issues",
                likelihood="medium",
                risk_score=5.0,
                references=[
                    "https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"
                ],
                raw_data={
                    "issue": "incomplete_chain"
                }
            )
            findings.append(finding)
        
        return findings

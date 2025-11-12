"""Cloud Metadata Scanner for BugBountyCrawler."""

import asyncio
import aiohttp
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class CloudMetadataScanner(BaseScanner):
    """Scanner for cloud metadata vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize cloud metadata scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "CloudMetadataScanner"
        
        # Cloud metadata endpoints
        self.metadata_endpoints = {
            'aws': [
                'http://169.254.169.254/latest/meta-data/',
                'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
            ],
            'azure': [
                'http://169.254.169.254/metadata/instance?api-version=2017-08-01',
                'http://169.254.169.254/metadata/instance/compute?api-version=2017-08-01',
                'http://169.254.169.254/metadata/instance/network?api-version=2017-08-01',
                'http://169.254.169.254/metadata/instance/security-credentials?api-version=2017-08-01',
            ],
            'gcp': [
                'http://metadata.google.internal/computeMetadata/v1/',
                'http://metadata.google.internal/computeMetadata/v1/instance/',
                'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/',
                'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',
            ],
            'digitalocean': [
                'http://169.254.169.254/metadata/v1/',
                'http://169.254.169.254/metadata/v1/id',
                'http://169.254.169.254/metadata/v1/hostname',
                'http://169.254.169.254/metadata/v1/region',
                'http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address',
            ],
            'linode': [
                'http://169.254.169.254/linode/v1/',
                'http://169.254.169.254/linode/v1/instance',
                'http://169.254.169.254/linode/v1/network',
            ],
            'vultr': [
                'http://169.254.169.254/v1/',
                'http://169.254.169.254/v1/instance',
                'http://169.254.169.254/v1/network',
            ],
        }
        
        # Sensitive metadata patterns
        self.sensitive_patterns = [
            r'access_key_id',
            r'secret_access_key',
            r'session_token',
            r'access_token',
            r'refresh_token',
            r'api_key',
            r'private_key',
            r'public_key',
            r'certificate',
            r'password',
            r'passwd',
            r'pwd',
            r'secret',
            r'credential',
            r'credential',
            r'token',
            r'key',
            r'auth',
            r'authorization',
            r'bearer',
            r'jwt',
            r'oauth',
            r'saml',
            r'ldap',
            r'kerberos',
            r'ntlm',
            r'basic',
            r'digest',
            r'aws_access_key_id',
            r'aws_secret_access_key',
            r'aws_session_token',
            r'azure_client_id',
            r'azure_client_secret',
            r'azure_tenant_id',
            r'azure_subscription_id',
            r'gcp_service_account',
            r'gcp_private_key',
            r'gcp_client_email',
            r'gcp_project_id',
            r'gcp_private_key_id',
            r'gcp_client_id',
            r'gcp_auth_uri',
            r'gcp_token_uri',
            r'gcp_auth_provider_x509_cert_url',
            r'gcp_client_x509_cert_url',
        ]
        
        # Cloud provider indicators
        self.cloud_indicators = {
            'aws': [r'aws', r'amazon', r'ec2', r's3', r'rds', r'lambda', r'cloudformation'],
            'azure': [r'azure', r'microsoft', r'windows', r'active directory', r'office 365'],
            'gcp': [r'google', r'gcp', r'gce', r'gke', r'cloud storage', r'bigquery'],
            'digitalocean': [r'digitalocean', r'droplet', r'spaces', r'kubernetes'],
            'linode': [r'linode', r'akamai', r'nodebalancer', r'object storage'],
            'vultr': [r'vultr', r'cloud compute', r'block storage', r'bare metal'],
        }
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for cloud metadata vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Test for SSRF to metadata endpoints
            ssrf_findings = await self._test_ssrf_to_metadata(url)
            findings.extend(ssrf_findings)
            
            # Test for direct metadata access
            direct_findings = await self._test_direct_metadata_access(url)
            findings.extend(direct_findings)
            
            # Test for metadata leakage in responses
            leakage_findings = await self._test_metadata_leakage(url)
            findings.extend(leakage_findings)
            
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
    
    async def _test_ssrf_to_metadata(self, url: str) -> List[Finding]:
        """Test for SSRF to cloud metadata endpoints."""
        findings = []
        
        # Test each cloud provider's metadata endpoints
        for provider, endpoints in self.metadata_endpoints.items():
            for endpoint in endpoints[:3]:  # Test first 3 endpoints per provider
                try:
                    # Create SSRF payload
                    ssrf_payload = f"{url}?url={endpoint}"
                    
                    response = await self.make_request(ssrf_payload)
                    content = await response.text()
                    
                    # Check if metadata was retrieved
                    if self._is_metadata_retrieved(content, provider):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.CLOUD_METADATA_EXPOSURE,
                            title=f"SSRF to {provider.upper()} Metadata - {endpoint}",
                            description=f"SSRF vulnerability allows access to {provider.upper()} metadata endpoint: {endpoint}",
                            severity=FindingSeverity.CRITICAL,
                            impact=f"SSRF to {provider.upper()} metadata can lead to complete cloud account compromise and credential theft",
                            likelihood="medium",
                            risk_score=9.5,
                            references=[
                                "https://owasp.org/www-community/attacks/Server_Side_Request_Forgery",
                                "https://cwe.mitre.org/data/definitions/918.html"
                            ],
                            raw_data={
                                "provider": provider,
                                "endpoint": endpoint,
                                "ssrf_payload": ssrf_payload,
                                "response_content": content[:500] if len(content) > 500 else content,
                                "vulnerability_type": "ssrf_to_metadata"
                            }
                        )
                        findings.append(finding)
                    
                    # Small delay to avoid overwhelming the server
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    continue  # Skip failed tests
        
        return findings
    
    async def _test_direct_metadata_access(self, url: str) -> List[Finding]:
        """Test for direct access to cloud metadata endpoints."""
        findings = []
        
        # Test each cloud provider's metadata endpoints
        for provider, endpoints in self.metadata_endpoints.items():
            for endpoint in endpoints[:2]:  # Test first 2 endpoints per provider
                try:
                    response = await self.make_request(endpoint)
                    content = await response.text()
                    
                    # Check if metadata is accessible
                    if self._is_metadata_accessible(content, response.status, provider):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.CLOUD_METADATA_EXPOSURE,
                            title=f"Direct Access to {provider.upper()} Metadata - {endpoint}",
                            description=f"Direct access to {provider.upper()} metadata endpoint: {endpoint}",
                            severity=FindingSeverity.CRITICAL,
                            impact=f"Direct access to {provider.upper()} metadata can lead to complete cloud account compromise",
                            likelihood="high",
                            risk_score=9.0,
                            references=[
                                "https://owasp.org/www-community/attacks/Cloud_Metadata_Exposure",
                                "https://cwe.mitre.org/data/definitions/200.html"
                            ],
                            raw_data={
                                "provider": provider,
                                "endpoint": endpoint,
                                "response_status": response.status,
                                "response_content": content[:500] if len(content) > 500 else content,
                                "vulnerability_type": "direct_metadata_access"
                            }
                        )
                        findings.append(finding)
                    
                    # Small delay to avoid overwhelming the server
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    continue  # Skip failed tests
        
        return findings
    
    async def _test_metadata_leakage(self, url: str) -> List[Finding]:
        """Test for metadata leakage in responses."""
        findings = []
        
        try:
            response = await self.make_request(url)
            content = await response.text()
            headers = dict(response.headers)
            
            # Check for metadata leakage in response content
            leaked_metadata = self._find_metadata_leakage(content)
            if leaked_metadata:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.CLOUD_METADATA_EXPOSURE,
                    title="Cloud Metadata Leakage in Response",
                    description=f"Cloud metadata leaked in response: {', '.join(leaked_metadata)}",
                    severity=FindingSeverity.HIGH,
                    impact="Cloud metadata leakage can lead to credential theft and account compromise",
                    likelihood="high",
                    risk_score=8.5,
                    references=[
                        "https://owasp.org/www-community/attacks/Cloud_Metadata_Exposure",
                        "https://cwe.mitre.org/data/definitions/200.html"
                    ],
                    raw_data={
                        "leaked_metadata": leaked_metadata,
                        "response_content": content[:500] if len(content) > 500 else content,
                        "vulnerability_type": "metadata_leakage"
                    }
                )
                findings.append(finding)
            
            # Check for metadata leakage in headers
            leaked_headers = self._find_metadata_in_headers(headers)
            if leaked_headers:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.CLOUD_METADATA_EXPOSURE,
                    title="Cloud Metadata Leakage in Headers",
                    description=f"Cloud metadata leaked in headers: {', '.join(leaked_headers)}",
                    severity=FindingSeverity.MEDIUM,
                    impact="Cloud metadata leakage in headers can provide information for further attacks",
                    likelihood="high",
                    risk_score=7.0,
                    references=[
                        "https://owasp.org/www-community/attacks/Cloud_Metadata_Exposure",
                        "https://cwe.mitre.org/data/definitions/200.html"
                    ],
                    raw_data={
                        "leaked_headers": leaked_headers,
                        "headers": headers,
                        "vulnerability_type": "metadata_header_leakage"
                    }
                )
                findings.append(finding)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    def _is_metadata_retrieved(self, content: str, provider: str) -> bool:
        """Check if metadata was retrieved via SSRF."""
        # Check for provider-specific indicators
        if provider in self.cloud_indicators:
            for indicator in self.cloud_indicators[provider]:
                if re.search(indicator, content, re.IGNORECASE):
                    return True
        
        # Check for sensitive metadata patterns
        for pattern in self.sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _is_metadata_accessible(self, content: str, status_code: int, provider: str) -> bool:
        """Check if metadata is directly accessible."""
        # Check status code
        if status_code != 200:
            return False
        
        # Check for provider-specific indicators
        if provider in self.cloud_indicators:
            for indicator in self.cloud_indicators[provider]:
                if re.search(indicator, content, re.IGNORECASE):
                    return True
        
        # Check for sensitive metadata patterns
        for pattern in self.sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _find_metadata_leakage(self, content: str) -> List[str]:
        """Find metadata leakage in response content."""
        leaked_metadata = []
        
        for pattern in self.sensitive_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            leaked_metadata.extend(matches)
        
        return list(set(leaked_metadata))  # Remove duplicates
    
    def _find_metadata_in_headers(self, headers: Dict[str, str]) -> List[str]:
        """Find metadata leakage in response headers."""
        leaked_headers = []
        
        for header_name, header_value in headers.items():
            for pattern in self.sensitive_patterns:
                if re.search(pattern, header_name, re.IGNORECASE) or re.search(pattern, header_value, re.IGNORECASE):
                    leaked_headers.append(f"{header_name}: {header_value}")
        
        return leaked_headers

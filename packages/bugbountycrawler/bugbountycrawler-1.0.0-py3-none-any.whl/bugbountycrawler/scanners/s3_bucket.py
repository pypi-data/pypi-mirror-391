"""S3 Bucket Scanner for BugBountyCrawler."""

import asyncio
import aiohttp
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import json

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class S3BucketScanner(BaseScanner):
    """Scanner for S3 bucket vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize S3 bucket scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "S3BucketScanner"
        
        # Common S3 bucket naming patterns
        self.bucket_patterns = [
            r'([a-z0-9-]+)\.s3\.amazonaws\.com',
            r's3\.amazonaws\.com/([a-z0-9-]+)',
            r'([a-z0-9-]+)\.s3-website-[a-z0-9-]+\.amazonaws\.com',
            r'([a-z0-9-]+)\.s3-[a-z0-9-]+\.amazonaws\.com',
            r'([a-z0-9-]+)\.s3\.dualstack\.[a-z0-9-]+\.amazonaws\.com',
        ]
        
        # Common bucket names to test
        self.common_bucket_names = [
            'test', 'testing', 'dev', 'development', 'staging', 'prod', 'production',
            'backup', 'backups', 'data', 'files', 'uploads', 'downloads', 'assets',
            'static', 'media', 'images', 'docs', 'documents', 'logs', 'temp', 'tmp',
            'admin', 'config', 'configuration', 'secrets', 'keys', 'credentials',
            'database', 'db', 'mysql', 'postgres', 'redis', 'cache', 'session',
            'user', 'users', 'customer', 'customers', 'client', 'clients',
            'api', 'apis', 'webhook', 'webhooks', 'notification', 'notifications',
            'email', 'emails', 'mail', 'smtp', 'ftp', 'sftp', 'ssh', 'vpn',
            'monitoring', 'metrics', 'analytics', 'stats', 'dashboard', 'panel',
            'control', 'manage', 'management', 'admin-panel', 'cpanel', 'phpmyadmin',
            'jenkins', 'gitlab', 'github', 'bitbucket', 'docker', 'kubernetes',
            'terraform', 'ansible', 'chef', 'puppet', 'vagrant', 'packer',
            'lambda', 'serverless', 'cloudformation', 'cloudfront', 'route53',
            'ec2', 'rds', 'elasticache', 'elasticsearch', 'kibana', 'grafana',
            'prometheus', 'influxdb', 'mongodb', 'cassandra', 'dynamodb',
            's3', 'glacier', 'storage', 'bucket', 'buckets', 'blob', 'blobs',
        ]
        
        # S3 bucket access test URLs
        self.access_test_urls = [
            'https://{bucket}.s3.amazonaws.com/',
            'https://{bucket}.s3.amazonaws.com/?list-type=2',
            'https://{bucket}.s3.amazonaws.com/?list-type=1',
            'https://{bucket}.s3-website-us-east-1.amazonaws.com/',
            'https://{bucket}.s3-website-us-west-2.amazonaws.com/',
            'https://{bucket}.s3-website-eu-west-1.amazonaws.com/',
            'https://{bucket}.s3-website-ap-southeast-1.amazonaws.com/',
        ]
        
        # Indicators of public bucket access
        self.public_access_indicators = [
            r'<ListBucketResult',
            r'<ListAllMyBucketsResult',
            r'<Contents>',
            r'<Key>',
            r'<Size>',
            r'<LastModified>',
            r'<StorageClass>',
            r'<Owner>',
            r'<ID>',
            r'<DisplayName>',
            r'<Name>',
            r'<CreationDate>',
            r'<Prefix>',
            r'<MaxKeys>',
            r'<IsTruncated>',
            r'<NextContinuationToken>',
            r'<CommonPrefixes>',
            r'<Delimiter>',
            r'<Marker>',
            r'<NextMarker>',
            r'<MaxKeys>',
            r'<IsTruncated>',
        ]
        
        # Sensitive file patterns
        self.sensitive_file_patterns = [
            r'\.env', r'\.git', r'\.svn', r'\.hg', r'\.bzr',
            r'config\.json', r'config\.yaml', r'config\.yml',
            r'secrets\.json', r'secrets\.yaml', r'secrets\.yml',
            r'credentials\.json', r'credentials\.yaml', r'credentials\.yml',
            r'\.pem', r'\.key', r'\.p12', r'\.pfx', r'\.jks',
            r'\.sql', r'\.dump', r'\.backup', r'\.bak',
            r'\.log', r'\.logs', r'\.txt', r'\.csv', r'\.xlsx',
            r'\.zip', r'\.tar', r'\.gz', r'\.rar', r'\.7z',
            r'password', r'passwd', r'pwd', r'secret', r'private',
            r'admin', r'root', r'user', r'login', r'auth',
            r'database', r'db', r'mysql', r'postgres', r'mongo',
            r'api', r'token', r'key', r'credential', r'access',
        ]
        
        # Bucket takeover indicators
        self.takeover_indicators = [
            r'NoSuchBucket',
            r'InvalidBucketName',
            r'BucketNotFound',
            r'NoSuchWebsiteConfiguration',
            r'AccessDenied',
            r'AllAccessDisabled',
            r'InvalidRequest',
            r'InvalidBucketState',
            r'BucketAlreadyExists',
            r'BucketAlreadyOwnedByYou',
            r'BucketNotEmpty',
            r'BucketNotOwnedByYou',
            r'BucketNotOwnedByYou',
            r'BucketNotOwnedByYou',
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for S3 bucket vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Extract potential bucket names from URL
            bucket_names = self._extract_bucket_names(url)
            
            if not bucket_names:
                # Try to find bucket names in the domain
                domain = urlparse(url).netloc
                bucket_names = self._extract_bucket_names_from_domain(domain)
            
            # Test each potential bucket
            for bucket_name in bucket_names:
                bucket_findings = await self._test_s3_bucket(bucket_name)
                findings.extend(bucket_findings)
            
            # Test common bucket names
            common_findings = await self._test_common_buckets(url)
            findings.extend(common_findings)
            
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
    
    async def _test_s3_bucket(self, bucket_name: str) -> List[Finding]:
        """Test a specific S3 bucket for vulnerabilities."""
        findings = []
        
        # Test different S3 access methods
        for test_url_template in self.access_test_urls:
            try:
                test_url = test_url_template.format(bucket=bucket_name)
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check for public access
                if self._is_public_bucket(content, response.status):
                    finding = self.create_finding(
                        url=test_url,
                        finding_type=FindingType.S3_BUCKET_MISCONFIGURATION,
                        title=f"Public S3 Bucket - {bucket_name}",
                        description=f"S3 bucket '{bucket_name}' is publicly accessible and may contain sensitive data",
                        severity=FindingSeverity.HIGH,
                        impact="Public S3 buckets can lead to data exposure, credential theft, and unauthorized access to sensitive information",
                        likelihood="high",
                        risk_score=8.5,
                        references=[
                            "https://owasp.org/www-community/attacks/S3_Bucket_Misconfiguration",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "bucket_name": bucket_name,
                            "test_url": test_url,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "public_bucket"
                        }
                    )
                    findings.append(finding)
                
                # Check for sensitive files
                sensitive_files = self._find_sensitive_files(content)
                if sensitive_files:
                    finding = self.create_finding(
                        url=test_url,
                        finding_type=FindingType.S3_BUCKET_MISCONFIGURATION,
                        title=f"Sensitive Files in S3 Bucket - {bucket_name}",
                        description=f"S3 bucket '{bucket_name}' contains sensitive files: {', '.join(sensitive_files)}",
                        severity=FindingSeverity.CRITICAL,
                        impact="Sensitive files in public S3 buckets can lead to complete system compromise and data breach",
                        likelihood="high",
                        risk_score=9.5,
                        references=[
                            "https://owasp.org/www-community/attacks/S3_Bucket_Misconfiguration",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "bucket_name": bucket_name,
                            "test_url": test_url,
                            "sensitive_files": sensitive_files,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "sensitive_files"
                        }
                    )
                    findings.append(finding)
                
                # Check for bucket takeover
                if self._is_bucket_takeover_possible(content, response.status):
                    finding = self.create_finding(
                        url=test_url,
                        finding_type=FindingType.S3_BUCKET_MISCONFIGURATION,
                        title=f"S3 Bucket Takeover Possible - {bucket_name}",
                        description=f"S3 bucket '{bucket_name}' may be vulnerable to takeover",
                        severity=FindingSeverity.HIGH,
                        impact="S3 bucket takeover can lead to complete control of the bucket and potential credential theft",
                        likelihood="medium",
                        risk_score=8.0,
                        references=[
                            "https://owasp.org/www-community/attacks/S3_Bucket_Takeover",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "bucket_name": bucket_name,
                            "test_url": test_url,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "bucket_takeover"
                        }
                    )
                    findings.append(finding)
                
                # Small delay to avoid overwhelming AWS
                await asyncio.sleep(0.2)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_common_buckets(self, url: str) -> List[Finding]:
        """Test common bucket names for the domain."""
        findings = []
        
        # Extract domain from URL
        domain = urlparse(url).netloc
        base_domain = self._extract_base_domain(domain)
        
        if not base_domain:
            return findings
        
        # Test common bucket names with the domain
        for bucket_name in self.common_bucket_names[:10]:  # Test first 10
            try:
                # Test different bucket naming conventions
                test_buckets = [
                    f"{bucket_name}-{base_domain}",
                    f"{base_domain}-{bucket_name}",
                    f"{bucket_name}.{base_domain}",
                    f"{base_domain}.{bucket_name}",
                    f"{bucket_name}{base_domain}",
                    f"{base_domain}{bucket_name}",
                ]
                
                for test_bucket in test_buckets:
                    bucket_findings = await self._test_s3_bucket(test_bucket)
                    findings.extend(bucket_findings)
                    
                    # Small delay to avoid overwhelming AWS
                    await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    def _extract_bucket_names(self, url: str) -> List[str]:
        """Extract potential bucket names from URL."""
        bucket_names = []
        
        for pattern in self.bucket_patterns:
            matches = re.findall(pattern, url, re.IGNORECASE)
            bucket_names.extend(matches)
        
        return list(set(bucket_names))  # Remove duplicates
    
    def _extract_bucket_names_from_domain(self, domain: str) -> List[str]:
        """Extract potential bucket names from domain."""
        bucket_names = []
        
        # Check if domain contains bucket-like patterns
        if 's3' in domain.lower():
            # Extract the part before s3
            parts = domain.split('.')
            for i, part in enumerate(parts):
                if 's3' in part.lower() and i > 0:
                    bucket_names.append(parts[i-1])
        
        return bucket_names
    
    def _extract_base_domain(self, domain: str) -> str:
        """Extract base domain from full domain."""
        # Remove common TLDs and subdomains
        parts = domain.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return domain
    
    def _is_public_bucket(self, content: str, status_code: int) -> bool:
        """Check if bucket is publicly accessible."""
        # Check for S3 XML response indicators
        for indicator in self.public_access_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _find_sensitive_files(self, content: str) -> List[str]:
        """Find sensitive files in bucket listing."""
        sensitive_files = []
        
        for pattern in self.sensitive_file_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            sensitive_files.extend(matches)
        
        return list(set(sensitive_files))  # Remove duplicates
    
    def _is_bucket_takeover_possible(self, content: str, status_code: int) -> bool:
        """Check if bucket takeover is possible."""
        # Check for takeover indicators
        for indicator in self.takeover_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check for specific error patterns
        if status_code == 404 and 'NoSuchBucket' in content:
            return True
        
        return False

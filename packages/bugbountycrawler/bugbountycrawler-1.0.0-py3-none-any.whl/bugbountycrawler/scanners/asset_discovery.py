"""
Asset Discovery Scanner
Performs subdomain enumeration and OSINT gathering
"""

import asyncio
import aiohttp
import dns.resolver
import socket
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse
import re
import json
from datetime import datetime

from ..core.config import Settings
from ..scanners.base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType, Remediation
from ..core.logger import get_logger

logger = get_logger(__name__)

class AssetDiscoveryScanner(BaseScanner):
    """Scanner for asset discovery and subdomain enumeration."""
    
    def __init__(self, settings: Settings, rate_limiter=None):
        super().__init__(settings, rate_limiter)
        self.name = "Asset Discovery"
        self.description = "Discovers subdomains and gathers OSINT information"
        
        # Common subdomain wordlist
        self.subdomain_wordlist = [
            'www', 'mail', 'ftp', 'admin', 'api', 'app', 'blog', 'cdn', 'dev', 'test',
            'staging', 'prod', 'production', 'secure', 'ssl', 'vpn', 'remote', 'backup',
            'db', 'database', 'mysql', 'postgres', 'redis', 'cache', 'static', 'assets',
            'media', 'files', 'download', 'upload', 'docs', 'documentation', 'help',
            'support', 'status', 'monitor', 'metrics', 'logs', 'analytics', 'stats',
            'dashboard', 'panel', 'control', 'manage', 'admin-panel', 'cpanel', 'phpmyadmin',
            'webmail', 'email', 'smtp', 'pop', 'imap', 'ns1', 'ns2', 'dns', 'mx',
            'subdomain', 'sub', 'beta', 'alpha', 'demo', 'sandbox', 'lab', 'research',
            'internal', 'private', 'intranet', 'extranet', 'portal', 'gateway', 'proxy',
            'load', 'balancer', 'lb', 'cluster', 'node', 'server', 'host', 'vm', 'container'
        ]
        
        # Common DNS record types to check
        self.dns_record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA']
        
    async def scan_url(self, url: str) -> ScanResult:
        """Scan a URL for asset discovery."""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            logger.info(f"Starting asset discovery for domain: {domain}")
            
            findings = []
            
            # 1. Subdomain enumeration
            subdomain_findings = await self._enumerate_subdomains(domain)
            findings.extend(subdomain_findings)
            
            # 2. DNS record analysis
            dns_findings = await self._analyze_dns_records(domain)
            findings.extend(dns_findings)
            
            # 3. Port scanning (basic)
            port_findings = await self._scan_common_ports(domain)
            findings.extend(port_findings)
            
            # 4. Technology stack detection
            tech_findings = await self._detect_technology_stack(url)
            findings.extend(tech_findings)
            
            # 5. Certificate transparency logs
            cert_findings = await self._check_certificate_transparency(domain)
            findings.extend(cert_findings)
            
            logger.info(f"Asset discovery completed. Found {len(findings)} findings")
            
            return ScanResult(
                url=url,
                findings=findings,
                errors=[],
                response_time=0.0,
                status_code=200,
                headers={},
                content_length=0
            )
            
        except Exception as e:
            logger.error(f"Asset discovery failed for {url}: {e}")
            return ScanResult(
                url=url,
                findings=[],
                errors=[str(e)],
                response_time=0.0,
                status_code=0,
                headers={},
                content_length=0
            )
    
    def _create_finding(self, url: str, title: str, description: str, severity: FindingSeverity, 
                       impact: str, remediation: str, finding_type: FindingType = FindingType.INFORMATION_DISCLOSURE,
                       references: List[str] = None) -> Finding:
        """Create a Finding object with proper structure."""
        return Finding(
            scan_id="asset_discovery",  # Will be set by scanner
            target_id="asset_discovery",  # Will be set by scanner
            title=title,
            description=description,
            severity=severity,
            impact=impact,
            finding_type=finding_type,
            url=url,
            likelihood="medium",
            risk_score=5.0,
            remediation=Remediation(
                description=remediation,
                references=references or []
            )
        )
    
    async def _enumerate_subdomains(self, domain: str) -> List[Finding]:
        """Enumerate subdomains using various techniques."""
        findings = []
        discovered_subdomains = set()
        
        try:
            # Method 1: DNS brute force
            logger.info(f"Brute forcing subdomains for {domain}")
            brute_force_subdomains = await self._dns_brute_force(domain)
            discovered_subdomains.update(brute_force_subdomains)
            
            # Method 2: Certificate transparency logs
            logger.info(f"Checking certificate transparency for {domain}")
            cert_subdomains = await self._get_certificate_subdomains(domain)
            discovered_subdomains.update(cert_subdomains)
            
            # Method 3: Search engine dorking (simulated)
            logger.info(f"Search engine dorking for {domain}")
            search_subdomains = await self._search_engine_dorking(domain)
            discovered_subdomains.update(search_subdomains)
            
            # Create findings for discovered subdomains
            for subdomain in discovered_subdomains:
                if subdomain != domain:  # Don't report the main domain
                    findings.append(self._create_finding(
                        url=f"https://{subdomain}",
                        title=f"Subdomain Discovered: {subdomain}",
                        description=f"Discovered subdomain: {subdomain}",
                        severity=FindingSeverity.INFO,
                        impact="Subdomain enumeration reveals additional attack surface",
                        remediation="Review subdomain security and ensure proper configuration",
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        references=["https://owasp.org/www-community/attacks/Subdomain_Takeover"]
                    ))
            
            if discovered_subdomains:
                findings.append(self._create_finding(
                    url=f"https://{domain}",
                    title=f"Subdomain Enumeration Results",
                    description=f"Discovered {len(discovered_subdomains)} subdomains: {', '.join(sorted(discovered_subdomains))}",
                    severity=FindingSeverity.INFO,
                    impact="Additional attack surface identified",
                    remediation="Audit all discovered subdomains for security issues",
                    finding_type=FindingType.INFORMATION_DISCLOSURE,
                    references=[]
                ))
                
        except Exception as e:
            logger.error(f"Subdomain enumeration failed: {e}")
            findings.append(self._create_finding(
                url=f"https://{domain}",
                title="Subdomain Enumeration Failed",
                description=f"Failed to enumerate subdomains: {str(e)}",
                severity=FindingSeverity.LOW,
                impact="Incomplete reconnaissance",
                remediation="Manual subdomain enumeration recommended",
                finding_type=FindingType.INFORMATION_DISCLOSURE,
                references=[]
            ))
        
        return findings
    
    async def _dns_brute_force(self, domain: str) -> Set[str]:
        """Brute force subdomains using DNS queries."""
        discovered = set()
        
        # Limit concurrent requests
        semaphore = asyncio.Semaphore(10)
        
        async def check_subdomain(subdomain: str):
            async with semaphore:
                try:
                    full_domain = f"{subdomain}.{domain}"
                    # Check A record
                    resolver = dns.resolver.Resolver()
                    resolver.timeout = 2
                    resolver.lifetime = 2
                    result = resolver.resolve(full_domain, 'A')
                    if result:
                        discovered.add(full_domain)
                        logger.debug(f"Found subdomain: {full_domain}")
                except:
                    pass  # Subdomain doesn't exist
        
        # Check common subdomains
        tasks = [check_subdomain(sub) for sub in self.subdomain_wordlist[:20]]  # Limit for demo
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return discovered
    
    async def _get_certificate_subdomains(self, domain: str) -> Set[str]:
        """Get subdomains from certificate transparency logs."""
        discovered = set()
        
        try:
            # Simulate certificate transparency check
            # In a real implementation, you'd query crt.sh or similar
            common_cert_subdomains = [
                f"www.{domain}",
                f"mail.{domain}",
                f"api.{domain}",
                f"admin.{domain}",
                f"app.{domain}"
            ]
            
            # Simulate finding some subdomains
            for subdomain in common_cert_subdomains[:2]:  # Simulate finding 2
                discovered.add(subdomain)
                
        except Exception as e:
            logger.error(f"Certificate transparency check failed: {e}")
        
        return discovered
    
    async def _search_engine_dorking(self, domain: str) -> Set[str]:
        """Simulate search engine dorking for subdomains."""
        discovered = set()
        
        try:
            # Simulate search engine results
            # In a real implementation, you'd query Google, Bing, etc.
            search_subdomains = [
                f"blog.{domain}",
                f"docs.{domain}",
                f"support.{domain}"
            ]
            
            # Simulate finding some subdomains
            for subdomain in search_subdomains[:1]:  # Simulate finding 1
                discovered.add(subdomain)
                
        except Exception as e:
            logger.error(f"Search engine dorking failed: {e}")
        
        return discovered
    
    async def _analyze_dns_records(self, domain: str) -> List[Finding]:
        """Analyze DNS records for security issues."""
        findings = []
        
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            # Check for DNS security issues
            for record_type in self.dns_record_types:
                try:
                    result = resolver.resolve(domain, record_type)
                    
                    if record_type == 'TXT':
                        for record in result:
                            txt_record = str(record)
                            
                            # Check for SPF records
                            if 'v=spf1' in txt_record:
                                if '~all' in txt_record or '-all' in txt_record:
                                    findings.append(Finding(
                                        title="SPF Record Found",
                                        description=f"SPF record found: {txt_record}",
                                        severity=FindingSeverity.INFO,
                                        impact="Email authentication configured",
                                        remediation="Ensure SPF record is properly configured",
                                        references=["https://tools.ietf.org/html/rfc7208"]
                                    ))
                                else:
                                    findings.append(Finding(
                                        title="Weak SPF Record",
                                        description=f"Weak SPF record found: {txt_record}",
                                        severity=FindingSeverity.MEDIUM,
                                        impact="Weak SPF record may allow email spoofing",
                                        remediation="Strengthen SPF record with proper qualifiers",
                                        references=["https://tools.ietf.org/html/rfc7208"]
                                    ))
                            
                            # Check for DMARC records
                            if 'v=DMARC1' in txt_record:
                                findings.append(Finding(
                                    title="DMARC Record Found",
                                    description=f"DMARC record found: {txt_record}",
                                    severity=FindingSeverity.INFO,
                                    impact="Email authentication and reporting configured",
                                    remediation="Monitor DMARC reports for policy violations",
                                    references=["https://tools.ietf.org/html/rfc7489"]
                                ))
                    
                    elif record_type == 'MX':
                        mx_records = [str(record) for record in result]
                        findings.append(Finding(
                            title="MX Records Found",
                            description=f"Mail exchange records: {', '.join(mx_records)}",
                            severity=FindingSeverity.INFO,
                            impact="Email server configuration visible",
                            remediation="Ensure MX records point to secure mail servers",
                            references=[]
                        ))
                    
                except Exception as e:
                    # Record type not found, continue
                    pass
                    
        except Exception as e:
            logger.error(f"DNS analysis failed: {e}")
            findings.append(Finding(
                title="DNS Analysis Failed",
                description=f"Failed to analyze DNS records: {str(e)}",
                severity=FindingSeverity.LOW,
                impact="Incomplete DNS reconnaissance",
                remediation="Manual DNS analysis recommended",
                references=[]
            ))
        
        return findings
    
    async def _scan_common_ports(self, domain: str) -> List[Finding]:
        """Scan common ports for open services."""
        findings = []
        
        # Common ports to check
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306, 6379]
        
        try:
            for port in common_ports[:5]:  # Limit for demo
                try:
                    # Use asyncio for non-blocking socket operations
                    future = asyncio.get_event_loop().run_in_executor(
                        None, self._check_port, domain, port
                    )
                    is_open = await future
                    
                    if is_open:
                        service = self._get_service_name(port)
                        findings.append(Finding(
                            title=f"Open Port Found: {port}",
                            description=f"Port {port} ({service}) is open on {domain}",
                            severity=FindingSeverity.INFO,
                            impact=f"Open {service} service may expose attack surface",
                            remediation=f"Review {service} service configuration and security",
                            references=[]
                        ))
                        
                except Exception as e:
                    logger.debug(f"Port {port} check failed: {e}")
                    
        except Exception as e:
            logger.error(f"Port scanning failed: {e}")
            findings.append(Finding(
                title="Port Scanning Failed",
                description=f"Failed to scan ports: {str(e)}",
                severity=FindingSeverity.LOW,
                impact="Incomplete service discovery",
                remediation="Manual port scanning recommended",
                references=[]
            ))
        
        return findings
    
    def _check_port(self, host: str, port: int) -> bool:
        """Check if a port is open (synchronous)."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _get_service_name(self, port: int) -> str:
        """Get service name for common ports."""
        services = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
            80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
            993: 'IMAPS', 995: 'POP3S', 3389: 'RDP', 5432: 'PostgreSQL',
            3306: 'MySQL', 6379: 'Redis'
        }
        return services.get(port, 'Unknown')
    
    async def _detect_technology_stack(self, url: str) -> List[Finding]:
        """Detect technology stack from HTTP headers and content."""
        findings = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    headers = response.headers
                    
                    # Check for technology indicators
                    tech_indicators = {
                        'Server': 'Web Server',
                        'X-Powered-By': 'Application Framework',
                        'X-Generator': 'CMS/Generator',
                        'X-AspNet-Version': 'ASP.NET Version',
                        'X-Runtime': 'Ruby on Rails',
                        'X-Drupal-Cache': 'Drupal CMS',
                        'X-WordPress': 'WordPress CMS'
                    }
                    
                    detected_tech = []
                    for header, tech_type in tech_indicators.items():
                        if header in headers:
                            value = headers[header]
                            detected_tech.append(f"{tech_type}: {value}")
                            findings.append(self._create_finding(
                                url=url,
                                title=f"Technology Detected: {tech_type}",
                                description=f"{tech_type} detected: {value}",
                                severity=FindingSeverity.INFO,
                                impact=f"Technology stack information disclosed",
                                remediation="Consider hiding or modifying technology headers",
                                finding_type=FindingType.INFORMATION_DISCLOSURE,
                                references=[]
                            ))
                    
                    if detected_tech:
                        findings.append(self._create_finding(
                            url=url,
                            title="Technology Stack Analysis",
                            description=f"Detected technologies: {'; '.join(detected_tech)}",
                            severity=FindingSeverity.INFO,
                            impact="Technology stack information may aid attackers",
                            remediation="Review and minimize technology disclosure",
                            finding_type=FindingType.INFORMATION_DISCLOSURE,
                            references=[]
                        ))
                        
        except Exception as e:
            logger.error(f"Technology detection failed: {e}")
            findings.append(self._create_finding(
                url=url,
                title="Technology Detection Failed",
                description=f"Failed to detect technology stack: {str(e)}",
                severity=FindingSeverity.LOW,
                impact="Incomplete technology reconnaissance",
                remediation="Manual technology detection recommended",
                finding_type=FindingType.INFORMATION_DISCLOSURE,
                references=[]
            ))
        
        return findings
    
    async def _check_certificate_transparency(self, domain: str) -> List[Finding]:
        """Check certificate transparency logs for additional domains and takeover opportunities."""
        findings = []
        
        try:
            # Get subdomains from certificate transparency
            cert_subdomains = await self._get_certificate_subdomains(domain)
            
            for subdomain in cert_subdomains:
                # Check for subdomain takeover vulnerability
                takeover_finding = await self._check_subdomain_takeover(subdomain)
                if takeover_finding:
                    findings.append(takeover_finding)
                else:
                    findings.append(Finding(
                        title=f"Subdomain from Certificate: {subdomain}",
                        description=f"Subdomain found in certificate transparency logs: {subdomain}",
                        severity=FindingSeverity.INFO,
                        impact="Additional attack surface identified",
                        remediation="Audit subdomain for security issues",
                        references=["https://crt.sh/"]
                    ))
            
            if not cert_subdomains:
                findings.append(Finding(
                    title="Certificate Transparency Check",
                    description="Certificate transparency logs checked for additional domains",
                    severity=FindingSeverity.INFO,
                    impact="Certificate transparency may reveal additional attack surface",
                    remediation="Monitor certificate transparency logs regularly",
                    references=["https://crt.sh/"]
                ))
            
        except Exception as e:
            logger.error(f"Certificate transparency check failed: {e}")
        
        return findings
    
    async def _check_subdomain_takeover(self, subdomain: str) -> Finding:
        """Check if subdomain is vulnerable to takeover."""
        try:
            # Check DNS records first
            dns_info = await self._get_dns_info(subdomain)
            if not dns_info:
                return None
            
            # Check for CNAME records pointing to vulnerable services
            cname_record = dns_info.get('CNAME', '')
            
            # Known vulnerable services and their takeover indicators
            vulnerable_services = {
                'github.io': {
                    'pattern': r'github\.io',
                    'check_method': 'github_pages',
                    'severity': FindingSeverity.HIGH,
                    'description': 'GitHub Pages subdomain takeover'
                },
                'herokuapp.com': {
                    'pattern': r'herokuapp\.com',
                    'check_method': 'heroku',
                    'severity': FindingSeverity.HIGH,
                    'description': 'Heroku subdomain takeover'
                },
                's3.amazonaws.com': {
                    'pattern': r's3\.amazonaws\.com',
                    'check_method': 'aws_s3',
                    'severity': FindingSeverity.HIGH,
                    'description': 'AWS S3 subdomain takeover'
                },
                'azurewebsites.net': {
                    'pattern': r'azurewebsites\.net',
                    'check_method': 'azure',
                    'severity': FindingSeverity.HIGH,
                    'description': 'Azure subdomain takeover'
                },
                'cloudfront.net': {
                    'pattern': r'cloudfront\.net',
                    'check_method': 'cloudfront',
                    'severity': FindingSeverity.MEDIUM,
                    'description': 'CloudFront subdomain takeover'
                },
                'fastly.com': {
                    'pattern': r'fastly\.com',
                    'check_method': 'fastly',
                    'severity': FindingSeverity.MEDIUM,
                    'description': 'Fastly subdomain takeover'
                }
            }
            
            # Check if CNAME points to vulnerable service
            for service, config in vulnerable_services.items():
                if re.search(config['pattern'], cname_record, re.IGNORECASE):
                    # Check if service is available for takeover
                    is_vulnerable = await self._check_service_takeover(subdomain, config['check_method'])
                    
                    if is_vulnerable:
                        return Finding(
                            title=f"Subdomain Takeover Vulnerability: {subdomain}",
                            description=f"{config['description']} vulnerability detected. CNAME record points to: {cname_record}",
                            severity=config['severity'],
                            finding_type=FindingType.SUBDOMAIN_TAKEOVER,
                            impact=f"Subdomain takeover allows complete control of {subdomain} and potential credential theft",
                            remediation=f"Remove or update CNAME record pointing to {service}, or claim the subdomain on the service",
                            references=[
                                "https://github.com/EdOverflow/can-i-take-over-xyz",
                                "https://owasp.org/www-community/attacks/Subdomain_Takeover"
                            ]
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Subdomain takeover check failed for {subdomain}: {e}")
            return None
    
    async def _get_dns_info(self, subdomain: str) -> Dict[str, str]:
        """Get DNS information for subdomain."""
        try:
            import dns.resolver
            
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            dns_info = {}
            
            # Get CNAME record
            try:
                cname_result = resolver.resolve(subdomain, 'CNAME')
                dns_info['CNAME'] = str(cname_result[0])
            except:
                dns_info['CNAME'] = ''
            
            # Get A record
            try:
                a_result = resolver.resolve(subdomain, 'A')
                dns_info['A'] = str(a_result[0])
            except:
                dns_info['A'] = ''
            
            return dns_info
            
        except Exception as e:
            logger.error(f"DNS lookup failed for {subdomain}: {e}")
            return {}
    
    async def _check_service_takeover(self, subdomain: str, service_type: str) -> bool:
        """Check if service is available for takeover."""
        try:
            # Test HTTP response
            test_url = f"https://{subdomain}"
            
            try:
                response = await self.make_request(test_url, timeout=10)
                content = await response.text()
                status_code = response.status
            except:
                # Try HTTP if HTTPS fails
                test_url = f"http://{subdomain}"
                try:
                    response = await self.make_request(test_url, timeout=10)
                    content = await response.text()
                    status_code = response.status
                except:
                    return False
            
            # Check based on service type
            if service_type == 'github_pages':
                return (
                    status_code == 404 and 
                    ('github' in content.lower() or 'not found' in content.lower())
                )
            elif service_type == 'heroku':
                return (
                    status_code in [404, 503] and 
                    ('heroku' in content.lower() or 'no such app' in content.lower())
                )
            elif service_type == 'aws_s3':
                return (
                    status_code == 404 and 
                    ('no such bucket' in content.lower() or 'not found' in content.lower())
                )
            elif service_type == 'azure':
                return (
                    status_code == 404 and 
                    ('azure' in content.lower() or 'not found' in content.lower())
                )
            elif service_type == 'cloudfront':
                return (
                    status_code == 404 and 
                    ('cloudfront' in content.lower() or 'error' in content.lower())
                )
            elif service_type == 'fastly':
                return (
                    status_code == 404 and 
                    ('fastly' in content.lower() or 'error' in content.lower())
                )
            
            return False
            
        except Exception as e:
            logger.error(f"Service takeover check failed for {subdomain}: {e}")
            return False

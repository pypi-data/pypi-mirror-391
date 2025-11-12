"""DNS Scanner for BugBountyCrawler."""

import asyncio
import aiohttp
import dns.resolver
import dns.zone
import dns.query
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class DNSScanner(BaseScanner):
    """Scanner for DNS vulnerabilities and misconfigurations."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize DNS scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "DNSScanner"
        
        # DNS record types to check
        self.dns_record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA', 'PTR', 'SRV', 'CAA']
        
        # DNS security patterns
        self.security_patterns = {
            'spf': r'v=spf1',
            'dmarc': r'v=DMARC1',
            'dkim': r'v=DKIM1',
            'dane': r'v=TLSRPTv1',
            'mta-sts': r'v=STSv1',
            'dnssec': r'RRSIG',
            'caa': r'issue',
            'cname': r'CNAME',
            'mx': r'MX',
            'ns': r'NS',
            'txt': r'TXT',
            'soa': r'SOA',
            'ptr': r'PTR',
            'srv': r'SRV',
        }
        
        # DNS vulnerability patterns
        self.vulnerability_patterns = [
            r'zone.*transfer',
            r'axfr',
            r'ixfr',
            r'zone.*dump',
            r'dns.*dump',
            r'zone.*file',
            r'dns.*file',
            r'zone.*data',
            r'dns.*data',
            r'zone.*info',
            r'dns.*info',
            r'zone.*list',
            r'dns.*list',
            r'zone.*enum',
            r'dns.*enum',
            r'zone.*scan',
            r'dns.*scan',
            r'zone.*probe',
            r'dns.*probe',
            r'zone.*test',
            r'dns.*test',
            r'zone.*check',
            r'dns.*check',
            r'zone.*audit',
            r'dns.*audit',
            r'zone.*review',
            r'dns.*review',
            r'zone.*analysis',
            r'dns.*analysis',
            r'zone.*assessment',
            r'dns.*assessment',
            r'zone.*evaluation',
            r'dns.*evaluation',
            r'zone.*inspection',
            r'dns.*inspection',
            r'zone.*examination',
            r'dns.*examination',
            r'zone.*investigation',
            r'dns.*investigation',
            r'zone.*exploration',
            r'dns.*exploration',
            r'zone.*discovery',
            r'dns.*discovery',
            r'zone.*reconnaissance',
            r'dns.*reconnaissance',
            r'zone.*intelligence',
            r'dns.*intelligence',
            r'zone.*gathering',
            r'dns.*gathering',
            r'zone.*collection',
            r'dns.*collection',
            r'zone.*harvesting',
            r'dns.*harvesting',
            r'zone.*extraction',
            r'dns.*extraction',
            r'zone.*mining',
            r'dns.*mining',
            r'zone.*digging',
            r'dns.*digging',
            r'zone.*excavation',
            r'dns.*excavation',
            r'zone.*excavation',
            r'dns.*excavation',
        ]
        
        # Common DNS servers
        self.dns_servers = [
            '8.8.8.8',      # Google DNS
            '8.8.4.4',      # Google DNS
            '1.1.1.1',      # Cloudflare DNS
            '1.0.0.1',      # Cloudflare DNS
            '208.67.222.222', # OpenDNS
            '208.67.220.220', # OpenDNS
            '9.9.9.9',      # Quad9
            '149.112.112.112', # Quad9
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for DNS vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Extract domain from URL
            parsed_url = urlparse(url)
            domain = parsed_url.hostname
            
            if not domain:
                return ScanResult(
                    url=url,
                    findings=findings,
                    errors=errors,
                    response_time=response_time,
                    status_code=status_code,
                    headers=headers,
                    content_length=content_length
                )
            
            # Test for DNS zone transfer
            zone_findings = await self._test_zone_transfer(domain)
            findings.extend(zone_findings)
            
            # Test for DNS misconfigurations
            misconfig_findings = await self._test_dns_misconfigurations(domain)
            findings.extend(misconfig_findings)
            
            # Test for DNS security records
            security_findings = await self._test_dns_security_records(domain)
            findings.extend(security_findings)
            
            # Test for DNS vulnerabilities
            vuln_findings = await self._test_dns_vulnerabilities(domain)
            findings.extend(vuln_findings)
            
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
    
    async def _test_zone_transfer(self, domain: str) -> List[Finding]:
        """Test for DNS zone transfer vulnerabilities."""
        findings = []
        
        try:
            # Get authoritative nameservers
            ns_records = dns.resolver.resolve(domain, 'NS')
            nameservers = [str(ns) for ns in ns_records]
            
            # Test zone transfer on each nameserver
            for nameserver in nameservers[:3]:  # Test first 3 nameservers
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(nameserver, domain))
                    
                    if zone:
                        finding = self.create_finding(
                            url=domain,
                            finding_type=FindingType.INFORMATION_DISCLOSURE,
                            title=f"DNS Zone Transfer Vulnerability - {nameserver}",
                            description=f"DNS zone transfer is allowed on nameserver {nameserver} for domain {domain}",
                            severity=FindingSeverity.HIGH,
                            impact="DNS zone transfer can lead to complete domain information disclosure and reconnaissance",
                            likelihood="high",
                            risk_score=8.0,
                            references=[
                                "https://owasp.org/www-community/attacks/DNS_Zone_Transfer",
                                "https://cwe.mitre.org/data/definitions/200.html"
                            ],
                            raw_data={
                                "domain": domain,
                                "nameserver": nameserver,
                                "zone_records": len(zone),
                                "vulnerability_type": "dns_zone_transfer"
                            }
                        )
                        findings.append(finding)
                
                except Exception as e:
                    continue  # Skip failed tests
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    async def _test_dns_misconfigurations(self, domain: str) -> List[Finding]:
        """Test for DNS misconfigurations."""
        findings = []
        
        try:
            # Test for missing DNS records
            missing_records = await self._check_missing_dns_records(domain)
            if missing_records:
                finding = self.create_finding(
                    url=domain,
                    finding_type=FindingType.INFORMATION_DISCLOSURE,
                    title="Missing DNS Records",
                    description=f"Missing DNS records for domain {domain}: {', '.join(missing_records)}",
                    severity=FindingSeverity.MEDIUM,
                    impact="Missing DNS records can lead to service unavailability and security issues",
                    likelihood="high",
                    risk_score=6.0,
                    references=[
                        "https://owasp.org/www-community/attacks/DNS_Misconfiguration",
                        "https://cwe.mitre.org/data/definitions/200.html"
                    ],
                    raw_data={
                        "domain": domain,
                        "missing_records": missing_records,
                        "vulnerability_type": "missing_dns_records"
                    }
                )
                findings.append(finding)
            
            # Test for DNS misconfigurations
            misconfigs = await self._check_dns_misconfigurations(domain)
            if misconfigs:
                finding = self.create_finding(
                    url=domain,
                    finding_type=FindingType.INFORMATION_DISCLOSURE,
                    title="DNS Misconfiguration",
                    description=f"DNS misconfiguration detected for domain {domain}: {', '.join(misconfigs)}",
                    severity=FindingSeverity.MEDIUM,
                    impact="DNS misconfigurations can lead to service unavailability and security issues",
                    likelihood="high",
                    risk_score=6.5,
                    references=[
                        "https://owasp.org/www-community/attacks/DNS_Misconfiguration",
                        "https://cwe.mitre.org/data/definitions/200.html"
                    ],
                    raw_data={
                        "domain": domain,
                        "misconfigurations": misconfigs,
                        "vulnerability_type": "dns_misconfiguration"
                    }
                )
                findings.append(finding)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    async def _test_dns_security_records(self, domain: str) -> List[Finding]:
        """Test for DNS security records."""
        findings = []
        
        try:
            # Check for SPF record
            spf_record = await self._get_dns_record(domain, 'TXT')
            if spf_record and not any('v=spf1' in record for record in spf_record):
                finding = self.create_finding(
                    url=domain,
                    finding_type=FindingType.INFORMATION_DISCLOSURE,
                    title="Missing SPF Record",
                    description=f"SPF record is missing for domain {domain}",
                    severity=FindingSeverity.MEDIUM,
                    impact="Missing SPF record can lead to email spoofing and phishing attacks",
                    likelihood="high",
                    risk_score=6.0,
                    references=[
                        "https://owasp.org/www-community/attacks/Email_Spoofing",
                        "https://cwe.mitre.org/data/definitions/346.html"
                    ],
                    raw_data={
                        "domain": domain,
                        "record_type": "SPF",
                        "vulnerability_type": "missing_spf_record"
                    }
                )
                findings.append(finding)
            
            # Check for DMARC record
            dmarc_record = await self._get_dns_record(f'_dmarc.{domain}', 'TXT')
            if not dmarc_record or not any('v=DMARC1' in record for record in dmarc_record):
                finding = self.create_finding(
                    url=domain,
                    finding_type=FindingType.INFORMATION_DISCLOSURE,
                    title="Missing DMARC Record",
                    description=f"DMARC record is missing for domain {domain}",
                    severity=FindingSeverity.MEDIUM,
                    impact="Missing DMARC record can lead to email spoofing and phishing attacks",
                    likelihood="high",
                    risk_score=6.0,
                    references=[
                        "https://owasp.org/www-community/attacks/Email_Spoofing",
                        "https://cwe.mitre.org/data/definitions/346.html"
                    ],
                    raw_data={
                        "domain": domain,
                        "record_type": "DMARC",
                        "vulnerability_type": "missing_dmarc_record"
                    }
                )
                findings.append(finding)
            
            # Check for DKIM record
            dkim_record = await self._get_dns_record(f'default._domainkey.{domain}', 'TXT')
            if not dkim_record or not any('v=DKIM1' in record for record in dkim_record):
                finding = self.create_finding(
                    url=domain,
                    finding_type=FindingType.INFORMATION_DISCLOSURE,
                    title="Missing DKIM Record",
                    description=f"DKIM record is missing for domain {domain}",
                    severity=FindingSeverity.MEDIUM,
                    impact="Missing DKIM record can lead to email spoofing and phishing attacks",
                    likelihood="high",
                    risk_score=6.0,
                    references=[
                        "https://owasp.org/www-community/attacks/Email_Spoofing",
                        "https://cwe.mitre.org/data/definitions/346.html"
                    ],
                    raw_data={
                        "domain": domain,
                        "record_type": "DKIM",
                        "vulnerability_type": "missing_dkim_record"
                    }
                )
                findings.append(finding)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    async def _test_dns_vulnerabilities(self, domain: str) -> List[Finding]:
        """Test for DNS vulnerabilities."""
        findings = []
        
        try:
            # Check for DNS vulnerability patterns
            vuln_patterns = await self._find_dns_vulnerabilities(domain)
            if vuln_patterns:
                finding = self.create_finding(
                    url=domain,
                    finding_type=FindingType.INFORMATION_DISCLOSURE,
                    title="DNS Vulnerability Detected",
                    description=f"DNS vulnerability patterns detected for domain {domain}: {', '.join(vuln_patterns)}",
                    severity=FindingSeverity.MEDIUM,
                    impact="DNS vulnerabilities can lead to service unavailability and security issues",
                    likelihood="medium",
                    risk_score=6.5,
                    references=[
                        "https://owasp.org/www-community/attacks/DNS_Vulnerabilities",
                        "https://cwe.mitre.org/data/definitions/200.html"
                    ],
                    raw_data={
                        "domain": domain,
                        "vulnerability_patterns": vuln_patterns,
                        "vulnerability_type": "dns_vulnerability"
                    }
                )
                findings.append(finding)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    async def _check_missing_dns_records(self, domain: str) -> List[str]:
        """Check for missing DNS records."""
        missing_records = []
        
        # Check for A record
        try:
            dns.resolver.resolve(domain, 'A')
        except:
            missing_records.append('A')
        
        # Check for AAAA record
        try:
            dns.resolver.resolve(domain, 'AAAA')
        except:
            missing_records.append('AAAA')
        
        # Check for MX record
        try:
            dns.resolver.resolve(domain, 'MX')
        except:
            missing_records.append('MX')
        
        # Check for NS record
        try:
            dns.resolver.resolve(domain, 'NS')
        except:
            missing_records.append('NS')
        
        return missing_records
    
    async def _check_dns_misconfigurations(self, domain: str) -> List[str]:
        """Check for DNS misconfigurations."""
        misconfigs = []
        
        try:
            # Check for CNAME to root domain
            cname_records = await self._get_dns_record(domain, 'CNAME')
            if cname_records:
                misconfigs.append('CNAME to root domain')
            
            # Check for multiple A records
            a_records = await self._get_dns_record(domain, 'A')
            if a_records and len(a_records) > 1:
                misconfigs.append('Multiple A records')
            
            # Check for missing SOA record
            soa_records = await self._get_dns_record(domain, 'SOA')
            if not soa_records:
                misconfigs.append('Missing SOA record')
            
        except Exception as e:
            pass  # Skip failed tests
        
        return misconfigs
    
    async def _get_dns_record(self, domain: str, record_type: str) -> List[str]:
        """Get DNS record for domain."""
        try:
            records = dns.resolver.resolve(domain, record_type)
            return [str(record) for record in records]
        except:
            return []
    
    async def _find_dns_vulnerabilities(self, domain: str) -> List[str]:
        """Find DNS vulnerability patterns."""
        vuln_patterns = []
        
        try:
            # Get all TXT records
            txt_records = await self._get_dns_record(domain, 'TXT')
            
            for record in txt_records:
                for pattern in self.vulnerability_patterns:
                    if re.search(pattern, record, re.IGNORECASE):
                        vuln_patterns.append(pattern)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return list(set(vuln_patterns))  # Remove duplicates

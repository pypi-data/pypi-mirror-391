"""API Security scanner for BugBountyCrawler."""

import re
import asyncio
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class APISecurityScanner(BaseScanner):
    """Scanner for API security vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize API security scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "APISecurityScanner"
        
        # Common API endpoints
        self.api_endpoints = [
            '/api', '/api/v1', '/api/v2', '/api/v3', '/api/v4', '/api/v5',
            '/rest', '/rest/v1', '/rest/v2', '/rest/v3', '/rest/v4', '/rest/v5',
            '/graphql', '/graphiql', '/playground', '/explorer', '/docs', '/swagger',
            '/openapi', '/redoc', '/api-docs', '/api/docs', '/api/documentation',
            '/api/swagger', '/api/openapi', '/api/redoc', '/api/explorer',
            '/api/playground', '/api/graphql', '/api/graphiql', '/api/health',
            '/api/status', '/api/version', '/api/info', '/api/about',
        ]
        
        # Common API parameters
        self.api_parameters = [
            'id', 'user_id', 'account_id', 'profile_id', 'document_id', 'file_id',
            'order_id', 'transaction_id', 'payment_id', 'invoice_id', 'customer_id',
            'client_id', 'session_id', 'request_id', 'case_id', 'ticket_id',
            'message_id', 'post_id', 'article_id', 'comment_id', 'product_id',
            'item_id', 'cart_id', 'wishlist_id', 'category_id', 'subcategory_id',
            'group_id', 'team_id', 'project_id', 'task_id', 'issue_id', 'bug_id',
            'feature_id', 'milestone_id', 'release_id', 'version_id', 'build_id',
            'deployment_id', 'environment_id', 'server_id', 'host_id', 'device_id',
            'asset_id', 'resource_id', 'folder_id', 'directory_id', 'path_id',
            'route_id', 'endpoint_id', 'api_id', 'key_id', 'token_id', 'credential_id',
            'secret_id', 'config_id', 'setting_id', 'preference_id', 'option_id',
            'role_id', 'permission_id', 'privilege_id', 'access_id', 'audit_id',
            'log_id', 'event_id', 'activity_id', 'history_id', 'report_id',
            'dashboard_id', 'widget_id', 'chart_id', 'graph_id', 'table_id',
            'view_id', 'query_id', 'search_id', 'filter_id', 'sort_id',
            'order_by_id', 'limit_id', 'offset_id', 'page_id', 'size_id',
            'count_id', 'total_id', 'result_id', 'response_id',
        ]
        
        # BOLA (Broken Object Level Authorization) test cases
        self.bola_test_cases = [
            {'id': '1', 'description': 'Test with ID 1'},
            {'id': '2', 'description': 'Test with ID 2'},
            {'id': '3', 'description': 'Test with ID 3'},
            {'id': '999', 'description': 'Test with ID 999'},
            {'id': '0', 'description': 'Test with ID 0'},
            {'id': '-1', 'description': 'Test with ID -1'},
            {'id': '999999', 'description': 'Test with ID 999999'},
            {'id': 'admin', 'description': 'Test with admin ID'},
            {'id': 'root', 'description': 'Test with root ID'},
            {'id': 'test', 'description': 'Test with test ID'},
        ]
        
        # Mass assignment test cases
        self.mass_assignment_test_cases = [
            {'role': 'admin', 'is_admin': True, 'admin': True, 'administrator': True},
            {'role': 'user', 'is_user': True, 'user': True, 'guest': True},
            {'role': 'root', 'is_root': True, 'root': True, 'superuser': True},
            {'role': 'manager', 'is_manager': True, 'manager': True, 'moderator': True},
            {'role': 'test', 'is_test': True, 'test': True, 'demo': True},
            {'permission': 'read', 'can_read': True, 'read': True, 'view': True},
            {'permission': 'write', 'can_write': True, 'write': True, 'edit': True},
            {'permission': 'delete', 'can_delete': True, 'delete': True, 'remove': True},
            {'permission': 'admin', 'can_admin': True, 'admin': True, 'manage': True},
            {'permission': 'root', 'can_root': True, 'root': True, 'super': True},
        ]
        
        # GraphQL introspection queries
        self.graphql_introspection_queries = [
            'query { __schema { types { name } } }',
            'query { __schema { queryType { name } } }',
            'query { __schema { mutationType { name } } }',
            'query { __schema { subscriptionType { name } } }',
            'query { __schema { directives { name } } }',
            'query { __type(name: "Query") { fields { name } } }',
            'query { __type(name: "Mutation") { fields { name } } }',
            'query { __type(name: "Subscription") { fields { name } } }',
            'query { __type(name: "User") { fields { name } } }',
            'query { __type(name: "Admin") { fields { name } } }',
        ]
        
        # API versioning test cases
        self.api_versioning_test_cases = [
            '/api/v1', '/api/v2', '/api/v3', '/api/v4', '/api/v5',
            '/api/v1.0', '/api/v1.1', '/api/v1.2', '/api/v2.0', '/api/v2.1',
            '/api/1', '/api/2', '/api/3', '/api/4', '/api/5',
            '/api/1.0', '/api/1.1', '/api/1.2', '/api/2.0', '/api/2.1',
            '/rest/v1', '/rest/v2', '/rest/v3', '/rest/v4', '/rest/v5',
            '/rest/1', '/rest/2', '/rest/3', '/rest/4', '/rest/5',
        ]
        
        # HTTP method test cases
        self.http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE']
        
        # API response indicators
        self.success_indicators = [
            r'200\s+OK',
            r'201\s+Created',
            r'202\s+Accepted',
            r'204\s+No Content',
            r'Content-Type:\s*application/json',
            r'Content-Type:\s*application/xml',
            r'Content-Type:\s*text/json',
            r'Content-Type:\s*text/xml',
            r'"success":\s*true',
            r'"status":\s*"success"',
            r'"error":\s*false',
            r'"valid":\s*true',
            r'"found":\s*true',
            r'"exists":\s*true',
            r'"available":\s*true',
            r'"accessible":\s*true',
            r'"permitted":\s*true',
            r'"authorized":\s*true',
            r'"allowed":\s*true',
        ]
        
        # API error indicators
        self.error_indicators = [
            r'400\s+Bad Request',
            r'401\s+Unauthorized',
            r'403\s+Forbidden',
            r'404\s+Not Found',
            r'405\s+Method Not Allowed',
            r'406\s+Not Acceptable',
            r'408\s+Request Timeout',
            r'409\s+Conflict',
            r'410\s+Gone',
            r'411\s+Length Required',
            r'412\s+Precondition Failed',
            r'413\s+Payload Too Large',
            r'414\s+URI Too Long',
            r'415\s+Unsupported Media Type',
            r'416\s+Range Not Satisfiable',
            r'417\s+Expectation Failed',
            r'418\s+I\'m a teapot',
            r'421\s+Misdirected Request',
            r'422\s+Unprocessable Entity',
            r'423\s+Locked',
            r'424\s+Failed Dependency',
            r'425\s+Too Early',
            r'426\s+Upgrade Required',
            r'428\s+Precondition Required',
            r'429\s+Too Many Requests',
            r'431\s+Request Header Fields Too Large',
            r'451\s+Unavailable For Legal Reasons',
            r'500\s+Internal Server Error',
            r'501\s+Not Implemented',
            r'502\s+Bad Gateway',
            r'503\s+Service Unavailable',
            r'504\s+Gateway Timeout',
            r'505\s+HTTP Version Not Supported',
            r'506\s+Variant Also Negotiates',
            r'507\s+Insufficient Storage',
            r'508\s+Loop Detected',
            r'510\s+Not Extended',
            r'511\s+Network Authentication Required',
            r'"error":\s*"Access denied"',
            r'"error":\s*"Unauthorized"',
            r'"error":\s*"Forbidden"',
            r'"error":\s*"Not found"',
            r'"error":\s*"Method not allowed"',
            r'"error":\s*"Not acceptable"',
            r'"error":\s*"Request timeout"',
            r'"error":\s*"Conflict"',
            r'"error":\s*"Gone"',
            r'"error":\s*"Length required"',
            r'"error":\s*"Precondition failed"',
            r'"error":\s*"Payload too large"',
            r'"error":\s*"URI too long"',
            r'"error":\s*"Unsupported media type"',
            r'"error":\s*"Range not satisfiable"',
            r'"error":\s*"Expectation failed"',
            r'"error":\s*"I\'m a teapot"',
            r'"error":\s*"Misdirected request"',
            r'"error":\s*"Unprocessable entity"',
            r'"error":\s*"Locked"',
            r'"error":\s*"Failed dependency"',
            r'"error":\s*"Too early"',
            r'"error":\s*"Upgrade required"',
            r'"error":\s*"Precondition required"',
            r'"error":\s*"Too many requests"',
            r'"error":\s*"Request header fields too large"',
            r'"error":\s*"Unavailable for legal reasons"',
            r'"error":\s*"Internal server error"',
            r'"error":\s*"Not implemented"',
            r'"error":\s*"Bad gateway"',
            r'"error":\s*"Service unavailable"',
            r'"error":\s*"Gateway timeout"',
            r'"error":\s*"HTTP version not supported"',
            r'"error":\s*"Variant also negotiates"',
            r'"error":\s*"Insufficient storage"',
            r'"error":\s*"Loop detected"',
            r'"error":\s*"Not extended"',
            r'"error":\s*"Network authentication required"',
            r'"success":\s*false',
            r'"status":\s*"error"',
            r'"valid":\s*false',
            r'"found":\s*false',
            r'"exists":\s*false',
            r'"available":\s*false',
            r'"accessible":\s*false',
            r'"permitted":\s*false',
            r'"authorized":\s*false',
            r'"allowed":\s*false',
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for API security vulnerabilities."""
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
            
            # Test for BOLA vulnerabilities
            bola_findings = await self._test_bola_vulnerabilities(url)
            findings.extend(bola_findings)
            
            # Test for mass assignment vulnerabilities
            mass_assignment_findings = await self._test_mass_assignment_vulnerabilities(url)
            findings.extend(mass_assignment_findings)
            
            # Test for GraphQL introspection
            graphql_findings = await self._test_graphql_introspection(url)
            findings.extend(graphql_findings)
            
            # Test for API versioning issues
            versioning_findings = await self._test_api_versioning(url)
            findings.extend(versioning_findings)
            
            # Test for HTTP method issues
            method_findings = await self._test_http_methods(url)
            findings.extend(method_findings)
            
            # Test for API endpoint discovery
            endpoint_findings = await self._test_api_endpoint_discovery(url)
            findings.extend(endpoint_findings)
            
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
    
    async def _test_bola_vulnerabilities(self, url: str) -> List[Finding]:
        """Test for BOLA (Broken Object Level Authorization) vulnerabilities."""
        findings = []
        
        # Parse URL parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Test each parameter for BOLA
        for param_name, param_values in query_params.items():
            if param_values and param_name.lower() in self.api_parameters:
                original_value = param_values[0]
                
                # Test with different IDs
                for test_case in self.bola_test_cases[:5]:  # Test first 5 cases
                    test_id = test_case['id']
                    
                    if test_id != original_value:
                        try:
                            # Create test URL with different ID
                            test_url = self._create_test_url(url, param_name, test_id)
                            
                            response = await self.make_request(test_url)
                            content = await response.text()
                            
                            # Check if BOLA vulnerability exists
                            if self._is_bola_vulnerability(content, response.status):
                                finding = self.create_finding(
                                    url=url,
                                    finding_type=FindingType.API_MISCONFIGURATION,
                                    title=f"BOLA Vulnerability - {param_name} (ID: {test_id})",
                                    description=f"Broken Object Level Authorization (BOLA) vulnerability detected in parameter '{param_name}'. Can access object with ID: {test_id}",
                                    severity=FindingSeverity.HIGH,
                                    impact="BOLA vulnerabilities can lead to unauthorized access to other users' data and resources",
                                    likelihood="high",
                                    risk_score=8.5,
                                    references=[
                                        "https://owasp.org/www-community/attacks/Broken_Object_Level_Authorization",
                                        "https://cwe.mitre.org/data/definitions/639.html"
                                    ],
                                    raw_data={
                                        "parameter": param_name,
                                        "original_value": original_value,
                                        "test_id": test_id,
                                        "response_status": response.status,
                                        "response_content": content[:500] if len(content) > 500 else content,
                                        "bola_type": "object_level_authorization"
                                    }
                                )
                                findings.append(finding)
                                break  # Found vulnerability, no need to test more IDs
                            
                            # Small delay to avoid overwhelming the server
                            await asyncio.sleep(0.1)
                            
                        except Exception as e:
                            continue  # Skip failed tests
        
        return findings
    
    async def _test_mass_assignment_vulnerabilities(self, url: str) -> List[Finding]:
        """Test for mass assignment vulnerabilities."""
        findings = []
        
        # Test with different mass assignment payloads
        for test_case in self.mass_assignment_test_cases[:5]:  # Test first 5 cases
            try:
                # Create test data with mass assignment payload
                test_data = json.dumps(test_case)
                
                response = await self.make_request(url, method='POST', data=test_data)
                content = await response.text()
                
                # Check if mass assignment was successful
                if self._is_mass_assignment_successful(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.API_MISCONFIGURATION,
                        title="Mass Assignment Vulnerability",
                        description=f"Mass assignment vulnerability detected. Payload: {test_case}",
                        severity=FindingSeverity.HIGH,
                        impact="Mass assignment vulnerabilities can lead to privilege escalation and unauthorized access",
                        likelihood="medium",
                        risk_score=8.0,
                        references=[
                            "https://owasp.org/www-community/attacks/Mass_Assignment",
                            "https://cwe.mitre.org/data/definitions/915.html"
                        ],
                        raw_data={
                            "payload": test_case,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "mass_assignment_type": "parameter_pollution"
                        }
                    )
                    findings.append(finding)
                    break  # Found vulnerability, no need to test more cases
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_graphql_introspection(self, url: str) -> List[Finding]:
        """Test for GraphQL introspection vulnerabilities."""
        findings = []
        
        # Test GraphQL introspection queries
        for query in self.graphql_introspection_queries[:5]:  # Test first 5 queries
            try:
                # Create GraphQL request
                graphql_data = {
                    'query': query,
                    'variables': {},
                    'operationName': None
                }
                
                response = await self.make_request(url, method='POST', data=json.dumps(graphql_data))
                content = await response.text()
                
                # Check if GraphQL introspection is enabled
                if self._is_graphql_introspection_enabled(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.GRAPHQL_INTROSPECTION,
                        title="GraphQL Introspection Enabled",
                        description=f"GraphQL introspection is enabled, which may expose sensitive schema information. Query: {query}",
                        severity=FindingSeverity.MEDIUM,
                        impact="GraphQL introspection can expose sensitive schema information and internal API structure",
                        likelihood="high",
                        risk_score=6.5,
                        references=[
                            "https://owasp.org/www-community/attacks/GraphQL_Introspection",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "query": query,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "graphql_type": "introspection_enabled"
                        }
                    )
                    findings.append(finding)
                    break  # Found vulnerability, no need to test more queries
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_api_versioning(self, url: str) -> List[Finding]:
        """Test for API versioning issues."""
        findings = []
        
        # Test different API versions
        for version in self.api_versioning_test_cases[:5]:  # Test first 5 versions
            try:
                # Create test URL with different version
                test_url = f"{url.rstrip('/')}{version}"
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check if API version is accessible
                if self._is_api_version_accessible(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.API_VERSIONING,
                        title=f"API Version Accessible - {version}",
                        description=f"API version '{version}' is accessible, which may expose deprecated or vulnerable endpoints",
                        severity=FindingSeverity.MEDIUM,
                        impact="Accessible API versions may expose deprecated or vulnerable endpoints",
                        likelihood="medium",
                        risk_score=6.0,
                        references=[
                            "https://owasp.org/www-community/attacks/API_Versioning",
                            "https://cwe.mitre.org/data/definitions/1104.html"
                        ],
                        raw_data={
                            "version": version,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "api_versioning_type": "deprecated_version"
                        }
                    )
                    findings.append(finding)
                    break  # Found vulnerability, no need to test more versions
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_http_methods(self, url: str) -> List[Finding]:
        """Test for HTTP method issues."""
        findings = []
        
        # Test different HTTP methods
        for method in self.http_methods:
            try:
                response = await self.make_request(url, method=method)
                content = await response.text()
                
                # Check if HTTP method is allowed
                if self._is_http_method_allowed(content, response.status, method):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.API_MISCONFIGURATION,
                        title=f"HTTP Method Allowed - {method}",
                        description=f"HTTP method '{method}' is allowed, which may expose sensitive operations",
                        severity=FindingSeverity.MEDIUM,
                        impact=f"HTTP method '{method}' may expose sensitive operations or allow unauthorized actions",
                        likelihood="medium",
                        risk_score=6.5,
                        references=[
                            "https://owasp.org/www-community/attacks/HTTP_Method_Override",
                            "https://cwe.mitre.org/data/definitions/650.html"
                        ],
                        raw_data={
                            "method": method,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "http_method_type": "method_allowed"
                        }
                    )
                    findings.append(finding)
                    break  # Found vulnerability, no need to test more methods
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_api_endpoint_discovery(self, url: str) -> List[Finding]:
        """Test for API endpoint discovery."""
        findings = []
        
        # Test common API endpoints
        for endpoint in self.api_endpoints[:5]:  # Test first 5 endpoints
            try:
                # Create test URL with API endpoint
                test_url = f"{url.rstrip('/')}{endpoint}"
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check if API endpoint is accessible
                if self._is_api_endpoint_accessible(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.API_MISCONFIGURATION,
                        title=f"API Endpoint Accessible - {endpoint}",
                        description=f"API endpoint '{endpoint}' is accessible, which may expose sensitive API information",
                        severity=FindingSeverity.LOW,
                        impact="Accessible API endpoints may expose sensitive API information and structure",
                        likelihood="high",
                        risk_score=5.0,
                        references=[
                            "https://owasp.org/www-community/attacks/API_Endpoint_Discovery",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "endpoint": endpoint,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "api_endpoint_type": "endpoint_discovery"
                        }
                    )
                    findings.append(finding)
                    break  # Found vulnerability, no need to test more endpoints
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    def _is_bola_vulnerability(self, content: str, status_code: int) -> bool:
        """Check if BOLA vulnerability exists."""
        # Check for success indicators
        for indicator in self.success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _is_mass_assignment_successful(self, content: str, status_code: int) -> bool:
        """Check if mass assignment was successful."""
        # Check for success indicators
        for indicator in self.success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _is_graphql_introspection_enabled(self, content: str, status_code: int) -> bool:
        """Check if GraphQL introspection is enabled."""
        # Check for GraphQL introspection indicators
        introspection_indicators = [
            r'"__schema"',
            r'"__type"',
            r'"__queryType"',
            r'"__mutationType"',
            r'"__subscriptionType"',
            r'"__directives"',
            r'"__fields"',
            r'"__enumValues"',
            r'"__inputFields"',
            r'"__ofType"',
            r'"__possibleTypes"',
            r'"__interfaces"',
            r'"__args"',
            r'"__returnType"',
            r'"__fieldType"',
            r'"__enumType"',
            r'"__inputType"',
            r'"__interfaceType"',
            r'"__unionType"',
            r'"__scalarType"',
            r'"__objectType"',
            r'"__listType"',
            r'"__nonNullType"',
            r'"__directiveType"',
            r'"__directiveLocation"',
            r'"__directiveLocationEnum"',
            r'"__directiveLocationEnumValue"',
            r'"__directiveLocationEnumValueName"',
            r'"__directiveLocationEnumValueDescription"',
            r'"__directiveLocationEnumValueIsDeprecated"',
            r'"__directiveLocationEnumValueDeprecationReason"',
            r'"__directiveLocationEnumValueName"',
            r'"__directiveLocationEnumValueDescription"',
            r'"__directiveLocationEnumValueIsDeprecated"',
            r'"__directiveLocationEnumValueDeprecationReason"',
            r'"__directiveLocationEnumValueName"',
            r'"__directiveLocationEnumValueDescription"',
            r'"__directiveLocationEnumValueIsDeprecated"',
            r'"__directiveLocationEnumValueDeprecationReason"',
            r'"__directiveLocationEnumValueName"',
            r'"__directiveLocationEnumValueDescription"',
            r'"__directiveLocationEnumValueIsDeprecated"',
            r'"__directiveLocationEnumValueDeprecationReason"',
            r'"__directiveLocationEnumValueName"',
            r'"__directiveLocationEnumValueDescription"',
            r'"__directiveLocationEnumValueIsDeprecated"',
            r'"__directiveLocationEnumValueDeprecationReason"',
        ]
        
        for indicator in introspection_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _is_api_version_accessible(self, content: str, status_code: int) -> bool:
        """Check if API version is accessible."""
        # Check for success indicators
        for indicator in self.success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _is_http_method_allowed(self, content: str, status_code: int, method: str) -> bool:
        """Check if HTTP method is allowed."""
        # Check for success indicators
        for indicator in self.success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _is_api_endpoint_accessible(self, content: str, status_code: int) -> bool:
        """Check if API endpoint is accessible."""
        # Check for success indicators
        for indicator in self.success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _create_test_url(self, url: str, param_name: str, param_value: str) -> str:
        """Create test URL with manipulated parameter value."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Replace the parameter value
        query_params[param_name] = [param_value]
        
        # Rebuild URL
        new_query = urlencode(query_params, doseq=True)
        new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        if new_query:
            new_url += f"?{new_query}"
        
        return new_url











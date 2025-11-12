"""IDOR (Insecure Direct Object Reference) scanner for BugBountyCrawler."""

import re
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class IDORScanner(BaseScanner):
    """Scanner for Insecure Direct Object Reference (IDOR) vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize IDOR scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "IDORScanner"
        
        # Common ID parameter names
        self.id_parameters = [
            'id', 'user_id', 'uid', 'account_id', 'profile_id', 'document_id',
            'file_id', 'order_id', 'transaction_id', 'payment_id', 'invoice_id',
            'customer_id', 'client_id', 'session_id', 'request_id', 'case_id',
            'ticket_id', 'message_id', 'post_id', 'article_id', 'comment_id',
            'product_id', 'item_id', 'cart_id', 'wishlist_id', 'category_id',
            'subcategory_id', 'group_id', 'team_id', 'project_id', 'task_id',
            'issue_id', 'bug_id', 'feature_id', 'milestone_id', 'release_id',
            'version_id', 'build_id', 'deployment_id', 'environment_id',
            'server_id', 'host_id', 'device_id', 'asset_id', 'resource_id',
            'folder_id', 'directory_id', 'path_id', 'route_id', 'endpoint_id',
            'api_id', 'key_id', 'token_id', 'credential_id', 'secret_id',
            'config_id', 'setting_id', 'preference_id', 'option_id',
            'role_id', 'permission_id', 'privilege_id', 'access_id',
            'audit_id', 'log_id', 'event_id', 'activity_id', 'history_id',
            'report_id', 'dashboard_id', 'widget_id', 'chart_id', 'graph_id',
            'table_id', 'view_id', 'query_id', 'search_id', 'filter_id',
            'sort_id', 'order_by_id', 'limit_id', 'offset_id', 'page_id',
            'size_id', 'count_id', 'total_id', 'result_id', 'response_id',
        ]
        
        # Common ID patterns and formats
        self.id_patterns = [
            r'^\d+$',  # Numeric IDs
            r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',  # UUIDs
            r'^[a-fA-F0-9]{32}$',  # MD5 hashes
            r'^[a-fA-F0-9]{40}$',  # SHA1 hashes
            r'^[a-fA-F0-9]{64}$',  # SHA256 hashes
            r'^[A-Za-z0-9+/]{20,}={0,2}$',  # Base64 encoded
            r'^[A-Za-z0-9_-]{10,}$',  # Alphanumeric with special chars
        ]
        
        # Common ID manipulation techniques
        self.manipulation_techniques = {
            'increment': lambda x: str(int(x) + 1) if x.isdigit() else None,
            'decrement': lambda x: str(int(x) - 1) if x.isdigit() else None,
            'neighbor': lambda x: str(int(x) + 1) if x.isdigit() else None,
            'random': lambda x: str(int(x) + 100) if x.isdigit() else None,
            'zero': lambda x: '0' if x.isdigit() else None,
            'negative': lambda x: f"-{x}" if x.isdigit() else None,
            'max': lambda x: '999999' if x.isdigit() else None,
            'min': lambda x: '1' if x.isdigit() else None,
        }
        
        # Response indicators of successful IDOR
        self.success_indicators = [
            r'200\s+OK',
            r'Content-Type:\s*application/json',
            r'Content-Type:\s*text/html',
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
        
        # Response indicators of failed IDOR (access denied)
        self.failure_indicators = [
            r'403\s+Forbidden',
            r'401\s+Unauthorized',
            r'404\s+Not Found',
            r'500\s+Internal Server Error',
            r'"error":\s*"Access denied"',
            r'"error":\s*"Unauthorized"',
            r'"error":\s*"Forbidden"',
            r'"error":\s*"Not found"',
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
        
        # Common sensitive endpoints that might have IDOR
        self.sensitive_endpoints = [
            '/api/users/',
            '/api/accounts/',
            '/api/profiles/',
            '/api/documents/',
            '/api/files/',
            '/api/orders/',
            '/api/payments/',
            '/api/invoices/',
            '/api/customers/',
            '/api/clients/',
            '/api/sessions/',
            '/api/requests/',
            '/api/cases/',
            '/api/tickets/',
            '/api/messages/',
            '/api/posts/',
            '/api/articles/',
            '/api/comments/',
            '/api/products/',
            '/api/items/',
            '/api/carts/',
            '/api/wishlists/',
            '/api/categories/',
            '/api/subcategories/',
            '/api/groups/',
            '/api/teams/',
            '/api/projects/',
            '/api/tasks/',
            '/api/issues/',
            '/api/bugs/',
            '/api/features/',
            '/api/milestones/',
            '/api/releases/',
            '/api/versions/',
            '/api/builds/',
            '/api/deployments/',
            '/api/environments/',
            '/api/servers/',
            '/api/hosts/',
            '/api/devices/',
            '/api/assets/',
            '/api/resources/',
            '/api/folders/',
            '/api/directories/',
            '/api/paths/',
            '/api/routes/',
            '/api/endpoints/',
            '/api/apis/',
            '/api/keys/',
            '/api/tokens/',
            '/api/credentials/',
            '/api/secrets/',
            '/api/configs/',
            '/api/settings/',
            '/api/preferences/',
            '/api/options/',
            '/api/roles/',
            '/api/permissions/',
            '/api/privileges/',
            '/api/accesses/',
            '/api/audits/',
            '/api/logs/',
            '/api/events/',
            '/api/activities/',
            '/api/histories/',
            '/api/reports/',
            '/api/dashboards/',
            '/api/widgets/',
            '/api/charts/',
            '/api/graphs/',
            '/api/tables/',
            '/api/views/',
            '/api/queries/',
            '/api/searches/',
            '/api/filters/',
            '/api/sorts/',
            '/api/order_bys/',
            '/api/limits/',
            '/api/offsets/',
            '/api/pages/',
            '/api/sizes/',
            '/api/counts/',
            '/api/totals/',
            '/api/results/',
            '/api/responses/',
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for IDOR vulnerabilities."""
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
            
            # Test each parameter for IDOR
            for param_name, param_values in query_params.items():
                if param_values:
                    original_value = param_values[0]
                    
                    # Check if parameter looks like an ID
                    if self._is_id_parameter(param_name, original_value):
                        # Test IDOR vulnerabilities
                        idor_findings = await self._test_idor_vulnerability(
                            url, param_name, original_value, baseline_content
                        )
                        findings.extend(idor_findings)
            
            # Test for horizontal privilege escalation
            horizontal_findings = await self._test_horizontal_escalation(url, query_params)
            findings.extend(horizontal_findings)
            
            # Test for vertical privilege escalation
            vertical_findings = await self._test_vertical_escalation(url, query_params)
            findings.extend(vertical_findings)
            
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
    
    async def _test_idor_vulnerability(self, url: str, param_name: str, 
                                     original_value: str, baseline_content: str) -> List[Finding]:
        """Test for IDOR vulnerabilities in a specific parameter."""
        findings = []
        
        # Test different manipulation techniques
        for technique_name, manipulation_func in self.manipulation_techniques.items():
            try:
                # Apply manipulation technique
                manipulated_value = manipulation_func(original_value)
                
                if manipulated_value is None:
                    continue
                
                # Create test URL with manipulated ID
                test_url = self._create_test_url(url, param_name, manipulated_value)
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check if manipulation was successful (indicates IDOR)
                if self._is_manipulation_successful(content, baseline_content):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.AUTHORIZATION_BYPASS,
                        title=f"IDOR Vulnerability - {technique_name.title()} Manipulation (Parameter: {param_name})",
                        description=f"Insecure Direct Object Reference (IDOR) vulnerability detected in parameter '{param_name}' using {technique_name} manipulation. Original: {original_value}, Manipulated: {manipulated_value}",
                        severity=FindingSeverity.HIGH,
                        impact="IDOR vulnerabilities can lead to unauthorized access to other users' data, privilege escalation, and data breaches",
                        likelihood="high",
                        risk_score=8.5,
                        references=[
                            "https://owasp.org/www-community/attacks/Insecure_Direct_Object_References",
                            "https://cwe.mitre.org/data/definitions/639.html"
                        ],
                        raw_data={
                            "parameter": param_name,
                            "original_value": original_value,
                            "manipulated_value": manipulated_value,
                            "technique": technique_name,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "idor_type": "parameter_manipulation"
                        }
                    )
                    findings.append(finding)
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_horizontal_escalation(self, url: str, query_params: Dict[str, List[str]]) -> List[Finding]:
        """Test for horizontal privilege escalation."""
        findings = []
        
        # Look for user-related parameters
        user_params = [p for p in query_params.keys() if 'user' in p.lower() or 'id' in p.lower()]
        
        for param_name in user_params:
            if query_params[param_name]:
                original_value = query_params[param_name][0]
                
                # Test with different user IDs (simulating access to other users' data)
                test_user_ids = ['1', '2', '3', '999', '0', '-1']
                
                for test_user_id in test_user_ids:
                    if test_user_id != original_value:
                        try:
                            # Create test URL with different user ID
                            test_url = self._create_test_url(url, param_name, test_user_id)
                            
                            response = await self.make_request(test_url)
                            content = await response.text()
                            
                            # Check if we can access other user's data
                            if self._is_horizontal_escalation_successful(content):
                                finding = self.create_finding(
                                    url=url,
                                    finding_type=FindingType.AUTHORIZATION_BYPASS,
                                    title=f"Horizontal Privilege Escalation (Parameter: {param_name})",
                                    description=f"Horizontal privilege escalation detected in parameter '{param_name}'. Can access other users' data using ID: {test_user_id}",
                                    severity=FindingSeverity.HIGH,
                                    impact="Horizontal privilege escalation allows access to other users' data and resources",
                                    likelihood="high",
                                    risk_score=8.0,
                                    references=[
                                        "https://owasp.org/www-community/attacks/Insecure_Direct_Object_References",
                                        "https://cwe.mitre.org/data/definitions/639.html"
                                    ],
                                    raw_data={
                                        "parameter": param_name,
                                        "original_value": original_value,
                                        "test_user_id": test_user_id,
                                        "response_content": content[:500] if len(content) > 500 else content,
                                        "idor_type": "horizontal_escalation"
                                    }
                                )
                                findings.append(finding)
                                break  # Found vulnerability, no need to test more IDs
                            
                            # Small delay to avoid overwhelming the server
                            await asyncio.sleep(0.1)
                            
                        except Exception as e:
                            continue  # Skip failed tests
        
        return findings
    
    async def _test_vertical_escalation(self, url: str, query_params: Dict[str, List[str]]) -> List[Finding]:
        """Test for vertical privilege escalation."""
        findings = []
        
        # Look for role or permission related parameters
        role_params = [p for p in query_params.keys() if any(role in p.lower() for role in ['role', 'permission', 'privilege', 'access', 'level', 'type'])]
        
        for param_name in role_params:
            if query_params[param_name]:
                original_value = query_params[param_name][0]
                
                # Test with different privilege levels
                privilege_levels = ['admin', 'administrator', 'root', 'superuser', 'manager', 'moderator', 'user', 'guest', '1', '2', '3', '0']
                
                for privilege_level in privilege_levels:
                    if privilege_level != original_value:
                        try:
                            # Create test URL with different privilege level
                            test_url = self._create_test_url(url, param_name, privilege_level)
                            
                            response = await self.make_request(test_url)
                            content = await response.text()
                            
                            # Check if we can escalate privileges
                            if self._is_vertical_escalation_successful(content, privilege_level):
                                finding = self.create_finding(
                                    url=url,
                                    finding_type=FindingType.AUTHORIZATION_BYPASS,
                                    title=f"Vertical Privilege Escalation (Parameter: {param_name})",
                                    description=f"Vertical privilege escalation detected in parameter '{param_name}'. Can escalate to privilege level: {privilege_level}",
                                    severity=FindingSeverity.CRITICAL,
                                    impact="Vertical privilege escalation allows unauthorized access to administrative functions and sensitive operations",
                                    likelihood="medium",
                                    risk_score=9.0,
                                    references=[
                                        "https://owasp.org/www-community/attacks/Insecure_Direct_Object_References",
                                        "https://cwe.mitre.org/data/definitions/639.html"
                                    ],
                                    raw_data={
                                        "parameter": param_name,
                                        "original_value": original_value,
                                        "privilege_level": privilege_level,
                                        "response_content": content[:500] if len(content) > 500 else content,
                                        "idor_type": "vertical_escalation"
                                    }
                                )
                                findings.append(finding)
                                break  # Found vulnerability, no need to test more levels
                            
                            # Small delay to avoid overwhelming the server
                            await asyncio.sleep(0.1)
                            
                        except Exception as e:
                            continue  # Skip failed tests
        
        return findings
    
    def _is_id_parameter(self, param_name: str, param_value: str) -> bool:
        """Check if parameter looks like an ID parameter."""
        # Check parameter name
        if any(id_param in param_name.lower() for id_param in self.id_parameters):
            return True
        
        # Check parameter value format
        for pattern in self.id_patterns:
            if re.match(pattern, param_value):
                return True
        
        return False
    
    def _is_manipulation_successful(self, content: str, baseline_content: str) -> bool:
        """Check if ID manipulation was successful."""
        # Check for success indicators
        for indicator in self.success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check for significant content difference
        if abs(len(content) - len(baseline_content)) > 50:
            return True
        
        # Check for different response structure
        if content != baseline_content and len(content) > 100:
            return True
        
        return False
    
    def _is_horizontal_escalation_successful(self, content: str) -> bool:
        """Check if horizontal escalation was successful."""
        # Check for success indicators
        for indicator in self.success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check for user-specific data patterns
        user_data_patterns = [
            r'"username":\s*"[^"]*"',
            r'"email":\s*"[^"]*"',
            r'"profile":\s*\{[^}]*\}',
            r'"data":\s*\{[^}]*\}',
            r'"user":\s*\{[^}]*\}',
            r'"account":\s*\{[^}]*\}',
            r'"personal":\s*\{[^}]*\}',
            r'"private":\s*\{[^}]*\}',
            r'"sensitive":\s*\{[^}]*\}',
            r'"confidential":\s*\{[^}]*\}',
        ]
        
        for pattern in user_data_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _is_vertical_escalation_successful(self, content: str, privilege_level: str) -> bool:
        """Check if vertical escalation was successful."""
        # Check for success indicators
        for indicator in self.success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check for administrative data patterns
        admin_patterns = [
            r'"admin":\s*true',
            r'"administrator":\s*true',
            r'"root":\s*true',
            r'"superuser":\s*true',
            r'"manager":\s*true',
            r'"moderator":\s*true',
            r'"privilege":\s*"[^"]*"',
            r'"permission":\s*"[^"]*"',
            r'"access":\s*"[^"]*"',
            r'"role":\s*"[^"]*"',
            r'"level":\s*"[^"]*"',
            r'"type":\s*"[^"]*"',
        ]
        
        for pattern in admin_patterns:
            if re.search(pattern, content, re.IGNORECASE):
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
    
    def _extract_parameters_from_url(self, url: str) -> Dict[str, List[str]]:
        """Extract parameters from URL."""
        try:
            parsed = urlparse(url)
            return parse_qs(parsed.query)
        except Exception:
            return {}

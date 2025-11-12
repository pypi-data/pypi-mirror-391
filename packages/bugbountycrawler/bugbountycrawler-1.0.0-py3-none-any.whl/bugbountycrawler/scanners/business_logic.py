"""Business Logic vulnerability scanner for BugBountyCrawler."""

import asyncio
import time
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp
import re

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class BusinessLogicScanner(BaseScanner):
    """Scanner for business logic vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize business logic scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "BusinessLogicScanner"
        
        # Sensitive parameters that might indicate business logic
        self.price_params = ['price', 'amount', 'cost', 'total', 'subtotal', 'discount', 'coupon']
        self.quantity_params = ['quantity', 'qty', 'amount', 'count', 'number']
        self.id_params = ['id', 'user_id', 'account_id', 'order_id', 'transaction_id']
        self.status_params = ['status', 'state', 'approved', 'verified', 'confirmed']
        self.step_params = ['step', 'stage', 'phase', 'page', 'current_step']
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for business logic vulnerabilities."""
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
            
            baseline_content = await response.text()
            
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
            
            # Test for different business logic flaws
            findings.extend(await self._test_price_manipulation(url, query_params))
            findings.extend(await self._test_negative_values(url, query_params))
            findings.extend(await self._test_quantity_bypass(url, query_params))
            findings.extend(await self._test_workflow_bypass(url, query_params))
            findings.extend(await self._test_race_conditions(url, query_params))
        
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
    
    async def _test_price_manipulation(self, url: str, params: Dict) -> List[Finding]:
        """Test for price manipulation vulnerabilities."""
        findings = []
        
        for param_name, param_values in params.items():
            if not any(price_param in param_name.lower() for price_param in self.price_params):
                continue
            
            original_value = param_values[0]
            
            # Test negative price
            test_values = ['-1', '-100', '0', '0.01']
            
            for test_value in test_values:
                try:
                    test_url = self._create_test_url(url, param_name, test_value)
                    response = await self.make_request(test_url)
                    content = await response.text()
                    
                    # Check if request was successful with manipulated price
                    if response.status == 200 and self._indicates_success(content):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.BUSINESS_LOGIC,
                            title=f"Price Manipulation Vulnerability (Parameter: {param_name})",
                            description=f"Application accepts invalid price value '{test_value}' in parameter '{param_name}'",
                            severity=FindingSeverity.HIGH,
                            impact="Price manipulation can lead to financial loss through zero or negative pricing",
                            likelihood="medium",
                            risk_score=8.0,
                            references=[
                                "https://owasp.org/www-community/vulnerabilities/Business_logic_vulnerability"
                            ],
                            raw_data={
                                "parameter": param_name,
                                "original_value": original_value,
                                "manipulated_value": test_value,
                                "response_status": response.status
                            }
                        )
                        findings.append(finding)
                        return findings  # Stop after first finding
                    
                    await asyncio.sleep(0.1)
                except Exception:
                    continue
        
        return findings
    
    async def _test_negative_values(self, url: str, params: Dict) -> List[Finding]:
        """Test for negative value vulnerabilities."""
        findings = []
        
        for param_name, param_values in params.items():
            if not any(qty_param in param_name.lower() for qty_param in self.quantity_params):
                continue
            
            original_value = param_values[0]
            
            # Test negative quantity
            try:
                test_url = self._create_test_url(url, param_name, '-1')
                response = await self.make_request(test_url)
                content = await response.text()
                
                if response.status == 200 and self._indicates_success(content):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.BUSINESS_LOGIC,
                        title=f"Negative Quantity Vulnerability (Parameter: {param_name})",
                        description=f"Application accepts negative quantity value in parameter '{param_name}'",
                        severity=FindingSeverity.MEDIUM,
                        impact="Negative quantities can lead to unexpected behavior or financial losses",
                        likelihood="medium",
                        risk_score=6.0,
                        references=[
                            "https://owasp.org/www-community/vulnerabilities/Business_logic_vulnerability"
                        ],
                        raw_data={
                            "parameter": param_name,
                            "original_value": original_value,
                            "manipulated_value": "-1"
                        }
                    )
                    findings.append(finding)
                
                await asyncio.sleep(0.1)
            except Exception:
                pass
        
        return findings
    
    async def _test_quantity_bypass(self, url: str, params: Dict) -> List[Finding]:
        """Test for quantity limit bypass."""
        findings = []
        
        for param_name, param_values in params.items():
            if not any(qty_param in param_name.lower() for qty_param in self.quantity_params):
                continue
            
            # Test extremely high quantities
            test_values = ['999999', '2147483647', '9999999999']
            
            for test_value in test_values:
                try:
                    test_url = self._create_test_url(url, param_name, test_value)
                    response = await self.make_request(test_url)
                    content = await response.text()
                    
                    if response.status == 200 and self._indicates_success(content):
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.BUSINESS_LOGIC,
                            title=f"Quantity Limit Bypass (Parameter: {param_name})",
                            description=f"Application accepts unrealistic quantity value '{test_value}'",
                            severity=FindingSeverity.MEDIUM,
                            impact="Quantity limit bypass can lead to inventory issues or denial of service",
                            likelihood="medium",
                            risk_score=6.0,
                            references=[
                                "https://owasp.org/www-community/vulnerabilities/Business_logic_vulnerability"
                            ],
                            raw_data={
                                "parameter": param_name,
                                "manipulated_value": test_value
                            }
                        )
                        findings.append(finding)
                        return findings
                    
                    await asyncio.sleep(0.1)
                except Exception:
                    continue
        
        return findings
    
    async def _test_workflow_bypass(self, url: str, params: Dict) -> List[Finding]:
        """Test for workflow bypass vulnerabilities."""
        findings = []
        
        for param_name, param_values in params.items():
            if not any(step_param in param_name.lower() for step_param in self.step_params):
                continue
            
            original_value = param_values[0]
            
            try:
                # Try skipping steps
                if original_value.isdigit():
                    test_value = str(int(original_value) + 2)  # Skip ahead
                    test_url = self._create_test_url(url, param_name, test_value)
                    response = await self.make_request(test_url)
                    content = await response.text()
                    
                    if response.status == 200:
                        finding = self.create_finding(
                            url=url,
                            finding_type=FindingType.BUSINESS_LOGIC,
                            title=f"Workflow Bypass Vulnerability (Parameter: {param_name})",
                            description=f"Application allows skipping workflow steps from '{original_value}' to '{test_value}'",
                            severity=FindingSeverity.HIGH,
                            impact="Workflow bypass can allow users to skip payment, verification, or approval steps",
                            likelihood="medium",
                            risk_score=7.5,
                            references=[
                                "https://owasp.org/www-community/vulnerabilities/Business_logic_vulnerability"
                            ],
                            raw_data={
                                "parameter": param_name,
                                "original_step": original_value,
                                "bypassed_to_step": test_value
                            }
                        )
                        findings.append(finding)
                
                await asyncio.sleep(0.1)
            except Exception:
                pass
        
        return findings
    
    async def _test_race_conditions(self, url: str, params: Dict) -> List[Finding]:
        """Test for race condition vulnerabilities."""
        findings = []
        
        # Look for endpoints that might be vulnerable to race conditions
        if any(keyword in url.lower() for keyword in ['transfer', 'withdraw', 'payment', 'purchase', 'redeem']):
            try:
                # Send multiple concurrent requests
                tasks = [self.make_request(url) for _ in range(5)]
                start_time = time.time()
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()
                
                # Check if all requests succeeded
                success_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
                
                if success_count >= 4:  # Most requests succeeded
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.BUSINESS_LOGIC,
                        title="Potential Race Condition Vulnerability",
                        description=f"Endpoint processed {success_count} concurrent identical requests, indicating potential race condition",
                        severity=FindingSeverity.MEDIUM,
                        impact="Race conditions can lead to double-spending, inventory issues, or financial losses",
                        likelihood="low",
                        risk_score=5.5,
                        references=[
                            "https://owasp.org/www-community/vulnerabilities/Business_logic_vulnerability"
                        ],
                        raw_data={
                            "concurrent_requests": 5,
                            "successful_requests": success_count,
                            "elapsed_time": end_time - start_time
                        }
                    )
                    findings.append(finding)
            except Exception:
                pass
        
        return findings
    
    def _indicates_success(self, content: str) -> bool:
        """Check if response indicates successful operation."""
        success_indicators = [
            r'"success":\s*true',
            r'"status":\s*"success"',
            r'"error":\s*false',
            r'successfully',
            r'completed',
            r'confirmed',
            r'approved',
            r'accepted'
        ]
        
        for indicator in success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        return False
    
    def _create_test_url(self, url: str, param_name: str, value: str) -> str:
        """Create test URL with modified parameter."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        query_params[param_name] = [value]
        
        new_query = urlencode(query_params, doseq=True)
        new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        if new_query:
            new_url += f"?{new_query}"
        
        return new_url


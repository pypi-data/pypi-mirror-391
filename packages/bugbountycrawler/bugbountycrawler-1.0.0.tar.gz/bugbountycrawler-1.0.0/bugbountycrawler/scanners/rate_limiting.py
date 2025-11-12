"""Rate limiting scanner for BugBountyCrawler."""

import asyncio
import time
from typing import List, Dict, Any
import aiohttp
import statistics

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class RateLimitingScanner(BaseScanner):
    """Scanner for rate limiting bypass vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize rate limiting scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "RateLimitingScanner"
        
        # Test configurations
        self.rapid_request_count = 50
        self.concurrent_request_count = 20
        self.delay_between_tests = 2  # seconds
        self.request_timeout = 10  # seconds
        
        # Rate limiting indicators
        self.rate_limit_indicators = {
            'status_codes': [429, 503, 502, 504],
            'headers': ['Retry-After', 'X-RateLimit-Remaining', 'X-RateLimit-Reset'],
            'response_phrases': ['rate limit', 'too many requests', 'quota exceeded', 'throttled']
        }
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for rate limiting issues."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Make initial request to get baseline
            baseline_response = await self.make_request(url)
            response_time = baseline_response.headers.get("X-Response-Time", 0.0)
            status_code = baseline_response.status
            headers = dict(baseline_response.headers)
            content_length = int(baseline_response.headers.get("Content-Length", 0))
            
            # Test 1: Rapid sequential requests
            rapid_findings = await self._test_rapid_requests(url)
            findings.extend(rapid_findings)
            
            # Wait between tests to avoid triggering rate limits
            await asyncio.sleep(self.delay_between_tests)
            
            # Test 2: Concurrent requests
            concurrent_findings = await self._test_concurrent_requests(url)
            findings.extend(concurrent_findings)
            
            # Wait between tests
            await asyncio.sleep(self.delay_between_tests)
            
            # Test 3: IP header bypass attempts
            ip_bypass_findings = await self._test_ip_header_bypass(url)
            findings.extend(ip_bypass_findings)
            
            # Wait between tests
            await asyncio.sleep(self.delay_between_tests)
            
            # Test 4: User-Agent rotation
            ua_bypass_findings = await self._test_user_agent_rotation(url)
            findings.extend(ua_bypass_findings)
            
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
    
    async def _test_rapid_requests(self, url: str) -> List[Finding]:
        """Test rapid sequential requests to detect rate limiting."""
        findings = []
        response_times = []
        status_codes = []
        rate_limited = False
        
        try:
            for i in range(self.rapid_request_count):
                start_time = time.time()
                response = await self.make_request(url)
                end_time = time.time()
                
                response_times.append(end_time - start_time)
                status_codes.append(response.status)
                
                # Check if rate limited
                if response.status in self.rate_limit_indicators['status_codes']:
                    rate_limited = True
                    break
                
                # Check response headers for rate limit info
                if any(header in response.headers for header in self.rate_limit_indicators['headers']):
                    rate_limited = True
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
            
            # Analyze results
            if rate_limited:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.RATE_LIMITING,
                    title="Rate Limiting Detected",
                    description=f"Rate limiting is active on this endpoint. Detected after {len(response_times)} requests.",
                    severity=FindingSeverity.LOW,
                    impact="Rate limiting is working correctly and preventing abuse",
                    likelihood="high",
                    risk_score=2.0,
                    references=[
                        "https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks"
                    ],
                    raw_data={
                        "test_type": "rapid_requests",
                        "requests_made": len(response_times),
                        "average_response_time": statistics.mean(response_times) if response_times else 0,
                        "status_codes": status_codes
                    }
                )
                findings.append(finding)
            else:
                # No rate limiting detected - potential vulnerability
                avg_response_time = statistics.mean(response_times) if response_times else 0
                
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.RATE_LIMITING,
                    title="No Rate Limiting Detected",
                    description=f"No rate limiting detected after {self.rapid_request_count} rapid requests. This may allow brute force attacks.",
                    severity=FindingSeverity.MEDIUM,
                    impact="Missing rate limiting allows brute force attacks and DoS",
                    likelihood="high",
                    risk_score=7.0,
                    references=[
                        "https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks",
                        "https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html"
                    ],
                    raw_data={
                        "test_type": "rapid_requests",
                        "requests_made": self.rapid_request_count,
                        "average_response_time": avg_response_time,
                        "status_codes": status_codes,
                        "rate_limiting_active": False
                    }
                )
                findings.append(finding)
        
        except Exception as e:
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.RATE_LIMITING,
                title="Rate Limiting Test Failed",
                description=f"Rate limiting test failed: {str(e)}",
                severity=FindingSeverity.LOW,
                impact="Unable to determine rate limiting status",
                likelihood="low",
                risk_score=1.0,
                raw_data={"error": str(e), "test_type": "rapid_requests"}
            )
            findings.append(finding)
        
        return findings
    
    async def _test_concurrent_requests(self, url: str) -> List[Finding]:
        """Test concurrent requests to detect rate limiting bypass."""
        findings = []
        
        try:
            # Create concurrent requests
            tasks = []
            for i in range(self.concurrent_request_count):
                task = self.make_request(url)
                tasks.append(task)
            
            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze responses
            successful_requests = 0
            rate_limited_requests = 0
            status_codes = []
            
            for response in responses:
                if isinstance(response, Exception):
                    continue
                
                status_codes.append(response.status)
                
                if response.status == 200:
                    successful_requests += 1
                elif response.status in self.rate_limit_indicators['status_codes']:
                    rate_limited_requests += 1
            
            # Check for rate limiting bypass
            if successful_requests > 10:  # More than half succeeded
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.RATE_LIMITING,
                    title="Potential Rate Limiting Bypass",
                    description=f"Concurrent requests bypassed rate limiting. {successful_requests}/{self.concurrent_request_count} requests succeeded.",
                    severity=FindingSeverity.HIGH,
                    impact="Rate limiting bypass allows concurrent brute force attacks",
                    likelihood="high",
                    risk_score=8.0,
                    references=[
                        "https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks"
                    ],
                    raw_data={
                        "test_type": "concurrent_requests",
                        "total_requests": self.concurrent_request_count,
                        "successful_requests": successful_requests,
                        "rate_limited_requests": rate_limited_requests,
                        "status_codes": status_codes
                    }
                )
                findings.append(finding)
        
        except Exception as e:
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.RATE_LIMITING,
                title="Concurrent Request Test Failed",
                description=f"Concurrent request test failed: {str(e)}",
                severity=FindingSeverity.LOW,
                impact="Unable to test concurrent request handling",
                likelihood="low",
                risk_score=1.0,
                raw_data={"error": str(e), "test_type": "concurrent_requests"}
            )
            findings.append(finding)
        
        return findings
    
    async def _test_ip_header_bypass(self, url: str) -> List[Finding]:
        """Test IP header bypass techniques."""
        findings = []
        
        # Common IP bypass headers
        bypass_headers = [
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Real-IP": "127.0.0.1"},
            {"X-Originating-IP": "127.0.0.1"},
            {"X-Remote-IP": "127.0.0.1"},
            {"X-Remote-Addr": "127.0.0.1"},
            {"X-Client-IP": "127.0.0.1"},
            {"CF-Connecting-IP": "127.0.0.1"},
            {"True-Client-IP": "127.0.0.1"}
        ]
        
        try:
            # Get baseline response
            baseline_response = await self.make_request(url)
            baseline_status = baseline_response.status
            
            # Test each bypass header
            bypass_successful = False
            for headers in bypass_headers:
                response = await self.make_request(url, headers=headers)
                
                # If response differs from baseline, bypass might be working
                if response.status != baseline_status or response.status == 200:
                    bypass_successful = True
                    break
                
                await asyncio.sleep(0.5)  # Small delay
            
            if bypass_successful:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.RATE_LIMITING,
                    title="IP Header Bypass Detected",
                    description="Rate limiting can be bypassed using IP spoofing headers",
                    severity=FindingSeverity.HIGH,
                    impact="IP header bypass allows rate limiting circumvention",
                    likelihood="medium",
                    risk_score=7.5,
                    references=[
                        "https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks"
                    ],
                    raw_data={
                        "test_type": "ip_header_bypass",
                        "headers_tested": [list(h.keys())[0] for h in bypass_headers],
                        "bypass_successful": True
                    }
                )
                findings.append(finding)
        
        except Exception as e:
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.RATE_LIMITING,
                title="IP Header Bypass Test Failed",
                description=f"IP header bypass test failed: {str(e)}",
                severity=FindingSeverity.LOW,
                impact="Unable to test IP header bypass",
                likelihood="low",
                risk_score=1.0,
                raw_data={"error": str(e), "test_type": "ip_header_bypass"}
            )
            findings.append(finding)
        
        return findings
    
    async def _test_user_agent_rotation(self, url: str) -> List[Finding]:
        """Test User-Agent rotation bypass."""
        findings = []
        
        # Common User-Agents for testing
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "curl/7.68.0",
            "Python-urllib/3.8",
            "Go-http-client/1.1",
            "Java/11.0.2"
        ]
        
        try:
            # Get baseline response
            baseline_response = await self.make_request(url)
            baseline_status = baseline_response.status
            
            # Test each User-Agent
            ua_bypass_successful = False
            for ua in user_agents:
                headers = {"User-Agent": ua}
                response = await self.make_request(url, headers=headers)
                
                if response.status != baseline_status:
                    ua_bypass_successful = True
                    break
                
                await asyncio.sleep(0.5)  # Small delay
            
            if ua_bypass_successful:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.RATE_LIMITING,
                    title="User-Agent Bypass Detected",
                    description="Rate limiting can be bypassed by rotating User-Agent headers",
                    severity=FindingSeverity.MEDIUM,
                    impact="User-Agent rotation allows rate limiting circumvention",
                    likelihood="medium",
                    risk_score=6.0,
                    references=[
                        "https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks"
                    ],
                    raw_data={
                        "test_type": "user_agent_rotation",
                        "user_agents_tested": user_agents,
                        "bypass_successful": True
                    }
                )
                findings.append(finding)
        
        except Exception as e:
            finding = self.create_finding(
                url=url,
                finding_type=FindingType.RATE_LIMITING,
                title="User-Agent Bypass Test Failed",
                description=f"User-Agent bypass test failed: {str(e)}",
                severity=FindingSeverity.LOW,
                impact="Unable to test User-Agent bypass",
                likelihood="low",
                risk_score=1.0,
                raw_data={"error": str(e), "test_type": "user_agent_rotation"}
            )
            findings.append(finding)
        
        return findings

"""IAM Scanner for BugBountyCrawler."""

import asyncio
import aiohttp
import re
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class IAMScanner(BaseScanner):
    """Scanner for IAM and privilege escalation vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize IAM scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "IAMScanner"
        
        # Overly permissive IAM patterns
        self.permissive_patterns = [
            r'"Effect":\s*"Allow".*"Action":\s*"\*"',
            r'"Effect":\s*"Allow".*"Resource":\s*"\*"',
            r'"Effect":\s*"Allow".*"Principal":\s*"\*"',
            r'"Effect":\s*"Allow".*"Condition":\s*\{\}',
            r'"Effect":\s*"Allow".*"NotAction":\s*"s3:GetObject"',
            r'"Effect":\s*"Allow".*"NotResource":\s*"arn:aws:s3:::my-bucket"',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"s3:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"ec2:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"iam:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"lambda:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"rds:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"dynamodb:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"sns:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"sqs:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"kms:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"secretsmanager:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"ssm:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"cloudformation:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"cloudtrail:\*".*\]',
            r'"Effect":\s*"Allow".*"Action":\s*\[.*"config:\*".*\]',
        ]
        
        # Dangerous IAM actions
        self.dangerous_actions = [
            'iam:CreateUser',
            'iam:DeleteUser',
            'iam:AttachUserPolicy',
            'iam:DetachUserPolicy',
            'iam:CreateRole',
            'iam:DeleteRole',
            'iam:AttachRolePolicy',
            'iam:DetachRolePolicy',
            'iam:PassRole',
            'iam:AssumeRole',
            'iam:CreatePolicy',
            'iam:DeletePolicy',
            'iam:CreatePolicyVersion',
            'iam:SetDefaultPolicyVersion',
            'iam:PutRolePolicy',
            'iam:DeleteRolePolicy',
            'iam:PutUserPolicy',
            'iam:DeleteUserPolicy',
            'iam:PutGroupPolicy',
            'iam:DeleteGroupPolicy',
            'iam:CreateAccessKey',
            'iam:DeleteAccessKey',
            'iam:UpdateAccessKey',
            'iam:CreateLoginProfile',
            'iam:DeleteLoginProfile',
            'iam:UpdateLoginProfile',
            'iam:CreateVirtualMFADevice',
            'iam:DeleteVirtualMFADevice',
            'iam:EnableMFADevice',
            'iam:DisableMFADevice',
            'iam:ResyncMFADevice',
            'iam:DeactivateMFADevice',
            'iam:DeleteMFADevice',
            'iam:CreateSAMLProvider',
            'iam:DeleteSAMLProvider',
            'iam:UpdateSAMLProvider',
            'iam:CreateOpenIDConnectProvider',
            'iam:DeleteOpenIDConnectProvider',
            'iam:UpdateOpenIDConnectProvider',
            'iam:CreateInstanceProfile',
            'iam:DeleteInstanceProfile',
            'iam:AddRoleToInstanceProfile',
            'iam:RemoveRoleFromInstanceProfile',
            'iam:CreateServiceLinkedRole',
            'iam:DeleteServiceLinkedRole',
            'iam:TagRole',
            'iam:UntagRole',
            'iam:TagUser',
            'iam:UntagUser',
            'iam:TagPolicy',
            'iam:UntagPolicy',
            'iam:TagSAMLProvider',
            'iam:UntagSAMLProvider',
            'iam:TagOpenIDConnectProvider',
            'iam:UntagOpenIDConnectProvider',
            'iam:TagInstanceProfile',
            'iam:UntagInstanceProfile',
            'iam:TagMFADevice',
            'iam:UntagMFADevice',
            'iam:TagServerCertificate',
            'iam:UntagServerCertificate',
            'iam:TagSigningCertificate',
            'iam:UntagSigningCertificate',
            'iam:TagSSHPublicKey',
            'iam:UntagSSHPublicKey',
            'iam:TagUser',
            'iam:UntagUser',
            'iam:TagRole',
            'iam:UntagRole',
            'iam:TagPolicy',
            'iam:UntagPolicy',
            'iam:TagSAMLProvider',
            'iam:UntagSAMLProvider',
            'iam:TagOpenIDConnectProvider',
            'iam:UntagOpenIDConnectProvider',
            'iam:TagInstanceProfile',
            'iam:UntagInstanceProfile',
            'iam:TagMFADevice',
            'iam:UntagMFADevice',
            'iam:TagServerCertificate',
            'iam:UntagServerCertificate',
            'iam:TagSigningCertificate',
            'iam:UntagSigningCertificate',
            'iam:TagSSHPublicKey',
            'iam:UntagSSHPublicKey',
        ]
        
        # Privilege escalation patterns
        self.privilege_escalation_patterns = [
            r'iam:PassRole.*iam:CreateRole',
            r'iam:PassRole.*iam:AttachRolePolicy',
            r'iam:PassRole.*iam:PutRolePolicy',
            r'iam:AssumeRole.*iam:CreateRole',
            r'iam:AssumeRole.*iam:AttachRolePolicy',
            r'iam:AssumeRole.*iam:PutRolePolicy',
            r'iam:CreateUser.*iam:AttachUserPolicy',
            r'iam:CreateUser.*iam:PutUserPolicy',
            r'iam:CreateAccessKey.*iam:CreateUser',
            r'iam:CreateLoginProfile.*iam:CreateUser',
            r'iam:CreateVirtualMFADevice.*iam:CreateUser',
            r'iam:EnableMFADevice.*iam:CreateUser',
            r'iam:CreateSAMLProvider.*iam:CreateRole',
            r'iam:CreateOpenIDConnectProvider.*iam:CreateRole',
            r'iam:CreateInstanceProfile.*iam:CreateRole',
            r'iam:CreateServiceLinkedRole.*iam:CreateRole',
        ]
        
        # Common IAM endpoints
        self.iam_endpoints = [
            '/iam/',
            '/iam/users',
            '/iam/roles',
            '/iam/policies',
            '/iam/groups',
            '/iam/access-keys',
            '/iam/login-profiles',
            '/iam/mfa-devices',
            '/iam/saml-providers',
            '/iam/openid-connect-providers',
            '/iam/instance-profiles',
            '/iam/service-linked-roles',
            '/iam/account-summary',
            '/iam/account-password-policy',
            '/iam/account-alias',
            '/iam/credential-report',
            '/iam/access-report',
            '/iam/organizations',
            '/iam/account',
            '/iam/account-summary',
        ]
        
        # IAM policy test cases
        self.policy_test_cases = [
            {
                'name': 'Wildcard Action',
                'policy': {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Action': '*',
                            'Resource': '*'
                        }
                    ]
                }
            },
            {
                'name': 'Wildcard Resource',
                'policy': {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Action': 's3:GetObject',
                            'Resource': '*'
                        }
                    ]
                }
            },
            {
                'name': 'Wildcard Principal',
                'policy': {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Principal': '*',
                            'Action': 's3:GetObject',
                            'Resource': 'arn:aws:s3:::my-bucket/*'
                        }
                    ]
                }
            },
            {
                'name': 'Dangerous Actions',
                'policy': {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Action': [
                                'iam:CreateUser',
                                'iam:AttachUserPolicy',
                                'iam:CreateAccessKey'
                            ],
                            'Resource': '*'
                        }
                    ]
                }
            },
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for IAM vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Test for IAM endpoint exposure
            iam_findings = await self._test_iam_endpoints(url)
            findings.extend(iam_findings)
            
            # Test for IAM policy exposure
            policy_findings = await self._test_iam_policies(url)
            findings.extend(policy_findings)
            
            # Test for privilege escalation
            escalation_findings = await self._test_privilege_escalation(url)
            findings.extend(escalation_findings)
            
            # Test for overly permissive policies
            permissive_findings = await self._test_permissive_policies(url)
            findings.extend(permissive_findings)
            
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
    
    async def _test_iam_endpoints(self, url: str) -> List[Finding]:
        """Test for exposed IAM endpoints."""
        findings = []
        
        for endpoint in self.iam_endpoints[:5]:  # Test first 5 endpoints
            try:
                test_url = f"{url.rstrip('/')}{endpoint}"
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check if IAM endpoint is accessible
                if self._is_iam_endpoint_accessible(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.KUBERNETES_MISCONFIGURATION,
                        title=f"Exposed IAM Endpoint - {endpoint}",
                        description=f"IAM endpoint '{endpoint}' is accessible and may expose sensitive information",
                        severity=FindingSeverity.HIGH,
                        impact="Exposed IAM endpoints can lead to privilege escalation and unauthorized access",
                        likelihood="medium",
                        risk_score=8.0,
                        references=[
                            "https://owasp.org/www-community/attacks/IAM_Misconfiguration",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "endpoint": endpoint,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "exposed_iam_endpoint"
                        }
                    )
                    findings.append(finding)
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_iam_policies(self, url: str) -> List[Finding]:
        """Test for IAM policy vulnerabilities."""
        findings = []
        
        for test_case in self.policy_test_cases:
            try:
                # Test policy via POST request
                policy_data = json.dumps(test_case['policy'])
                
                response = await self.make_request(url, method='POST', data=policy_data)
                content = await response.text()
                
                # Check if policy was accepted
                if self._is_policy_accepted(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.KUBERNETES_MISCONFIGURATION,
                        title=f"Dangerous IAM Policy Accepted - {test_case['name']}",
                        description=f"Dangerous IAM policy '{test_case['name']}' was accepted by the system",
                        severity=FindingSeverity.CRITICAL,
                        impact="Dangerous IAM policies can lead to complete account compromise and privilege escalation",
                        likelihood="medium",
                        risk_score=9.5,
                        references=[
                            "https://owasp.org/www-community/attacks/IAM_Misconfiguration",
                            "https://cwe.mitre.org/data/definitions/250.html"
                        ],
                        raw_data={
                            "policy_name": test_case['name'],
                            "policy": test_case['policy'],
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "dangerous_iam_policy"
                        }
                    )
                    findings.append(finding)
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_privilege_escalation(self, url: str) -> List[Finding]:
        """Test for privilege escalation vulnerabilities."""
        findings = []
        
        try:
            response = await self.make_request(url)
            content = await response.text()
            
            # Check for privilege escalation patterns
            escalation_patterns = self._find_privilege_escalation_patterns(content)
            if escalation_patterns:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.KUBERNETES_MISCONFIGURATION,
                    title="IAM Privilege Escalation Vulnerability",
                    description=f"Privilege escalation vulnerability detected: {', '.join(escalation_patterns)}",
                    severity=FindingSeverity.CRITICAL,
                    impact="IAM privilege escalation can lead to complete account compromise and unauthorized access",
                    likelihood="medium",
                    risk_score=9.0,
                    references=[
                        "https://owasp.org/www-community/attacks/Privilege_Escalation",
                        "https://cwe.mitre.org/data/definitions/250.html"
                    ],
                    raw_data={
                        "escalation_patterns": escalation_patterns,
                        "response_content": content[:500] if len(content) > 500 else content,
                        "vulnerability_type": "privilege_escalation"
                    }
                )
                findings.append(finding)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    async def _test_permissive_policies(self, url: str) -> List[Finding]:
        """Test for overly permissive IAM policies."""
        findings = []
        
        try:
            response = await self.make_request(url)
            content = await response.text()
            
            # Check for permissive policy patterns
            permissive_patterns = self._find_permissive_patterns(content)
            if permissive_patterns:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.KUBERNETES_MISCONFIGURATION,
                    title="Overly Permissive IAM Policy",
                    description=f"Overly permissive IAM policy detected: {', '.join(permissive_patterns)}",
                    severity=FindingSeverity.HIGH,
                    impact="Overly permissive IAM policies can lead to unauthorized access and privilege escalation",
                    likelihood="high",
                    risk_score=8.5,
                    references=[
                        "https://owasp.org/www-community/attacks/IAM_Misconfiguration",
                        "https://cwe.mitre.org/data/definitions/250.html"
                    ],
                    raw_data={
                        "permissive_patterns": permissive_patterns,
                        "response_content": content[:500] if len(content) > 500 else content,
                        "vulnerability_type": "permissive_iam_policy"
                    }
                )
                findings.append(finding)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    def _is_iam_endpoint_accessible(self, content: str, status_code: int) -> bool:
        """Check if IAM endpoint is accessible."""
        # Check status code
        if status_code != 200:
            return False
        
        # Check for IAM-related content
        iam_indicators = [
            r'iam',
            r'identity.*access.*management',
            r'user',
            r'role',
            r'policy',
            r'group',
            r'access.*key',
            r'login.*profile',
            r'mfa.*device',
            r'saml.*provider',
            r'openid.*connect.*provider',
            r'instance.*profile',
            r'service.*linked.*role',
            r'account.*summary',
            r'account.*password.*policy',
            r'account.*alias',
            r'credential.*report',
            r'access.*report',
            r'organizations',
        ]
        
        for indicator in iam_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        return False
    
    def _is_policy_accepted(self, content: str, status_code: int) -> bool:
        """Check if IAM policy was accepted."""
        # Check for success indicators
        success_indicators = [
            r'200\s+OK',
            r'"success":\s*true',
            r'"status":\s*"success"',
            r'"error":\s*false',
            r'"accepted":\s*true',
            r'"valid":\s*true',
            r'"created":\s*true',
            r'"updated":\s*true',
            r'"applied":\s*true',
            r'"enabled":\s*true',
        ]
        
        for indicator in success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check status code
        if status_code == 200:
            return True
        
        return False
    
    def _find_privilege_escalation_patterns(self, content: str) -> List[str]:
        """Find privilege escalation patterns in content."""
        escalation_patterns = []
        
        for pattern in self.privilege_escalation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            escalation_patterns.extend(matches)
        
        return list(set(escalation_patterns))  # Remove duplicates
    
    def _find_permissive_patterns(self, content: str) -> List[str]:
        """Find overly permissive IAM patterns in content."""
        permissive_patterns = []
        
        for pattern in self.permissive_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            permissive_patterns.extend(matches)
        
        return list(set(permissive_patterns))  # Remove duplicates

"""Kubernetes Scanner for BugBountyCrawler."""

import asyncio
import aiohttp
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class KubernetesScanner(BaseScanner):
    """Scanner for Kubernetes vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize Kubernetes scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "KubernetesScanner"
        
        # Kubernetes endpoints
        self.k8s_endpoints = [
            '/api/v1/',
            '/api/v1/namespaces',
            '/api/v1/pods',
            '/api/v1/services',
            '/api/v1/secrets',
            '/api/v1/configmaps',
            '/api/v1/nodes',
            '/api/v1/persistentvolumes',
            '/api/v1/persistentvolumeclaims',
            '/api/v1/events',
            '/api/v1/endpoints',
            '/api/v1/limitranges',
            '/api/v1/resourcequotas',
            '/api/v1/serviceaccounts',
            '/api/v1/componentstatuses',
            '/api/v1/namespaces/default',
            '/api/v1/namespaces/kube-system',
            '/api/v1/namespaces/kube-public',
            '/api/v1/namespaces/kube-node-lease',
            '/api/v1/namespaces/default/pods',
            '/api/v1/namespaces/default/services',
            '/api/v1/namespaces/default/secrets',
            '/api/v1/namespaces/default/configmaps',
            '/api/v1/namespaces/kube-system/pods',
            '/api/v1/namespaces/kube-system/services',
            '/api/v1/namespaces/kube-system/secrets',
            '/api/v1/namespaces/kube-system/configmaps',
            '/api/v1/namespaces/kube-public/pods',
            '/api/v1/namespaces/kube-public/services',
            '/api/v1/namespaces/kube-public/secrets',
            '/api/v1/namespaces/kube-public/configmaps',
            '/api/v1/namespaces/kube-node-lease/pods',
            '/api/v1/namespaces/kube-node-lease/services',
            '/api/v1/namespaces/kube-node-lease/secrets',
            '/api/v1/namespaces/kube-node-lease/configmaps',
            '/api/v1/namespaces/default/events',
            '/api/v1/namespaces/kube-system/events',
            '/api/v1/namespaces/kube-public/events',
            '/api/v1/namespaces/kube-node-lease/events',
            '/api/v1/namespaces/default/endpoints',
            '/api/v1/namespaces/kube-system/endpoints',
            '/api/v1/namespaces/kube-public/endpoints',
            '/api/v1/namespaces/kube-node-lease/endpoints',
            '/api/v1/namespaces/default/limitranges',
            '/api/v1/namespaces/kube-system/limitranges',
            '/api/v1/namespaces/kube-public/limitranges',
            '/api/v1/namespaces/kube-node-lease/limitranges',
            '/api/v1/namespaces/default/resourcequotas',
            '/api/v1/namespaces/kube-system/resourcequotas',
            '/api/v1/namespaces/kube-public/resourcequotas',
            '/api/v1/namespaces/kube-node-lease/resourcequotas',
            '/api/v1/namespaces/default/serviceaccounts',
            '/api/v1/namespaces/kube-system/serviceaccounts',
            '/api/v1/namespaces/kube-public/serviceaccounts',
            '/api/v1/namespaces/kube-node-lease/serviceaccounts',
            '/api/v1/namespaces/default/componentstatuses',
            '/api/v1/namespaces/kube-system/componentstatuses',
            '/api/v1/namespaces/kube-public/componentstatuses',
            '/api/v1/namespaces/kube-node-lease/componentstatuses',
            '/api/v1/namespaces/default/persistentvolumes',
            '/api/v1/namespaces/kube-system/persistentvolumes',
            '/api/v1/namespaces/kube-public/persistentvolumes',
            '/api/v1/namespaces/kube-node-lease/persistentvolumes',
            '/api/v1/namespaces/default/persistentvolumeclaims',
            '/api/v1/namespaces/kube-system/persistentvolumeclaims',
            '/api/v1/namespaces/kube-public/persistentvolumeclaims',
            '/api/v1/namespaces/kube-node-lease/persistentvolumeclaims',
            '/api/v1/namespaces/default/events',
            '/api/v1/namespaces/kube-system/events',
            '/api/v1/namespaces/kube-public/events',
            '/api/v1/namespaces/kube-node-lease/events',
            '/api/v1/namespaces/default/endpoints',
            '/api/v1/namespaces/kube-system/endpoints',
            '/api/v1/namespaces/kube-public/endpoints',
            '/api/v1/namespaces/kube-node-lease/endpoints',
            '/api/v1/namespaces/default/limitranges',
            '/api/v1/namespaces/kube-system/limitranges',
            '/api/v1/namespaces/kube-public/limitranges',
            '/api/v1/namespaces/kube-node-lease/limitranges',
            '/api/v1/namespaces/default/resourcequotas',
            '/api/v1/namespaces/kube-system/resourcequotas',
            '/api/v1/namespaces/kube-public/resourcequotas',
            '/api/v1/namespaces/kube-node-lease/resourcequotas',
            '/api/v1/namespaces/default/serviceaccounts',
            '/api/v1/namespaces/kube-system/serviceaccounts',
            '/api/v1/namespaces/kube-public/serviceaccounts',
            '/api/v1/namespaces/kube-node-lease/serviceaccounts',
            '/api/v1/namespaces/default/componentstatuses',
            '/api/v1/namespaces/kube-system/componentstatuses',
            '/api/v1/namespaces/kube-public/componentstatuses',
            '/api/v1/namespaces/kube-node-lease/componentstatuses',
            '/api/v1/namespaces/default/persistentvolumes',
            '/api/v1/namespaces/kube-system/persistentvolumes',
            '/api/v1/namespaces/kube-public/persistentvolumes',
            '/api/v1/namespaces/kube-node-lease/persistentvolumes',
            '/api/v1/namespaces/default/persistentvolumeclaims',
            '/api/v1/namespaces/kube-system/persistentvolumeclaims',
            '/api/v1/namespaces/kube-public/persistentvolumeclaims',
            '/api/v1/namespaces/kube-node-lease/persistentvolumeclaims',
        ]
        
        # Kubernetes dashboard endpoints
        self.dashboard_endpoints = [
            '/dashboard',
            '/kubernetes-dashboard',
            '/k8s-dashboard',
            '/kube-dashboard',
            '/dashboard/',
            '/kubernetes-dashboard/',
            '/k8s-dashboard/',
            '/kube-dashboard/',
            '/dashboard/#/',
            '/kubernetes-dashboard/#/',
            '/k8s-dashboard/#/',
            '/kube-dashboard/#/',
            '/dashboard/#/overview',
            '/kubernetes-dashboard/#/overview',
            '/k8s-dashboard/#/overview',
            '/kube-dashboard/#/overview',
            '/dashboard/#/pods',
            '/kubernetes-dashboard/#/pods',
            '/k8s-dashboard/#/pods',
            '/kube-dashboard/#/pods',
            '/dashboard/#/services',
            '/kubernetes-dashboard/#/services',
            '/k8s-dashboard/#/services',
            '/kube-dashboard/#/services',
            '/dashboard/#/secrets',
            '/kubernetes-dashboard/#/secrets',
            '/k8s-dashboard/#/secrets',
            '/kube-dashboard/#/secrets',
            '/dashboard/#/configmaps',
            '/kubernetes-dashboard/#/configmaps',
            '/k8s-dashboard/#/configmaps',
            '/kube-dashboard/#/configmaps',
            '/dashboard/#/nodes',
            '/kubernetes-dashboard/#/nodes',
            '/k8s-dashboard/#/nodes',
            '/kube-dashboard/#/nodes',
            '/dashboard/#/persistentvolumes',
            '/kubernetes-dashboard/#/persistentvolumes',
            '/k8s-dashboard/#/persistentvolumes',
            '/kube-dashboard/#/persistentvolumes',
            '/dashboard/#/persistentvolumeclaims',
            '/kubernetes-dashboard/#/persistentvolumeclaims',
            '/k8s-dashboard/#/persistentvolumeclaims',
            '/kube-dashboard/#/persistentvolumeclaims',
            '/dashboard/#/events',
            '/kubernetes-dashboard/#/events',
            '/k8s-dashboard/#/events',
            '/kube-dashboard/#/events',
            '/dashboard/#/endpoints',
            '/kubernetes-dashboard/#/endpoints',
            '/k8s-dashboard/#/endpoints',
            '/kube-dashboard/#/endpoints',
            '/dashboard/#/limitranges',
            '/kubernetes-dashboard/#/limitranges',
            '/k8s-dashboard/#/limitranges',
            '/kube-dashboard/#/limitranges',
            '/dashboard/#/resourcequotas',
            '/kubernetes-dashboard/#/resourcequotas',
            '/k8s-dashboard/#/resourcequotas',
            '/kube-dashboard/#/resourcequotas',
            '/dashboard/#/serviceaccounts',
            '/kubernetes-dashboard/#/serviceaccounts',
            '/k8s-dashboard/#/serviceaccounts',
            '/kube-dashboard/#/serviceaccounts',
            '/dashboard/#/componentstatuses',
            '/kubernetes-dashboard/#/componentstatuses',
            '/k8s-dashboard/#/componentstatuses',
            '/kube-dashboard/#/componentstatuses',
        ]
        
        # Kubernetes vulnerability patterns
        self.vulnerability_patterns = [
            r'kubectl',
            r'kubernetes',
            r'k8s',
            r'minikube',
            r'docker',
            r'containerd',
            r'cri-o',
            r'rkt',
            r'podman',
            r'helm',
            r'kustomize',
            r'kustomization',
            r'kustomization\.yaml',
            r'kustomization\.yml',
            r'kustomization\.json',
            r'kustomization\.toml',
            r'kustomization\.ini',
            r'kustomization\.cfg',
            r'kustomization\.conf',
            r'kustomization\.config',
            r'kustomization\.properties',
            r'kustomization\.xml',
            r'kustomization\.yaml',
            r'kustomization\.yml',
            r'kustomization\.json',
            r'kustomization\.toml',
            r'kustomization\.ini',
            r'kustomization\.cfg',
            r'kustomization\.conf',
            r'kustomization\.config',
            r'kustomization\.properties',
            r'kustomization\.xml',
        ]
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for Kubernetes vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Test for Kubernetes API endpoints
            api_findings = await self._test_k8s_api_endpoints(url)
            findings.extend(api_findings)
            
            # Test for Kubernetes dashboard
            dashboard_findings = await self._test_k8s_dashboard(url)
            findings.extend(dashboard_findings)
            
            # Test for Kubernetes vulnerabilities
            vuln_findings = await self._test_k8s_vulnerabilities(url)
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
    
    async def _test_k8s_api_endpoints(self, url: str) -> List[Finding]:
        """Test for Kubernetes API endpoints."""
        findings = []
        
        for endpoint in self.k8s_endpoints[:10]:  # Test first 10 endpoints
            try:
                test_url = f"{url.rstrip('/')}{endpoint}"
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check if Kubernetes API endpoint is accessible
                if self._is_k8s_api_accessible(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.KUBERNETES_MISCONFIGURATION,
                        title=f"Exposed Kubernetes API - {endpoint}",
                        description=f"Kubernetes API endpoint '{endpoint}' is accessible and may expose sensitive information",
                        severity=FindingSeverity.HIGH,
                        impact="Exposed Kubernetes API endpoints can lead to cluster compromise and data theft",
                        likelihood="medium",
                        risk_score=8.5,
                        references=[
                            "https://owasp.org/www-community/attacks/Kubernetes_Misconfiguration",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "endpoint": endpoint,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "exposed_k8s_api"
                        }
                    )
                    findings.append(finding)
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_k8s_dashboard(self, url: str) -> List[Finding]:
        """Test for Kubernetes dashboard."""
        findings = []
        
        for endpoint in self.dashboard_endpoints[:10]:  # Test first 10 endpoints
            try:
                test_url = f"{url.rstrip('/')}{endpoint}"
                
                response = await self.make_request(test_url)
                content = await response.text()
                
                # Check if Kubernetes dashboard is accessible
                if self._is_k8s_dashboard_accessible(content, response.status):
                    finding = self.create_finding(
                        url=url,
                        finding_type=FindingType.KUBERNETES_MISCONFIGURATION,
                        title=f"Exposed Kubernetes Dashboard - {endpoint}",
                        description=f"Kubernetes dashboard '{endpoint}' is accessible and may expose cluster information",
                        severity=FindingSeverity.HIGH,
                        impact="Exposed Kubernetes dashboard can lead to cluster compromise and data theft",
                        likelihood="medium",
                        risk_score=8.0,
                        references=[
                            "https://owasp.org/www-community/attacks/Kubernetes_Dashboard_Exposure",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "endpoint": endpoint,
                            "response_status": response.status,
                            "response_content": content[:500] if len(content) > 500 else content,
                            "vulnerability_type": "exposed_k8s_dashboard"
                        }
                    )
                    findings.append(finding)
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                continue  # Skip failed tests
        
        return findings
    
    async def _test_k8s_vulnerabilities(self, url: str) -> List[Finding]:
        """Test for Kubernetes vulnerabilities."""
        findings = []
        
        try:
            response = await self.make_request(url)
            content = await response.text()
            
            # Check for Kubernetes vulnerability patterns
            vuln_patterns = self._find_k8s_vulnerabilities(content)
            if vuln_patterns:
                finding = self.create_finding(
                    url=url,
                    finding_type=FindingType.KUBERNETES_MISCONFIGURATION,
                    title="Kubernetes Vulnerability Detected",
                    description=f"Kubernetes vulnerability patterns detected: {', '.join(vuln_patterns)}",
                    severity=FindingSeverity.MEDIUM,
                    impact="Kubernetes vulnerabilities can lead to cluster compromise and data theft",
                    likelihood="medium",
                    risk_score=7.0,
                    references=[
                        "https://owasp.org/www-community/attacks/Kubernetes_Vulnerabilities",
                        "https://cwe.mitre.org/data/definitions/200.html"
                    ],
                    raw_data={
                        "vulnerability_patterns": vuln_patterns,
                        "response_content": content[:500] if len(content) > 500 else content,
                        "vulnerability_type": "k8s_vulnerability"
                    }
                )
                findings.append(finding)
            
        except Exception as e:
            pass  # Skip failed tests
        
        return findings
    
    def _is_k8s_api_accessible(self, content: str, status_code: int) -> bool:
        """Check if Kubernetes API is accessible."""
        # Check status code
        if status_code != 200:
            return False
        
        # Check for Kubernetes API indicators
        k8s_indicators = [
            r'apiVersion',
            r'kind',
            r'metadata',
            r'spec',
            r'status',
            r'items',
            r'resourceVersion',
            r'selfLink',
            r'uid',
            r'creationTimestamp',
            r'deletionTimestamp',
            r'deletionGracePeriodSeconds',
            r'labels',
            r'annotations',
            r'ownerReferences',
            r'finalizers',
            r'managedFields',
            r'generateName',
            r'namespace',
            r'name',
            r'clusterName',
            r'initializers',
            r'generation',
            r'resourceVersion',
            r'uid',
            r'creationTimestamp',
            r'deletionTimestamp',
            r'deletionGracePeriodSeconds',
            r'labels',
            r'annotations',
            r'ownerReferences',
            r'finalizers',
            r'managedFields',
            r'generateName',
            r'namespace',
            r'name',
            r'clusterName',
            r'initializers',
            r'generation',
        ]
        
        for indicator in k8s_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        return False
    
    def _is_k8s_dashboard_accessible(self, content: str, status_code: int) -> bool:
        """Check if Kubernetes dashboard is accessible."""
        # Check status code
        if status_code != 200:
            return False
        
        # Check for Kubernetes dashboard indicators
        dashboard_indicators = [
            r'kubernetes.*dashboard',
            r'k8s.*dashboard',
            r'kube.*dashboard',
            r'dashboard',
            r'kubernetes',
            r'k8s',
            r'kube',
            r'pods',
            r'services',
            r'secrets',
            r'configmaps',
            r'nodes',
            r'persistentvolumes',
            r'persistentvolumeclaims',
            r'events',
            r'endpoints',
            r'limitranges',
            r'resourcequotas',
            r'serviceaccounts',
            r'componentstatuses',
        ]
        
        for indicator in dashboard_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        return False
    
    def _find_k8s_vulnerabilities(self, content: str) -> List[str]:
        """Find Kubernetes vulnerability patterns in content."""
        vuln_patterns = []
        
        for pattern in self.vulnerability_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            vuln_patterns.extend(matches)
        
        return list(set(vuln_patterns))  # Remove duplicates

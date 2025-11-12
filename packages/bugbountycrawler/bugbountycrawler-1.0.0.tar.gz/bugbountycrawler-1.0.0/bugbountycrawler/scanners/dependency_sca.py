"""Dependency / SCA (Software Composition Analysis) scanner for BugBountyCrawler."""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiohttp

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class DependencySCAScanner(BaseScanner):
    """Scanner for dependency vulnerabilities (SCA)."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize dependency/SCA scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "DependencySCAScanner"
        
        # Dependency file patterns
        self.dependency_files = {
            'npm': ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'pip': ['requirements.txt', 'Pipfile', 'Pipfile.lock', 'setup.py', 'pyproject.toml'],
            'maven': ['pom.xml'],
            'gradle': ['build.gradle', 'build.gradle.kts'],
            'composer': ['composer.json', 'composer.lock'],
            'nuget': ['packages.config', '*.csproj'],
            'ruby': ['Gemfile', 'Gemfile.lock'],
            'go': ['go.mod', 'go.sum'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
        }
        
        # Known vulnerable patterns
        self.vulnerable_packages = {
            'npm': {
                'lodash': {'<4.17.21': 'Prototype Pollution'},
                'express': {'<4.17.3': 'Open Redirect'},
                'axios': {'<0.21.1': 'SSRF'},
                'jquery': {'<3.5.0': 'XSS'},
                'moment': {'<2.29.2': 'ReDoS'},
                'minimist': {'<1.2.6': 'Prototype Pollution'},
                'ajv': {'<6.12.3': 'Prototype Pollution'},
                'yargs-parser': {'<18.1.3': 'Prototype Pollution'},
                'node-fetch': {'<2.6.7': 'Data Exposure'},
                'underscore': {'<1.13.1': 'Arbitrary Code Execution'},
            },
            'pip': {
                'django': {'<3.2.13': 'SQL Injection'},
                'flask': {'<2.0.3': 'Open Redirect'},
                'requests': {'<2.28.0': 'SSL Verification'},
                'urllib3': {'<1.26.5': 'HTTP Request Smuggling'},
                'pyyaml': {'<5.4': 'Arbitrary Code Execution'},
                'pillow': {'<9.0.1': 'Buffer Overflow'},
                'cryptography': {'<38.0.3': 'NULL Pointer Dereference'},
                'jinja2': {'<2.11.3': 'XSS'},
            },
            'maven': {
                'log4j-core': {'<2.17.1': 'Log4Shell RCE'},
                'spring-core': {'<5.3.18': 'Spring4Shell RCE'},
                'jackson-databind': {'<2.13.2.1': 'Remote Code Execution'},
                'commons-fileupload': {'<1.3.3': 'Arbitrary File Upload'},
                'commons-io': {'<2.7': 'Path Traversal'},
            }
        }
        
        # End-of-life packages
        self.eol_packages = {
            'npm': ['bower', 'grunt', 'gulp<4'],
            'pip': ['python2', 'django<3'],
            'maven': ['struts<2.5'],
        }
        
        # License risks
        self.risky_licenses = ['GPL', 'AGPL', 'SSPL', 'Commons Clause']
        
        # CVE database URLs (for real implementation, use NVD API)
        self.cve_apis = {
            'osv': 'https://api.osv.dev/v1/query',
            'snyk': 'https://snyk.io/api/v1',
        }
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL/repository for dependency vulnerabilities."""
        findings = []
        errors = []
        response_time = 0.0
        status_code = 0
        headers = {}
        content_length = 0
        
        try:
            # Try to detect dependency files in the URL
            dependency_findings = await self._scan_for_dependency_files(url)
            findings.extend(dependency_findings)
        
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
    
    async def scan_local_project(self, project_path: str) -> List[Finding]:
        """Scan local project for dependency vulnerabilities."""
        findings = []
        
        project_root = Path(project_path)
        
        if not project_root.exists():
            return findings
        
        # Scan for each ecosystem
        for ecosystem, file_patterns in self.dependency_files.items():
            for pattern in file_patterns:
                # Find all matching files
                for dep_file in project_root.rglob(pattern):
                    findings.extend(await self._analyze_dependency_file(
                        dep_file, ecosystem
                    ))
        
        return findings
    
    async def _scan_for_dependency_files(self, url: str) -> List[Finding]:
        """Scan for exposed dependency files."""
        findings = []
        
        # Common exposed dependency file locations
        common_paths = [
            '/package.json',
            '/package-lock.json',
            '/requirements.txt',
            '/Pipfile',
            '/pom.xml',
            '/composer.json',
            '/Gemfile',
            '/go.mod',
            '/Cargo.toml',
        ]
        
        for path in common_paths:
            try:
                test_url = url.rstrip('/') + path
                response = await self.make_request(test_url)
                
                if response.status == 200:
                    content = await response.text()
                    
                    # This is already a vulnerability (exposed dependency file)
                    finding = self.create_finding(
                        url=test_url,
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        title=f"Exposed Dependency File: {path}",
                        description=f"Dependency file {path} is publicly accessible, revealing package information",
                        severity=FindingSeverity.LOW,
                        impact="Exposed dependency files reveal package versions that can be targeted",
                        likelihood="high",
                        risk_score=4.0,
                        references=[
                            "https://owasp.org/www-community/vulnerabilities/Information_exposure_through_query_strings_in_url"
                        ],
                        raw_data={
                            "file_path": path,
                            "content": content[:500]
                        }
                    )
                    findings.append(finding)
                    
                    # Analyze the file for vulnerabilities
                    ecosystem = self._detect_ecosystem(path)
                    if ecosystem:
                        vuln_findings = await self._analyze_dependency_content(
                            test_url, content, ecosystem
                        )
                        findings.extend(vuln_findings)
                
                await asyncio.sleep(0.1)
                
            except Exception:
                continue
        
        return findings
    
    def _detect_ecosystem(self, filename: str) -> Optional[str]:
        """Detect ecosystem from filename."""
        for ecosystem, patterns in self.dependency_files.items():
            if any(pattern in filename for pattern in patterns):
                return ecosystem
        return None
    
    async def _analyze_dependency_file(self, file_path: Path, ecosystem: str) -> List[Finding]:
        """Analyze a dependency file for vulnerabilities."""
        findings = []
        
        try:
            content = file_path.read_text()
            findings.extend(await self._analyze_dependency_content(
                str(file_path), content, ecosystem
            ))
        except Exception:
            pass
        
        return findings
    
    async def _analyze_dependency_content(self, location: str, content: str, 
                                         ecosystem: str) -> List[Finding]:
        """Analyze dependency file content for vulnerabilities."""
        findings = []
        
        if ecosystem == 'npm':
            findings.extend(self._analyze_npm_dependencies(location, content))
        elif ecosystem == 'pip':
            findings.extend(self._analyze_pip_dependencies(location, content))
        elif ecosystem == 'maven':
            findings.extend(self._analyze_maven_dependencies(location, content))
        
        return findings
    
    def _analyze_npm_dependencies(self, location: str, content: str) -> List[Finding]:
        """Analyze npm dependencies."""
        findings = []
        
        try:
            if content.strip().startswith('{'):
                # JSON format (package.json or package-lock.json)
                data = json.loads(content)
                dependencies = {}
                
                if 'dependencies' in data:
                    dependencies.update(data['dependencies'])
                if 'devDependencies' in data:
                    dependencies.update(data['devDependencies'])
                
                for package_name, version in dependencies.items():
                    # Clean version string
                    version_clean = version.replace('^', '').replace('~', '').replace('>=', '').replace('<=', '')
                    
                    # Check for known vulnerabilities
                    if package_name in self.vulnerable_packages.get('npm', {}):
                        vuln_versions = self.vulnerable_packages['npm'][package_name]
                        
                        for vuln_version, vuln_desc in vuln_versions.items():
                            if self._is_vulnerable_version(version_clean, vuln_version):
                                finding = self.create_finding(
                                    url=location,
                                    finding_type=FindingType.VULNERABLE_DEPENDENCY,
                                    title=f"Vulnerable npm Package: {package_name}",
                                    description=f"Package {package_name}@{version} has known vulnerability: {vuln_desc}",
                                    severity=FindingSeverity.HIGH,
                                    impact=f"Vulnerable dependency can lead to: {vuln_desc}",
                                    likelihood="high",
                                    risk_score=8.0,
                                    references=[
                                        f"https://npmjs.com/package/{package_name}",
                                        "https://nvd.nist.gov/"
                                    ],
                                    raw_data={
                                        "package": package_name,
                                        "version": version,
                                        "vulnerability": vuln_desc,
                                        "ecosystem": "npm"
                                    }
                                )
                                findings.append(finding)
            
            else:
                # yarn.lock or pnpm-lock.yaml format
                # Simple pattern matching
                package_pattern = r'"?([a-z0-9-]+)@([0-9\.]+)"?'
                matches = re.findall(package_pattern, content)
                
                for package_name, version in matches:
                    if package_name in self.vulnerable_packages.get('npm', {}):
                        # Check vulnerability (simplified)
                        finding = self.create_finding(
                            url=location,
                            finding_type=FindingType.VULNERABLE_DEPENDENCY,
                            title=f"Potential Vulnerable npm Package: {package_name}",
                            description=f"Package {package_name}@{version} may have known vulnerabilities",
                            severity=FindingSeverity.MEDIUM,
                            impact="Vulnerable dependencies can introduce security risks",
                            likelihood="medium",
                            risk_score=6.0,
                            references=[
                                f"https://npmjs.com/package/{package_name}"
                            ],
                            raw_data={
                                "package": package_name,
                                "version": version,
                                "ecosystem": "npm"
                            }
                        )
                        findings.append(finding)
        
        except Exception:
            pass
        
        return findings
    
    def _analyze_pip_dependencies(self, location: str, content: str) -> List[Finding]:
        """Analyze pip dependencies."""
        findings = []
        
        try:
            # Parse requirements.txt format
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Extract package and version
                match = re.match(r'([a-zA-Z0-9-_]+)==([0-9\.]+)', line)
                if match:
                    package_name, version = match.groups()
                    
                    # Check for known vulnerabilities
                    if package_name.lower() in self.vulnerable_packages.get('pip', {}):
                        vuln_versions = self.vulnerable_packages['pip'][package_name.lower()]
                        
                        for vuln_version, vuln_desc in vuln_versions.items():
                            if self._is_vulnerable_version(version, vuln_version):
                                finding = self.create_finding(
                                    url=location,
                                    finding_type=FindingType.VULNERABLE_DEPENDENCY,
                                    title=f"Vulnerable pip Package: {package_name}",
                                    description=f"Package {package_name}=={version} has known vulnerability: {vuln_desc}",
                                    severity=FindingSeverity.HIGH,
                                    impact=f"Vulnerable dependency can lead to: {vuln_desc}",
                                    likelihood="high",
                                    risk_score=8.0,
                                    references=[
                                        f"https://pypi.org/project/{package_name}/",
                                        "https://nvd.nist.gov/"
                                    ],
                                    raw_data={
                                        "package": package_name,
                                        "version": version,
                                        "vulnerability": vuln_desc,
                                        "ecosystem": "pip"
                                    }
                                )
                                findings.append(finding)
        
        except Exception:
            pass
        
        return findings
    
    def _analyze_maven_dependencies(self, location: str, content: str) -> List[Finding]:
        """Analyze Maven dependencies."""
        findings = []
        
        try:
            # Parse pom.xml for dependencies
            dependency_pattern = r'<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>'
            matches = re.findall(dependency_pattern, content)
            
            for artifact_id, version in matches:
                # Check for known vulnerabilities
                if artifact_id in self.vulnerable_packages.get('maven', {}):
                    vuln_versions = self.vulnerable_packages['maven'][artifact_id]
                    
                    for vuln_version, vuln_desc in vuln_versions.items():
                        if self._is_vulnerable_version(version, vuln_version):
                            finding = self.create_finding(
                                url=location,
                                finding_type=FindingType.VULNERABLE_DEPENDENCY,
                                title=f"Vulnerable Maven Package: {artifact_id}",
                                description=f"Package {artifact_id}:{version} has known vulnerability: {vuln_desc}",
                                severity=FindingSeverity.CRITICAL,
                                impact=f"Vulnerable dependency can lead to: {vuln_desc}",
                                likelihood="high",
                                risk_score=9.0,
                                references=[
                                    f"https://mvnrepository.com/artifact/{artifact_id}",
                                    "https://nvd.nist.gov/"
                                ],
                                raw_data={
                                    "package": artifact_id,
                                    "version": version,
                                    "vulnerability": vuln_desc,
                                    "ecosystem": "maven"
                                }
                            )
                            findings.append(finding)
        
        except Exception:
            pass
        
        return findings
    
    def _is_vulnerable_version(self, installed_version: str, vulnerable_version: str) -> bool:
        """Check if installed version is vulnerable."""
        try:
            # Simple version comparison
            # vulnerable_version format: "<2.0.0" means versions less than 2.0.0 are vulnerable
            
            if vulnerable_version.startswith('<'):
                threshold = vulnerable_version[1:]
                return self._compare_versions(installed_version, threshold) < 0
            elif vulnerable_version.startswith('<='):
                threshold = vulnerable_version[2:]
                return self._compare_versions(installed_version, threshold) <= 0
            elif vulnerable_version.startswith('>'):
                threshold = vulnerable_version[1:]
                return self._compare_versions(installed_version, threshold) > 0
            elif vulnerable_version.startswith('>='):
                threshold = vulnerable_version[2:]
                return self._compare_versions(installed_version, threshold) >= 0
            else:
                return installed_version == vulnerable_version
        
        except Exception:
            return False
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings. Returns -1, 0, or 1."""
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            
            # Pad with zeros
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))
            
            for p1, p2 in zip(parts1, parts2):
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1
            
            return 0
        
        except Exception:
            return 0


"""SAST (Static Application Security Testing) scanner for BugBountyCrawler."""

import re
import asyncio
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import ast
import hashlib

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class SASTScanner(BaseScanner):
    """Scanner for static code analysis vulnerabilities."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize SAST scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "SASTScanner"
        
        # Dangerous functions by language
        self.dangerous_functions = {
            'python': {
                'eval': {
                    'patterns': [r'\beval\s*\(', r'\bexec\s*\('],
                    'severity': FindingSeverity.CRITICAL,
                    'description': 'Unsafe use of eval/exec allows arbitrary code execution',
                    'cwe': 'CWE-95'
                },
                'pickle': {
                    'patterns': [r'\bpickle\.loads\s*\(', r'\bunpickle\s*\('],
                    'severity': FindingSeverity.HIGH,
                    'description': 'Unsafe deserialization can lead to remote code execution',
                    'cwe': 'CWE-502'
                },
                'yaml_unsafe': {
                    'patterns': [r'yaml\.load\s*\((?!.*Loader\s*=)', r'yaml\.unsafe_load'],
                    'severity': FindingSeverity.HIGH,
                    'description': 'Unsafe YAML loading can execute arbitrary code',
                    'cwe': 'CWE-502'
                },
                'sql_concatenation': {
                    'patterns': [
                        r'execute\s*\(\s*["\'].*%s.*["\']',
                        r'execute\s*\(\s*f["\'].*\{.*\}.*["\']',
                        r'execute\s*\(\s*["\'].*\+.*["\']'
                    ],
                    'severity': FindingSeverity.CRITICAL,
                    'description': 'SQL query concatenation leads to SQL injection',
                    'cwe': 'CWE-89'
                },
                'hardcoded_secrets': {
                    'patterns': [
                        r'password\s*=\s*["\'][^"\']{8,}["\']',
                        r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
                        r'secret\s*=\s*["\'][^"\']{20,}["\']',
                        r'token\s*=\s*["\'][^"\']{20,}["\']',
                    ],
                    'severity': FindingSeverity.HIGH,
                    'description': 'Hardcoded credentials found in source code',
                    'cwe': 'CWE-798'
                },
                'weak_random': {
                    'patterns': [r'\brandom\.random\s*\(', r'\brandom\.randint\s*\('],
                    'severity': FindingSeverity.MEDIUM,
                    'description': 'Insecure random number generator for security purposes',
                    'cwe': 'CWE-330'
                },
                'shell_injection': {
                    'patterns': [
                        r'os\.system\s*\(',
                        r'subprocess\.call\s*\(.*shell\s*=\s*True',
                        r'subprocess\.run\s*\(.*shell\s*=\s*True',
                        r'subprocess\.Popen\s*\(.*shell\s*=\s*True'
                    ],
                    'severity': FindingSeverity.CRITICAL,
                    'description': 'Shell injection via subprocess with shell=True',
                    'cwe': 'CWE-78'
                },
                'path_traversal': {
                    'patterns': [
                        r'open\s*\([^)]*\+[^)]*\)',
                        r'os\.path\.join\s*\([^)]*user[^)]*\)',
                    ],
                    'severity': FindingSeverity.HIGH,
                    'description': 'Potential path traversal in file operations',
                    'cwe': 'CWE-22'
                },
                'xxe': {
                    'patterns': [
                        r'etree\.parse\s*\(',
                        r'xml\.etree\.ElementTree\.parse\s*\(',
                        r'lxml\.etree\.parse\s*\(',
                    ],
                    'severity': FindingSeverity.HIGH,
                    'description': 'XML parsing without disabling external entities',
                    'cwe': 'CWE-611'
                },
            },
            'javascript': {
                'eval': {
                    'patterns': [r'\beval\s*\(', r'\bFunction\s*\(', r'setTimeout\s*\([^,]*,'],
                    'severity': FindingSeverity.HIGH,
                    'description': 'Unsafe use of eval/Function allows code injection',
                    'cwe': 'CWE-95'
                },
                'innerhtml': {
                    'patterns': [r'\.innerHTML\s*=', r'\.outerHTML\s*=', r'document\.write\s*\('],
                    'severity': FindingSeverity.MEDIUM,
                    'description': 'DOM manipulation via innerHTML can lead to XSS',
                    'cwe': 'CWE-79'
                },
                'hardcoded_keys': {
                    'patterns': [
                        r'apiKey\s*:\s*["\'][^"\']{20,}["\']',
                        r'api_key\s*:\s*["\'][^"\']{20,}["\']',
                        r'secret\s*:\s*["\'][^"\']{20,}["\']',
                    ],
                    'severity': FindingSeverity.HIGH,
                    'description': 'Hardcoded API keys or secrets in JavaScript',
                    'cwe': 'CWE-798'
                },
                'prototype_pollution': {
                    'patterns': [
                        r'\[.*\]\s*=',
                        r'Object\.assign\s*\(',
                        r'__proto__',
                    ],
                    'severity': FindingSeverity.MEDIUM,
                    'description': 'Potential prototype pollution vulnerability',
                    'cwe': 'CWE-1321'
                },
            },
            'java': {
                'sql_injection': {
                    'patterns': [
                        r'executeQuery\s*\([^)]*\+',
                        r'createQuery\s*\([^)]*\+',
                    ],
                    'severity': FindingSeverity.CRITICAL,
                    'description': 'SQL query concatenation leads to SQL injection',
                    'cwe': 'CWE-89'
                },
                'command_injection': {
                    'patterns': [
                        r'Runtime\.getRuntime\s*\(\)\.exec\s*\(',
                        r'ProcessBuilder\s*\(',
                    ],
                    'severity': FindingSeverity.CRITICAL,
                    'description': 'Command execution with user input',
                    'cwe': 'CWE-78'
                },
                'deserialization': {
                    'patterns': [
                        r'ObjectInputStream\s*\(',
                        r'readObject\s*\(',
                    ],
                    'severity': FindingSeverity.CRITICAL,
                    'description': 'Unsafe deserialization can lead to RCE',
                    'cwe': 'CWE-502'
                },
            }
        }
        
        # Crypto anti-patterns
        self.crypto_issues = {
            'weak_cipher': {
                'patterns': [
                    r'DES\(',
                    r'RC4\(',
                    r'MD5\(',
                    r'SHA1\(',
                    r'ECB',
                    r'algorithm\s*=\s*["\']DES["\']',
                    r'algorithm\s*=\s*["\']RC4["\']',
                ],
                'severity': FindingSeverity.HIGH,
                'description': 'Weak cryptographic algorithm in use',
                'cwe': 'CWE-327'
            },
            'hardcoded_key': {
                'patterns': [
                    r'key\s*=\s*b?["\'][A-Za-z0-9+/=]{32,}["\']',
                    r'iv\s*=\s*b?["\'][A-Za-z0-9+/=]{16,}["\']',
                ],
                'severity': FindingSeverity.CRITICAL,
                'description': 'Hardcoded cryptographic key or IV',
                'cwe': 'CWE-321'
            },
            'insecure_random': {
                'patterns': [
                    r'Math\.random\s*\(',
                    r'random\.random\s*\(',
                    r'new Random\s*\(',
                ],
                'severity': FindingSeverity.MEDIUM,
                'description': 'Insecure random number generator for security',
                'cwe': 'CWE-330'
            },
        }
        
        # Sensitive file patterns
        self.sensitive_files = {
            '.env', '.git/config', '.aws/credentials', 'id_rsa', 'id_dsa',
            '.ssh/id_rsa', '.ssh/id_dsa', 'config.json', 'secrets.json',
            'credentials.json', '.npmrc', '.pypirc', '.dockercfg', '.docker/config.json'
        }
        
        # Common vulnerability patterns
        self.vulnerability_patterns = {
            'debug_enabled': {
                'patterns': [
                    r'DEBUG\s*=\s*True',
                    r'debug:\s*true',
                    r'ENV\s*=\s*["\']development["\']',
                ],
                'severity': FindingSeverity.MEDIUM,
                'description': 'Debug mode enabled in configuration',
                'cwe': 'CWE-489'
            },
            'insecure_tls': {
                'patterns': [
                    r'verify\s*=\s*False',
                    r'ssl._create_unverified_context',
                    r'NODE_TLS_REJECT_UNAUTHORIZED.*0',
                ],
                'severity': FindingSeverity.HIGH,
                'description': 'TLS/SSL verification disabled',
                'cwe': 'CWE-295'
            },
            'mass_assignment': {
                'patterns': [
                    r'\.update\s*\(request\.',
                    r'\.save\s*\(request\.',
                    r'Object\.assign\s*\(.*request\.',
                ],
                'severity': FindingSeverity.MEDIUM,
                'description': 'Potential mass assignment vulnerability',
                'cwe': 'CWE-915'
            },
        }
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for exposed source code and perform SAST."""
        findings = []
        errors = []
        
        try:
            # Try to find exposed source code files
            source_findings = await self._scan_for_source_files(url)
            findings.extend(source_findings)
        
        except Exception as e:
            errors.append(str(e))
        
        return ScanResult(
            url=url,
            findings=findings,
            errors=errors
        )
    
    async def scan_local_code(self, project_path: str, 
                             languages: Optional[List[str]] = None) -> List[Finding]:
        """Scan local codebase for vulnerabilities."""
        findings = []
        
        project_root = Path(project_path)
        if not project_root.exists():
            return findings
        
        # Default to scanning all supported languages
        if not languages:
            languages = ['python', 'javascript', 'java']
        
        # File extensions by language
        extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'go': ['.go'],
        }
        
        # Scan files for each language
        for language in languages:
            if language not in extensions:
                continue
            
            for ext in extensions[language]:
                for code_file in project_root.rglob(f'*{ext}'):
                    # Skip common ignore directories
                    if any(ignore in str(code_file) for ignore in ['node_modules', 'venv', '.git', 'dist', 'build']):
                        continue
                    
                    file_findings = await self._analyze_code_file(code_file, language)
                    findings.extend(file_findings)
        
        return findings
    
    async def _scan_for_source_files(self, url: str) -> List[Finding]:
        """Scan for exposed source code files."""
        findings = []
        
        # Common exposed source files
        exposed_files = [
            '/.git/config',
            '/.git/HEAD',
            '/.env',
            '/config.json',
            '/secrets.json',
            '/.aws/credentials',
            '/.npmrc',
            '/id_rsa',
            '/id_rsa.pub',
            '/.ssh/id_rsa',
        ]
        
        for file_path in exposed_files:
            try:
                test_url = url.rstrip('/') + file_path
                response = await self.make_request(test_url)
                
                if response.status == 200:
                    content = await response.text()
                    
                    finding = self.create_finding(
                        url=test_url,
                        finding_type=FindingType.INFORMATION_DISCLOSURE,
                        title=f"Exposed Sensitive File: {file_path}",
                        description=f"Sensitive file {file_path} is publicly accessible",
                        severity=FindingSeverity.CRITICAL,
                        impact="Exposed sensitive files can reveal credentials, keys, and system configuration",
                        likelihood="high",
                        risk_score=9.0,
                        references=[
                            "https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure",
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        raw_data={
                            "file_path": file_path,
                            "content_preview": content[:200]
                        }
                    )
                    findings.append(finding)
                
                await asyncio.sleep(0.1)
                
            except Exception:
                continue
        
        return findings
    
    async def _analyze_code_file(self, file_path: Path, language: str) -> List[Finding]:
        """Analyze a single code file for vulnerabilities."""
        findings = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Scan for dangerous functions
            if language in self.dangerous_functions:
                for func_name, func_info in self.dangerous_functions[language].items():
                    for pattern in func_info['patterns']:
                        matches = list(re.finditer(pattern, content, re.MULTILINE))
                        
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            
                            finding = self.create_finding(
                                url=str(file_path),
                                finding_type=FindingType.CODE_VULNERABILITY,
                                title=f"Unsafe {func_name.replace('_', ' ').title()} - {language.title()}",
                                description=f"{func_info['description']} at line {line_num}",
                                severity=func_info['severity'],
                                impact=func_info['description'],
                                likelihood="high",
                                risk_score=self._severity_to_score(func_info['severity']),
                                references=[
                                    f"https://cwe.mitre.org/data/definitions/{func_info['cwe'].split('-')[1]}.html"
                                ],
                                raw_data={
                                    "file_path": str(file_path),
                                    "line_number": line_num,
                                    "code_snippet": self._get_code_context(content, match.start()),
                                    "pattern": pattern,
                                    "language": language,
                                    "cwe": func_info['cwe']
                                }
                            )
                            findings.append(finding)
            
            # Scan for crypto issues
            for issue_name, issue_info in self.crypto_issues.items():
                for pattern in issue_info['patterns']:
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        finding = self.create_finding(
                            url=str(file_path),
                            finding_type=FindingType.CRYPTOGRAPHIC_FAILURE,
                            title=f"Cryptographic Issue: {issue_name.replace('_', ' ').title()}",
                            description=f"{issue_info['description']} at line {line_num}",
                            severity=issue_info['severity'],
                            impact=issue_info['description'],
                            likelihood="medium",
                            risk_score=self._severity_to_score(issue_info['severity']),
                            references=[
                                f"https://cwe.mitre.org/data/definitions/{issue_info['cwe'].split('-')[1]}.html"
                            ],
                            raw_data={
                                "file_path": str(file_path),
                                "line_number": line_num,
                                "code_snippet": self._get_code_context(content, match.start()),
                                "pattern": pattern,
                                "language": language,
                                "cwe": issue_info['cwe']
                            }
                        )
                        findings.append(finding)
            
            # Scan for generic vulnerability patterns
            for vuln_name, vuln_info in self.vulnerability_patterns.items():
                for pattern in vuln_info['patterns']:
                    matches = list(re.finditer(pattern, content, re.MULTILINE))
                    
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        finding = self.create_finding(
                            url=str(file_path),
                            finding_type=FindingType.CONFIGURATION_ISSUE,
                            title=f"Configuration Issue: {vuln_name.replace('_', ' ').title()}",
                            description=f"{vuln_info['description']} at line {line_num}",
                            severity=vuln_info['severity'],
                            impact=vuln_info['description'],
                            likelihood="medium",
                            risk_score=self._severity_to_score(vuln_info['severity']),
                            references=[
                                f"https://cwe.mitre.org/data/definitions/{vuln_info['cwe'].split('-')[1]}.html"
                            ],
                            raw_data={
                                "file_path": str(file_path),
                                "line_number": line_num,
                                "code_snippet": self._get_code_context(content, match.start()),
                                "pattern": pattern,
                                "cwe": vuln_info['cwe']
                            }
                        )
                        findings.append(finding)
            
            # Python-specific AST analysis
            if language == 'python':
                ast_findings = await self._analyze_python_ast(file_path, content)
                findings.extend(ast_findings)
        
        except Exception as e:
            # Skip files that can't be read
            pass
        
        return findings
    
    async def _analyze_python_ast(self, file_path: Path, content: str) -> List[Finding]:
        """Analyze Python code using AST (Abstract Syntax Tree)."""
        findings = []
        
        try:
            tree = ast.parse(content)
            
            # Detect dangerous function calls
            for node in ast.walk(tree):
                # Check for eval/exec
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', '__import__']:
                            line_num = node.lineno
                            
                            finding = self.create_finding(
                                url=str(file_path),
                                finding_type=FindingType.CODE_VULNERABILITY,
                                title=f"Dangerous Function Call: {node.func.id}",
                                description=f"Use of {node.func.id}() at line {line_num} can execute arbitrary code",
                                severity=FindingSeverity.CRITICAL,
                                impact="Arbitrary code execution vulnerability",
                                likelihood="high",
                                risk_score=9.0,
                                references=[
                                    "https://cwe.mitre.org/data/definitions/95.html"
                                ],
                                raw_data={
                                    "file_path": str(file_path),
                                    "line_number": line_num,
                                    "function_name": node.func.id,
                                    "analysis_method": "AST"
                                }
                            )
                            findings.append(finding)
                
                # Check for hardcoded strings (potential secrets)
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id.lower()
                            if any(secret_kw in var_name for secret_kw in ['password', 'secret', 'key', 'token', 'api']):
                                if isinstance(node.value, ast.Str):
                                    if len(node.value.s) >= 8:
                                        finding = self.create_finding(
                                            url=str(file_path),
                                            finding_type=FindingType.SECRET_EXPOSURE,
                                            title=f"Hardcoded Secret: {target.id}",
                                            description=f"Variable '{target.id}' contains hardcoded secret at line {node.lineno}",
                                            severity=FindingSeverity.HIGH,
                                            impact="Hardcoded secrets can be extracted from source code",
                                            likelihood="high",
                                            risk_score=8.0,
                                            references=[
                                                "https://cwe.mitre.org/data/definitions/798.html"
                                            ],
                                            raw_data={
                                                "file_path": str(file_path),
                                                "line_number": node.lineno,
                                                "variable_name": target.id,
                                                "secret_length": len(node.value.s)
                                            }
                                        )
                                        findings.append(finding)
        
        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception:
            pass
        
        return findings
    
    def _get_code_context(self, content: str, position: int, context_lines: int = 3) -> str:
        """Get code context around a position."""
        lines = content.split('\n')
        line_num = content[:position].count('\n')
        
        start = max(0, line_num - context_lines)
        end = min(len(lines), line_num + context_lines + 1)
        
        context = '\n'.join(lines[start:end])
        return context[:300]  # Limit to 300 chars
    
    def _severity_to_score(self, severity: FindingSeverity) -> float:
        """Convert severity to risk score."""
        mapping = {
            FindingSeverity.CRITICAL: 9.0,
            FindingSeverity.HIGH: 7.5,
            FindingSeverity.MEDIUM: 5.0,
            FindingSeverity.LOW: 3.0,
            FindingSeverity.INFO: 1.0,
        }
        return mapping.get(severity, 5.0)


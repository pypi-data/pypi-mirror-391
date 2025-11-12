"""Mobile Security scanner for BugBountyCrawler."""

import re
import asyncio
import zipfile
import tempfile
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
import xml.etree.ElementTree as ET

from .base import BaseScanner, ScanResult
from ..models.finding import Finding, FindingSeverity, FindingType


class MobileSecurityScanner(BaseScanner):
    """Scanner for mobile application security issues."""
    
    def __init__(self, settings, rate_limiter=None):
        """Initialize mobile security scanner."""
        super().__init__(settings, rate_limiter)
        self.name = "MobileSecurityScanner"
        
        # Android manifest security checks
        self.android_permissions = {
            'dangerous': [
                'READ_CONTACTS', 'WRITE_CONTACTS', 'GET_ACCOUNTS',
                'READ_CALL_LOG', 'WRITE_CALL_LOG', 'READ_PHONE_STATE',
                'CALL_PHONE', 'READ_SMS', 'SEND_SMS', 'RECEIVE_SMS',
                'ACCESS_FINE_LOCATION', 'ACCESS_COARSE_LOCATION',
                'CAMERA', 'RECORD_AUDIO', 'READ_EXTERNAL_STORAGE',
                'WRITE_EXTERNAL_STORAGE', 'BODY_SENSORS'
            ],
            'signature': [
                'INSTALL_PACKAGES', 'DELETE_PACKAGES', 'CLEAR_APP_CACHE',
                'CLEAR_APP_USER_DATA', 'RESTART_PACKAGES', 'MOUNT_UNMOUNT_FILESYSTEMS'
            ]
        }
        
        # Insecure storage patterns
        self.insecure_storage_patterns = {
            'android': [
                r'MODE_WORLD_READABLE',
                r'MODE_WORLD_WRITABLE',
                r'getSharedPreferences\s*\([^)]*MODE_WORLD',
                r'openFileOutput\s*\([^)]*MODE_WORLD',
                r'SQLiteDatabase\.openOrCreateDatabase\s*\([^)]*WORLD',
                r'setReadable\s*\(\s*true\s*,\s*true\s*\)',
                r'setWritable\s*\(\s*true\s*,\s*true\s*\)',
            ],
            'ios': [
                r'kSecAttrAccessibleAlways',
                r'NSFileProtectionNone',
                r'UserDefaults.*\.set',
                r'NSCoding',
                r'NSKeyedArchiver',
            ]
        }
        
        # Hardcoded secrets patterns (mobile-specific)
        self.mobile_secret_patterns = [
            r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
            r'client[_-]?secret\s*=\s*["\'][^"\']{20,}["\']',
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'token\s*=\s*["\'][^"\']{20,}["\']',
            r'aws[_-]?access[_-]?key\s*=\s*["\']AKIA[A-Z0-9]{16}["\']',
            r'private[_-]?key\s*=\s*["\'][^"\']{40,}["\']',
        ]
        
        # Certificate pinning checks
        self.cert_pinning_patterns = {
            'android': [
                r'CertificatePinner',
                r'TrustManager',
                r'SSLSocketFactory',
                r'HostnameVerifier',
                r'network_security_config',
            ],
            'ios': [
                r'NSURLSessionConfiguration',
                r'URLSessionDelegate',
                r'didReceiveChallenge',
                r'SecTrustEvaluate',
                r'kSecTrustResultProceed',
            ]
        }
        
        # Insecure communication patterns
        self.insecure_comm_patterns = {
            'android': [
                r'http://(?!localhost)',
                r'usesCleartextTraffic\s*=\s*"true"',
                r'android:usesCleartextTraffic="true"',
                r'ALLOW_ALL_HOSTNAME_VERIFIER',
            ],
            'ios': [
                r'NSAllowsArbitraryLoads.*true',
                r'NSExceptionAllowsInsecureHTTPLoads.*true',
                r'http://(?!localhost)',
            ]
        }
        
        # WebView security issues
        self.webview_patterns = {
            'android': [
                r'setJavaScriptEnabled\s*\(\s*true\s*\)',
                r'setAllowFileAccess\s*\(\s*true\s*\)',
                r'setAllowFileAccessFromFileURLs\s*\(\s*true\s*\)',
                r'setAllowUniversalAccessFromFileURLs\s*\(\s*true\s*\)',
                r'addJavascriptInterface\s*\(',
            ],
            'ios': [
                r'allowFileAccessFromFileURLs\s*=\s*true',
                r'allowUniversalAccessFromFileURLs\s*=\s*true',
            ]
        }
        
        # Debuggable/development build indicators
        self.debug_indicators = {
            'android': [
                r'android:debuggable\s*=\s*"true"',
                r'BuildConfig\.DEBUG\s*==\s*true',
                r'Log\.d\s*\(',
                r'Log\.v\s*\(',
                r'println\s*\(',
            ],
            'ios': [
                r'DEBUG\s*=\s*1',
                r'ENABLE_TESTABILITY\s*=\s*YES',
                r'NSLog\s*\(@',
            ]
        }
    
    async def scan_url(self, url: str) -> ScanResult:
        """Scan URL for mobile app downloads."""
        findings = []
        errors = []
        
        try:
            # Check for APK/IPA downloads
            if url.endswith('.apk'):
                findings.extend(await self._scan_android_apk_url(url))
            elif url.endswith('.ipa'):
                findings.extend(await self._scan_ios_ipa_url(url))
        
        except Exception as e:
            errors.append(str(e))
        
        return ScanResult(
            url=url,
            findings=findings,
            errors=errors
        )
    
    async def scan_apk_file(self, apk_path: str) -> List[Finding]:
        """Scan Android APK file for security issues."""
        findings = []
        apk_file = Path(apk_path)
        
        if not apk_file.exists():
            return findings
        
        temp_dir = None
        
        try:
            # Extract APK
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(apk_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            temp_path = Path(temp_dir)
            
            # Analyze AndroidManifest.xml
            manifest_findings = await self._analyze_android_manifest(temp_path)
            findings.extend(manifest_findings)
            
            # Scan for insecure storage
            storage_findings = await self._scan_android_storage(temp_path)
            findings.extend(storage_findings)
            
            # Scan for hardcoded secrets
            secret_findings = await self._scan_android_secrets(temp_path)
            findings.extend(secret_findings)
            
            # Check certificate pinning
            pinning_findings = await self._check_android_cert_pinning(temp_path)
            findings.extend(pinning_findings)
            
            # Check WebView security
            webview_findings = await self._check_android_webview(temp_path)
            findings.extend(webview_findings)
            
            # Check for debug/development build
            debug_findings = await self._check_android_debug(temp_path)
            findings.extend(debug_findings)
        
        except Exception as e:
            pass
        
        finally:
            # Cleanup
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        return findings
    
    async def scan_ipa_file(self, ipa_path: str) -> List[Finding]:
        """Scan iOS IPA file for security issues."""
        findings = []
        ipa_file = Path(ipa_path)
        
        if not ipa_file.exists():
            return findings
        
        temp_dir = None
        
        try:
            # Extract IPA
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(ipa_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            temp_path = Path(temp_dir)
            
            # Analyze Info.plist
            plist_findings = await self._analyze_ios_plist(temp_path)
            findings.extend(plist_findings)
            
            # Scan for insecure storage
            storage_findings = await self._scan_ios_storage(temp_path)
            findings.extend(storage_findings)
            
            # Scan for hardcoded secrets
            secret_findings = await self._scan_ios_secrets(temp_path)
            findings.extend(secret_findings)
            
            # Check certificate pinning
            pinning_findings = await self._check_ios_cert_pinning(temp_path)
            findings.extend(pinning_findings)
        
        except Exception as e:
            pass
        
        finally:
            # Cleanup
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        return findings
    
    async def _analyze_android_manifest(self, apk_dir: Path) -> List[Finding]:
        """Analyze AndroidManifest.xml for security issues."""
        findings = []
        
        manifest_path = apk_dir / 'AndroidManifest.xml'
        if not manifest_path.exists():
            return findings
        
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            
            # Check for debuggable flag
            application = root.find('application')
            if application is not None:
                debuggable = application.get('{http://schemas.android.com/apk/res/android}debuggable')
                if debuggable == 'true':
                    finding = self.create_finding(
                        url=str(manifest_path),
                        finding_type=FindingType.MOBILE_SECURITY,
                        title="Android App is Debuggable",
                        description="Application has android:debuggable=true, allowing debugging in production",
                        severity=FindingSeverity.HIGH,
                        impact="Debuggable apps can be reverse engineered and tampered with",
                        likelihood="high",
                        risk_score=7.5,
                        references=[
                            "https://developer.android.com/guide/topics/manifest/application-element#debug"
                        ],
                        raw_data={
                            "manifest_file": str(manifest_path),
                            "debuggable": "true"
                        }
                    )
                    findings.append(finding)
                
                # Check for backup allowed
                backup_allowed = application.get('{http://schemas.android.com/apk/res/android}allowBackup')
                if backup_allowed == 'true':
                    finding = self.create_finding(
                        url=str(manifest_path),
                        finding_type=FindingType.MOBILE_SECURITY,
                        title="Android Backup Enabled",
                        description="Application allows backup via adb, potentially exposing sensitive data",
                        severity=FindingSeverity.MEDIUM,
                        impact="App data can be extracted via ADB backup",
                        likelihood="medium",
                        risk_score=6.0,
                        references=[
                            "https://developer.android.com/guide/topics/manifest/application-element#allowbackup"
                        ],
                        raw_data={
                            "manifest_file": str(manifest_path),
                            "allowBackup": "true"
                        }
                    )
                    findings.append(finding)
            
            # Check for dangerous permissions
            for permission in root.findall('.//uses-permission'):
                perm_name = permission.get('{http://schemas.android.com/apk/res/android}name', '')
                perm_short = perm_name.split('.')[-1] if '.' in perm_name else perm_name
                
                if perm_short in self.android_permissions['dangerous']:
                    finding = self.create_finding(
                        url=str(manifest_path),
                        finding_type=FindingType.MOBILE_SECURITY,
                        title=f"Dangerous Android Permission: {perm_short}",
                        description=f"App requests dangerous permission: {perm_name}",
                        severity=FindingSeverity.LOW,
                        impact=f"Permission {perm_short} may access sensitive user data",
                        likelihood="medium",
                        risk_score=4.0,
                        references=[
                            "https://developer.android.com/guide/topics/permissions/overview"
                        ],
                        raw_data={
                            "permission": perm_name,
                            "permission_type": "dangerous"
                        }
                    )
                    findings.append(finding)
        
        except Exception:
            pass
        
        return findings
    
    async def _scan_android_storage(self, apk_dir: Path) -> List[Finding]:
        """Scan for insecure storage in Android app."""
        findings = []
        
        # Scan all Java/Kotlin files
        for code_file in apk_dir.rglob('*.smali'):
            try:
                content = code_file.read_text(errors='ignore')
                
                for pattern in self.insecure_storage_patterns['android']:
                    if re.search(pattern, content, re.IGNORECASE):
                        finding = self.create_finding(
                            url=str(code_file),
                            finding_type=FindingType.MOBILE_SECURITY,
                            title="Insecure Android Storage",
                            description=f"Insecure storage pattern found: {pattern}",
                            severity=FindingSeverity.HIGH,
                            impact="Data stored with world-readable/writable permissions can be accessed by other apps",
                            likelihood="high",
                            risk_score=8.0,
                            references=[
                                "https://owasp.org/www-project-mobile-top-10/2016-risks/m2-insecure-data-storage"
                            ],
                            raw_data={
                                "file": str(code_file),
                                "pattern": pattern,
                                "platform": "android"
                            }
                        )
                        findings.append(finding)
                        break  # Only report once per file
            
            except Exception:
                continue
        
        return findings
    
    async def _scan_android_secrets(self, apk_dir: Path) -> List[Finding]:
        """Scan for hardcoded secrets in Android app."""
        findings = []
        
        # Check strings.xml and other resources
        for xml_file in apk_dir.rglob('*.xml'):
            try:
                content = xml_file.read_text(errors='ignore')
                
                for pattern in self.mobile_secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        finding = self.create_finding(
                            url=str(xml_file),
                            finding_type=FindingType.SECRET_EXPOSURE,
                            title="Hardcoded Secret in Android Resources",
                            description=f"Hardcoded secret found in {xml_file.name}",
                            severity=FindingSeverity.CRITICAL,
                            impact="Hardcoded secrets can be extracted from APK and abused",
                            likelihood="high",
                            risk_score=9.0,
                            references=[
                                "https://owasp.org/www-project-mobile-top-10/2016-risks/m9-reverse-engineering"
                            ],
                            raw_data={
                                "file": str(xml_file),
                                "pattern": pattern,
                                "matched_text": match.group(0)[:50]
                            }
                        )
                        findings.append(finding)
                        break  # Only report once per file
            
            except Exception:
                continue
        
        return findings
    
    async def _check_android_cert_pinning(self, apk_dir: Path) -> List[Finding]:
        """Check for certificate pinning implementation."""
        findings = []
        
        has_pinning = False
        
        # Check for certificate pinning implementation
        for code_file in apk_dir.rglob('*.smali'):
            try:
                content = code_file.read_text(errors='ignore')
                
                for pattern in self.cert_pinning_patterns['android']:
                    if re.search(pattern, content, re.IGNORECASE):
                        has_pinning = True
                        break
                
                if has_pinning:
                    break
            
            except Exception:
                continue
        
        # Check network_security_config.xml
        network_config = apk_dir / 'res' / 'xml' / 'network_security_config.xml'
        if network_config.exists():
            has_pinning = True
        
        if not has_pinning:
            finding = self.create_finding(
                url=str(apk_dir),
                finding_type=FindingType.MOBILE_SECURITY,
                title="Missing Certificate Pinning (Android)",
                description="App does not implement certificate pinning",
                severity=FindingSeverity.MEDIUM,
                impact="Without certificate pinning, app is vulnerable to MITM attacks",
                likelihood="medium",
                risk_score=6.0,
                references=[
                    "https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"
                ],
                raw_data={
                    "platform": "android",
                    "cert_pinning": "not_found"
                }
            )
            findings.append(finding)
        
        return findings
    
    async def _check_android_webview(self, apk_dir: Path) -> List[Finding]:
        """Check for WebView security issues."""
        findings = []
        
        for code_file in apk_dir.rglob('*.smali'):
            try:
                content = code_file.read_text(errors='ignore')
                
                for pattern in self.webview_patterns['android']:
                    if re.search(pattern, content, re.IGNORECASE):
                        finding = self.create_finding(
                            url=str(code_file),
                            finding_type=FindingType.MOBILE_SECURITY,
                            title="Insecure WebView Configuration (Android)",
                            description=f"WebView has insecure configuration: {pattern}",
                            severity=FindingSeverity.HIGH,
                            impact="Insecure WebView can lead to JavaScript injection and file access",
                            likelihood="medium",
                            risk_score=7.0,
                            references=[
                                "https://owasp.org/www-project-mobile-top-10/2016-risks/m7-client-code-quality"
                            ],
                            raw_data={
                                "file": str(code_file),
                                "pattern": pattern,
                                "platform": "android"
                            }
                        )
                        findings.append(finding)
                        break  # Only report once per file
            
            except Exception:
                continue
        
        return findings
    
    async def _check_android_debug(self, apk_dir: Path) -> List[Finding]:
        """Check for debug/development build indicators."""
        findings = []
        
        for code_file in apk_dir.rglob('*.smali'):
            try:
                content = code_file.read_text(errors='ignore')
                
                # Count debug statements
                debug_count = sum(
                    len(re.findall(pattern, content, re.IGNORECASE))
                    for pattern in self.debug_indicators['android']
                )
                
                if debug_count > 10:  # Threshold for excessive logging
                    finding = self.create_finding(
                        url=str(code_file),
                        finding_type=FindingType.MOBILE_SECURITY,
                        title="Excessive Debug Logging (Android)",
                        description=f"Found {debug_count} debug logging statements",
                        severity=FindingSeverity.LOW,
                        impact="Debug logging can leak sensitive information in production",
                        likelihood="low",
                        risk_score=3.0,
                        references=[
                            "https://owasp.org/www-project-mobile-top-10/2016-risks/m7-client-code-quality"
                        ],
                        raw_data={
                            "file": str(code_file),
                            "debug_count": debug_count,
                            "platform": "android"
                        }
                    )
                    findings.append(finding)
                    break  # Only report once
            
            except Exception:
                continue
        
        return findings
    
    async def _scan_android_apk_url(self, url: str) -> List[Finding]:
        """Scan Android APK from URL."""
        findings = []
        
        try:
            # Download APK
            response = await self.make_request(url)
            
            if response.status == 200:
                # Save to temp file and scan
                with tempfile.NamedTemporaryFile(suffix='.apk', delete=False) as temp_file:
                    content = await response.read()
                    temp_file.write(content)
                    temp_file.flush()
                    
                    # Scan the APK
                    findings = await self.scan_apk_file(temp_file.name)
                    
                    # Cleanup
                    Path(temp_file.name).unlink(missing_ok=True)
        
        except Exception:
            pass
        
        return findings
    
    async def _scan_ios_ipa_url(self, url: str) -> List[Finding]:
        """Scan iOS IPA from URL."""
        findings = []
        
        try:
            response = await self.make_request(url)
            
            if response.status == 200:
                with tempfile.NamedTemporaryFile(suffix='.ipa', delete=False) as temp_file:
                    content = await response.read()
                    temp_file.write(content)
                    temp_file.flush()
                    
                    findings = await self.scan_ipa_file(temp_file.name)
                    
                    Path(temp_file.name).unlink(missing_ok=True)
        
        except Exception:
            pass
        
        return findings
    
    async def _analyze_ios_plist(self, ipa_dir: Path) -> List[Finding]:
        """Analyze iOS Info.plist for security issues."""
        findings = []
        
        # Find Info.plist
        plist_files = list(ipa_dir.rglob('Info.plist'))
        
        for plist_file in plist_files:
            try:
                content = plist_file.read_text(errors='ignore')
                
                # Check for insecure ATS settings
                if re.search(r'NSAllowsArbitraryLoads.*<true/>', content, re.IGNORECASE):
                    finding = self.create_finding(
                        url=str(plist_file),
                        finding_type=FindingType.MOBILE_SECURITY,
                        title="iOS App Transport Security Disabled",
                        description="NSAllowsArbitraryLoads is enabled, disabling ATS protection",
                        severity=FindingSeverity.HIGH,
                        impact="Disabling ATS allows insecure HTTP connections",
                        likelihood="high",
                        risk_score=7.5,
                        references=[
                            "https://developer.apple.com/documentation/security/preventing_insecure_network_connections"
                        ],
                        raw_data={
                            "plist_file": str(plist_file),
                            "platform": "ios"
                        }
                    )
                    findings.append(finding)
            
            except Exception:
                continue
        
        return findings
    
    async def _scan_ios_storage(self, ipa_dir: Path) -> List[Finding]:
        """Scan for insecure storage in iOS app."""
        findings = []
        
        # Scan Objective-C/Swift files (if available)
        for code_file in list(ipa_dir.rglob('*.m')) + list(ipa_dir.rglob('*.swift')):
            try:
                content = code_file.read_text(errors='ignore')
                
                for pattern in self.insecure_storage_patterns['ios']:
                    if re.search(pattern, content, re.IGNORECASE):
                        finding = self.create_finding(
                            url=str(code_file),
                            finding_type=FindingType.MOBILE_SECURITY,
                            title="Insecure iOS Storage",
                            description=f"Insecure storage pattern found: {pattern}",
                            severity=FindingSeverity.HIGH,
                            impact="Data stored insecurely can be accessed even when device is locked",
                            likelihood="medium",
                            risk_score=7.0,
                            references=[
                                "https://owasp.org/www-project-mobile-top-10/2016-risks/m2-insecure-data-storage"
                            ],
                            raw_data={
                                "file": str(code_file),
                                "pattern": pattern,
                                "platform": "ios"
                            }
                        )
                        findings.append(finding)
                        break
            
            except Exception:
                continue
        
        return findings
    
    async def _scan_ios_secrets(self, ipa_dir: Path) -> List[Finding]:
        """Scan for hardcoded secrets in iOS app."""
        findings = []
        
        for code_file in list(ipa_dir.rglob('*.m')) + list(ipa_dir.rglob('*.swift')) + list(ipa_dir.rglob('*.plist')):
            try:
                content = code_file.read_text(errors='ignore')
                
                for pattern in self.mobile_secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        finding = self.create_finding(
                            url=str(code_file),
                            finding_type=FindingType.SECRET_EXPOSURE,
                            title="Hardcoded Secret in iOS App",
                            description=f"Hardcoded secret found in {code_file.name}",
                            severity=FindingSeverity.CRITICAL,
                            impact="Hardcoded secrets can be extracted via reverse engineering",
                            likelihood="high",
                            risk_score=9.0,
                            references=[
                                "https://owasp.org/www-project-mobile-top-10/2016-risks/m9-reverse-engineering"
                            ],
                            raw_data={
                                "file": str(code_file),
                                "pattern": pattern,
                                "matched_text": match.group(0)[:50],
                                "platform": "ios"
                            }
                        )
                        findings.append(finding)
                        break
            
            except Exception:
                continue
        
        return findings
    
    async def _check_ios_cert_pinning(self, ipa_dir: Path) -> List[Finding]:
        """Check for certificate pinning in iOS app."""
        findings = []
        
        has_pinning = False
        
        for code_file in list(ipa_dir.rglob('*.m')) + list(ipa_dir.rglob('*.swift')):
            try:
                content = code_file.read_text(errors='ignore')
                
                for pattern in self.cert_pinning_patterns['ios']:
                    if re.search(pattern, content, re.IGNORECASE):
                        has_pinning = True
                        break
                
                if has_pinning:
                    break
            
            except Exception:
                continue
        
        if not has_pinning:
            finding = self.create_finding(
                url=str(ipa_dir),
                finding_type=FindingType.MOBILE_SECURITY,
                title="Missing Certificate Pinning (iOS)",
                description="App does not implement certificate pinning",
                severity=FindingSeverity.MEDIUM,
                impact="Without certificate pinning, app is vulnerable to MITM attacks",
                likelihood="medium",
                risk_score=6.0,
                references=[
                    "https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"
                ],
                raw_data={
                    "platform": "ios",
                    "cert_pinning": "not_found"
                }
            )
            findings.append(finding)
        
        return findings


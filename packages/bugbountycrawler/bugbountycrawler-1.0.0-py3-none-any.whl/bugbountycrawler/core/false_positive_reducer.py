"""False Positive Reduction engine for BugBountyCrawler."""

import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

from ..models.finding import Finding, FindingSeverity, FindingType


class FalsePositiveReducer:
    """Advanced false positive reduction with multi-evidence confirmation."""
    
    def __init__(self, settings=None):
        """Initialize false positive reducer."""
        self.settings = settings
        
        # Confidence scoring weights
        self.evidence_weights = {
            'response_diff': 0.25,      # Different from baseline
            'error_pattern': 0.30,      # Matches error pattern
            'timing_anomaly': 0.20,     # Timing difference
            'multiple_payloads': 0.15,  # Multiple payloads succeed
            'context_validation': 0.10, # Context makes sense
        }
        
        # Known false positive patterns
        self.false_positive_patterns = {
            FindingType.SQL_INJECTION: [
                r'syntax error.*expected',  # Generic JS/Python errors
                r'ReferenceError',
                r'TypeError',
                r'SyntaxError',
            ],
            FindingType.XSS: [
                r'angular\.js',  # Framework artifacts
                r'react\.js',
                r'vue\.js',
                r'<!-- .* -->',  # HTML comments
            ],
            FindingType.COMMAND_INJECTION: [
                r'No such file or directory',  # Legitimate errors
                r'Permission denied',
            ],
        }
        
        # Deduplication cache
        self.finding_cache = {}
        self.cache_ttl = timedelta(hours=24)
        
        # Verification retry settings
        self.retry_attempts = 3
        self.retry_delay = 1.0  # seconds
    
    async def reduce_false_positives(self, findings: List[Finding]) -> List[Finding]:
        """Apply comprehensive false positive reduction."""
        if not findings:
            return findings
        
        validated_findings = []
        
        for finding in findings:
            # Step 1: Deduplicate
            if self._is_duplicate(finding):
                continue
            
            # Step 2: Multi-evidence confirmation
            confidence_score = await self._calculate_confidence_score(finding)
            finding.confidence = self._score_to_confidence(confidence_score)
            
            # Step 3: Pattern-based filtering
            if self._matches_false_positive_pattern(finding):
                finding.status = "false_positive"
                finding.confidence = "low"
                continue
            
            # Step 4: Context validation
            if not self._validate_context(finding):
                finding.confidence = "low"
            
            # Step 5: Auto-retry verification
            if finding.confidence == "low" and confidence_score > 0.3:
                retry_result = await self._retry_verification(finding)
                if retry_result:
                    finding.confidence = "medium"
            
            validated_findings.append(finding)
        
        # Step 6: Prioritize by confidence
        validated_findings.sort(key=lambda f: (
            self._severity_to_priority(f.severity),
            self._confidence_to_priority(f.confidence),
            f.risk_score
        ), reverse=True)
        
        return validated_findings
    
    def _is_duplicate(self, finding: Finding) -> bool:
        """Check if finding is a duplicate."""
        # Create canonical fingerprint
        fingerprint = self._create_fingerprint(finding)
        
        # Check cache
        if fingerprint in self.finding_cache:
            cached_time = self.finding_cache[fingerprint]
            if datetime.utcnow() - cached_time < self.cache_ttl:
                return True
        
        # Add to cache
        self.finding_cache[fingerprint] = datetime.utcnow()
        return False
    
    def _create_fingerprint(self, finding: Finding) -> str:
        """Create unique fingerprint for finding."""
        # Normalize URL (remove query string variations)
        normalized_url = self._normalize_url(finding.url)
        
        # Create fingerprint components
        components = [
            str(finding.finding_type),
            normalized_url,
            finding.parameter or "",
            finding.method,
        ]
        
        # Hash to create fingerprint
        fingerprint_str = "|".join(components)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(url)
        
        # Keep only scheme, netloc, and path
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        return normalized
    
    async def _calculate_confidence_score(self, finding: Finding) -> float:
        """Calculate confidence score using multiple evidence factors."""
        scores = []
        
        raw_data = finding.raw_data or {}
        
        # Evidence 1: Response difference
        if 'response_content' in raw_data and 'baseline_content' in raw_data:
            diff_score = self._calculate_response_diff_score(
                raw_data['response_content'],
                raw_data.get('baseline_content', '')
            )
            scores.append(('response_diff', diff_score))
        
        # Evidence 2: Error pattern match
        if 'error_pattern' in raw_data or 'indicator' in raw_data:
            scores.append(('error_pattern', 1.0))
        
        # Evidence 3: Timing anomaly
        if 'response_time' in raw_data:
            timing_score = self._calculate_timing_score(
                raw_data['response_time'],
                raw_data.get('threshold', 5.0)
            )
            scores.append(('timing_anomaly', timing_score))
        
        # Evidence 4: Multiple payload success
        if raw_data.get('injection_type') or raw_data.get('payload'):
            scores.append(('multiple_payloads', 0.8))
        
        # Evidence 5: Context validation
        context_score = self._validate_finding_context(finding)
        scores.append(('context_validation', context_score))
        
        # Calculate weighted average
        total_score = 0.0
        for evidence_type, score in scores:
            weight = self.evidence_weights.get(evidence_type, 0.1)
            total_score += score * weight
        
        return min(total_score, 1.0)
    
    def _calculate_response_diff_score(self, response: str, baseline: str) -> float:
        """Calculate how different the response is from baseline."""
        if not baseline:
            return 0.5
        
        response_len = len(response)
        baseline_len = len(baseline)
        
        # Significant size difference
        if abs(response_len - baseline_len) > 100:
            return 1.0
        
        # Content similarity check (simple)
        if response == baseline:
            return 0.0
        
        # Partial similarity
        similarity = self._calculate_similarity(response[:500], baseline[:500])
        return 1.0 - similarity
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        if not str1 or not str2:
            return 0.0
        
        # Simple character-based similarity
        common_chars = sum(1 for c in str1 if c in str2)
        total_chars = max(len(str1), len(str2))
        
        return common_chars / total_chars if total_chars > 0 else 0.0
    
    def _calculate_timing_score(self, response_time: float, threshold: float) -> float:
        """Calculate timing anomaly score."""
        if response_time < threshold:
            return 0.0
        
        # Score based on how much over threshold
        ratio = response_time / threshold
        return min(ratio - 1.0, 1.0)
    
    def _validate_finding_context(self, finding: Finding) -> float:
        """Validate if finding makes sense in context."""
        score = 0.5  # Default neutral score
        
        # Check if finding type matches URL context
        url_lower = finding.url.lower()
        
        # SQL Injection more likely in database-related endpoints
        if finding.finding_type == FindingType.SQL_INJECTION:
            if any(kw in url_lower for kw in ['search', 'query', 'user', 'profile', 'id=']):
                score += 0.3
        
        # XSS more likely in user-generated content
        elif finding.finding_type == FindingType.XSS:
            if any(kw in url_lower for kw in ['comment', 'post', 'message', 'review']):
                score += 0.3
        
        # Command injection in file/system operations
        elif finding.finding_type == FindingType.COMMAND_INJECTION:
            if any(kw in url_lower for kw in ['file', 'upload', 'download', 'exec', 'run']):
                score += 0.3
        
        # API endpoints for API-related findings
        if 'api' in url_lower or 'rest' in url_lower:
            if finding.finding_type in [
                FindingType.API_MISCONFIGURATION,
                FindingType.BROKEN_OBJECT_LEVEL_AUTHORIZATION,
                FindingType.MASS_ASSIGNMENT
            ]:
                score += 0.2
        
        return min(score, 1.0)
    
    def _matches_false_positive_pattern(self, finding: Finding) -> bool:
        """Check if finding matches known false positive patterns."""
        patterns = self.false_positive_patterns.get(finding.finding_type, [])
        
        if not patterns:
            return False
        
        # Check response content
        response_content = finding.raw_data.get('response_content', '')
        
        for pattern in patterns:
            if re.search(pattern, response_content, re.IGNORECASE):
                return True
        
        return False
    
    def _validate_context(self, finding: Finding) -> bool:
        """Validate if finding context is valid."""
        # Check severity matches risk score
        severity_scores = {
            FindingSeverity.CRITICAL: (8.5, 10.0),
            FindingSeverity.HIGH: (7.0, 8.9),
            FindingSeverity.MEDIUM: (4.0, 6.9),
            FindingSeverity.LOW: (1.0, 3.9),
            FindingSeverity.INFO: (0.0, 0.9),
        }
        
        expected_range = severity_scores.get(finding.severity)
        if expected_range:
            min_score, max_score = expected_range
            if not (min_score <= finding.risk_score <= max_score):
                return False
        
        # Check required fields are present
        if not finding.title or not finding.description:
            return False
        
        if not finding.url:
            return False
        
        return True
    
    async def _retry_verification(self, finding: Finding) -> bool:
        """Retry verification with altered payloads."""
        # This is a placeholder for actual retry logic
        # In production, you'd make actual HTTP requests with variations
        
        for attempt in range(self.retry_attempts):
            await asyncio.sleep(self.retry_delay)
            
            # Simulate retry (in production, make actual request)
            # If we get consistent results, increase confidence
            if attempt == self.retry_attempts - 1:
                return True
        
        return False
    
    def _score_to_confidence(self, score: float) -> str:
        """Convert numeric score to confidence level."""
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _confidence_to_priority(self, confidence: str) -> int:
        """Convert confidence to priority number."""
        mapping = {
            "high": 3,
            "medium": 2,
            "low": 1,
        }
        return mapping.get(confidence, 0)
    
    def _severity_to_priority(self, severity: FindingSeverity) -> int:
        """Convert severity to priority number."""
        mapping = {
            FindingSeverity.CRITICAL: 5,
            FindingSeverity.HIGH: 4,
            FindingSeverity.MEDIUM: 3,
            FindingSeverity.LOW: 2,
            FindingSeverity.INFO: 1,
        }
        return mapping.get(severity, 0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get false positive reduction statistics."""
        return {
            "cache_size": len(self.finding_cache),
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600,
            "retry_attempts": self.retry_attempts,
            "evidence_weights": self.evidence_weights,
        }
    
    def clear_cache(self):
        """Clear deduplication cache."""
        self.finding_cache.clear()
    
    def cleanup_old_cache_entries(self):
        """Remove expired cache entries."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, timestamp in self.finding_cache.items()
            if now - timestamp > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.finding_cache[key]


class FindingDeduplicator:
    """Deduplicate findings by canonical URL and parameter fingerprinting."""
    
    @staticmethod
    def deduplicate(findings: List[Finding]) -> List[Finding]:
        """Remove duplicate findings."""
        seen_fingerprints = set()
        unique_findings = []
        
        for finding in findings:
            fingerprint = FindingDeduplicator._create_fingerprint(finding)
            
            if fingerprint not in seen_fingerprints:
                seen_fingerprints.add(fingerprint)
                unique_findings.append(finding)
        
        return unique_findings
    
    @staticmethod
    def _create_fingerprint(finding: Finding) -> str:
        """Create fingerprint for finding."""
        from urllib.parse import urlparse
        
        parsed = urlparse(finding.url)
        
        components = [
            str(finding.finding_type),
            parsed.netloc,
            parsed.path,
            finding.parameter or "",
            finding.method,
        ]
        
        return "|".join(components)


class ConfidenceScorer:
    """Calculate confidence scores for findings."""
    
    @staticmethod
    def score_finding(finding: Finding) -> float:
        """Calculate confidence score (0-1)."""
        score = 0.5  # Base score
        
        raw_data = finding.raw_data or {}
        
        # Evidence factors
        if 'error_pattern' in raw_data:
            score += 0.2
        
        if 'response_time' in raw_data:
            score += 0.1
        
        if 'payload' in raw_data:
            score += 0.1
        
        if finding.severity in [FindingSeverity.CRITICAL, FindingSeverity.HIGH]:
            score += 0.1
        
        return min(score, 1.0)
    
    @staticmethod
    def get_confidence_label(score: float) -> str:
        """Get confidence label from score."""
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"


"""ML-Assisted detection and triage for BugBountyCrawler."""

import re
import json
from typing import List, Dict, Any, Optional
from collections import Counter
from datetime import datetime

from ..models.finding import Finding, FindingSeverity, FindingType


class MLAssistedTriage:
    """ML-assisted triage and analysis system."""
    
    def __init__(self, settings=None):
        """Initialize ML-assisted triage."""
        self.settings = settings
        
        # Training data (historical findings)
        self.training_data = []
        
        # Feature extractors
        self.feature_weights = {
            'severity_score': 0.30,
            'confidence_score': 0.25,
            'evidence_count': 0.20,
            'historical_accuracy': 0.15,
            'context_match': 0.10,
        }
        
        # Pattern matching
        self.known_patterns = {}
        
        # Auto-generated templates
        self.custom_templates = []
    
    def triage_finding(self, finding: Finding) -> Dict[str, Any]:
        """Use ML to assist in triaging a finding."""
        
        # Extract features
        features = self._extract_features(finding)
        
        # Calculate triage score
        triage_score = self._calculate_triage_score(features)
        
        # Generate summary
        summary = self._generate_summary(finding)
        
        # Suggest remediation
        remediation = self._suggest_remediation(finding)
        
        # Estimate severity confidence
        severity_confidence = self._estimate_severity_confidence(finding)
        
        # Check for similar historical findings
        similar_findings = self._find_similar_findings(finding)
        
        return {
            'triage_score': triage_score,
            'recommended_action': self._get_recommended_action(triage_score),
            'summary': summary,
            'suggested_remediation': remediation,
            'severity_confidence': severity_confidence,
            'similar_findings_count': len(similar_findings),
            'estimated_bounty': self._estimate_bounty(finding),
            'priority_rank': self._calculate_priority(triage_score, finding.severity),
        }
    
    def _extract_features(self, finding: Finding) -> Dict[str, float]:
        """Extract numerical features from finding for ML."""
        features = {}
        
        # Severity score
        severity_map = {
            FindingSeverity.CRITICAL: 1.0,
            FindingSeverity.HIGH: 0.75,
            FindingSeverity.MEDIUM: 0.5,
            FindingSeverity.LOW: 0.25,
            FindingSeverity.INFO: 0.0,
        }
        features['severity_score'] = severity_map.get(finding.severity, 0.5)
        
        # Confidence score
        confidence_map = {'high': 1.0, 'medium': 0.5, 'low': 0.25}
        features['confidence_score'] = confidence_map.get(finding.confidence, 0.5)
        
        # Evidence count (from raw_data)
        features['evidence_count'] = len(finding.raw_data) / 10.0  # Normalize
        
        # Risk score
        features['risk_score_normalized'] = finding.risk_score / 10.0
        
        # Description length (longer = more detail = higher quality)
        features['description_quality'] = min(len(finding.description) / 200.0, 1.0)
        
        # Has proof of concept
        features['has_poc'] = 1.0 if finding.proof_of_concept else 0.0
        
        # Has remediation
        features['has_remediation'] = 1.0 if finding.remediation else 0.0
        
        # Reference count
        features['reference_count'] = min(len(finding.references) / 3.0, 1.0)
        
        return features
    
    def _calculate_triage_score(self, features: Dict[str, float]) -> float:
        """Calculate ML-based triage score (0-1)."""
        # Weighted combination of features
        score = 0.0
        
        score += features.get('severity_score', 0) * 0.30
        score += features.get('confidence_score', 0) * 0.25
        score += features.get('risk_score_normalized', 0) * 0.20
        score += features.get('evidence_count', 0) * 0.10
        score += features.get('description_quality', 0) * 0.05
        score += features.get('has_poc', 0) * 0.05
        score += features.get('has_remediation', 0) * 0.03
        score += features.get('reference_count', 0) * 0.02
        
        return min(score, 1.0)
    
    def _generate_summary(self, finding: Finding) -> str:
        """Generate AI-assisted summary of finding."""
        
        # Extract key information
        finding_type = str(finding.finding_type).replace('_', ' ').title()
        severity = str(finding.severity).upper()
        
        # Create summary
        summary = f"[{severity}] {finding_type} vulnerability detected. "
        
        # Add impact
        summary += f"Impact: {finding.impact[:100]}. "
        
        # Add parameter if present
        if finding.parameter:
            summary += f"Vulnerable parameter: '{finding.parameter}'. "
        
        # Add exploitation likelihood
        summary += f"Exploitation likelihood: {finding.likelihood}. "
        
        # Add recommendation
        if finding.risk_score >= 8.0:
            summary += "IMMEDIATE ACTION REQUIRED."
        elif finding.risk_score >= 6.0:
            summary += "Prompt remediation recommended."
        else:
            summary += "Schedule for remediation."
        
        return summary
    
    def _suggest_remediation(self, finding: Finding) -> str:
        """Generate ML-suggested remediation steps."""
        
        remediation_templates = {
            FindingType.SQL_INJECTION: "Use parameterized queries or prepared statements. Never concatenate user input into SQL queries.",
            FindingType.NOSQL_INJECTION: "Sanitize all user inputs and use schema validation. Avoid dynamic query construction.",
            FindingType.COMMAND_INJECTION: "Avoid shell execution with user input. Use language-specific APIs instead of shell commands.",
            FindingType.XSS: "Implement context-aware output encoding. Use Content Security Policy headers.",
            FindingType.CSRF: "Implement anti-CSRF tokens for all state-changing operations. Use SameSite cookie attribute.",
            FindingType.IDOR: "Implement proper authorization checks. Use indirect object references or UUIDs.",
            FindingType.XXE: "Disable external entity processing in XML parsers. Use secure XML parser configuration.",
            FindingType.BUSINESS_LOGIC: "Implement server-side validation for all business rules. Add rate limiting and transaction locking.",
            FindingType.SECURITY_HEADERS: f"Add recommended header: {finding.raw_data.get('recommended_value', 'See documentation')}",
            FindingType.VULNERABLE_DEPENDENCY: "Update to latest secure version. Check for breaking changes before upgrading.",
            FindingType.CODE_VULNERABILITY: "Refactor code to eliminate unsafe function usage. Follow secure coding guidelines.",
            FindingType.MOBILE_SECURITY: "Review mobile security best practices. Implement recommended security controls.",
        }
        
        return remediation_templates.get(
            finding.finding_type,
            "Review OWASP guidelines for this vulnerability type and implement recommended controls."
        )
    
    def _estimate_severity_confidence(self, finding: Finding) -> float:
        """Estimate confidence in severity rating (0-1)."""
        confidence = 0.5
        
        # More evidence = higher confidence
        evidence_count = len(finding.raw_data)
        confidence += min(evidence_count / 10.0, 0.3)
        
        # Has specific indicators = higher confidence
        if 'error_pattern' in finding.raw_data or 'indicator' in finding.raw_data:
            confidence += 0.2
        
        # Has PoC = higher confidence
        if finding.proof_of_concept:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _find_similar_findings(self, finding: Finding) -> List[Finding]:
        """Find similar historical findings."""
        similar = []
        
        for historical in self.training_data:
            similarity = self._calculate_similarity(finding, historical)
            if similarity > 0.7:  # 70% similar
                similar.append(historical)
        
        return similar
    
    def _calculate_similarity(self, finding1: Finding, finding2: Finding) -> float:
        """Calculate similarity between two findings."""
        score = 0.0
        
        # Same type
        if finding1.finding_type == finding2.finding_type:
            score += 0.4
        
        # Same severity
        if finding1.severity == finding2.severity:
            score += 0.2
        
        # Similar URL
        if self._are_urls_similar(finding1.url, finding2.url):
            score += 0.2
        
        # Same parameter
        if finding1.parameter == finding2.parameter:
            score += 0.2
        
        return score
    
    def _are_urls_similar(self, url1: str, url2: str) -> bool:
        """Check if URLs are similar."""
        from urllib.parse import urlparse
        
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        # Same domain and path
        return parsed1.netloc == parsed2.netloc and parsed1.path == parsed2.path
    
    def _estimate_bounty(self, finding: Finding) -> Dict[str, float]:
        """Estimate potential bug bounty payout."""
        
        # Bounty ranges by severity
        bounty_ranges = {
            FindingSeverity.CRITICAL: (5000, 50000),
            FindingSeverity.HIGH: (1000, 10000),
            FindingSeverity.MEDIUM: (250, 2500),
            FindingSeverity.LOW: (50, 500),
            FindingSeverity.INFO: (0, 100),
        }
        
        min_bounty, max_bounty = bounty_ranges.get(
            finding.severity,
            (0, 100)
        )
        
        # Adjust based on finding type
        multipliers = {
            FindingType.SQL_INJECTION: 1.5,
            FindingType.COMMAND_INJECTION: 1.8,
            FindingType.XXE: 1.4,
            FindingType.IDOR: 1.3,
            FindingType.BUSINESS_LOGIC: 1.6,
            FindingType.VULNERABLE_DEPENDENCY: 1.2,
        }
        
        multiplier = multipliers.get(finding.finding_type, 1.0)
        
        return {
            'min': int(min_bounty * multiplier),
            'max': int(max_bounty * multiplier),
            'estimated': int((min_bounty + max_bounty) / 2 * multiplier),
        }
    
    def _get_recommended_action(self, triage_score: float) -> str:
        """Get recommended action based on triage score."""
        if triage_score >= 0.8:
            return "Immediate triage required - High confidence, high severity"
        elif triage_score >= 0.6:
            return "Triage within 24 hours - Likely valid finding"
        elif triage_score >= 0.4:
            return "Schedule for review - Moderate confidence"
        else:
            return "Low priority - Manual verification recommended"
    
    def _calculate_priority(self, triage_score: float, severity: FindingSeverity) -> int:
        """Calculate priority ranking (1-10, 10 = highest)."""
        base_score = triage_score * 10
        
        # Adjust based on severity
        severity_bonus = {
            FindingSeverity.CRITICAL: 2,
            FindingSeverity.HIGH: 1,
            FindingSeverity.MEDIUM: 0,
            FindingSeverity.LOW: -1,
            FindingSeverity.INFO: -2,
        }
        
        priority = base_score + severity_bonus.get(severity, 0)
        return max(1, min(10, int(priority)))
    
    def train_from_findings(self, findings: List[Finding], labels: List[str]):
        """Train from historical findings (true_positive, false_positive, etc.)."""
        for finding, label in zip(findings, labels):
            self.training_data.append({
                'finding': finding,
                'label': label,
                'features': self._extract_features(finding),
                'timestamp': datetime.utcnow(),
            })
        
        # Update pattern recognition
        self._update_patterns()
    
    def _update_patterns(self):
        """Update known patterns from training data."""
        # Group by finding type and label
        for item in self.training_data:
            finding_type = item['finding'].finding_type
            label = item['label']
            
            key = f"{finding_type}_{label}"
            
            if key not in self.known_patterns:
                self.known_patterns[key] = {
                    'count': 0,
                    'avg_features': {},
                }
            
            self.known_patterns[key]['count'] += 1
    
    def generate_detection_template(self, example_findings: List[Finding]) -> Dict[str, Any]:
        """Auto-generate detection template from example findings."""
        
        if not example_findings:
            return {}
        
        # Analyze examples to extract pattern
        finding_type = example_findings[0].finding_type
        
        # Extract common payloads
        payloads = []
        for finding in example_findings:
            if 'payload' in finding.raw_data:
                payloads.append(finding.raw_data['payload'])
        
        # Extract common indicators
        indicators = []
        for finding in example_findings:
            if 'indicator' in finding.raw_data:
                indicators.append(finding.raw_data['indicator'])
            if 'error_pattern' in finding.raw_data:
                indicators.append(finding.raw_data['error_pattern'])
        
        # Create template
        template = {
            'name': f"{finding_type}_custom_template",
            'finding_type': str(finding_type),
            'severity': str(example_findings[0].severity),
            'payloads': list(set(payloads)),
            'indicators': list(set(indicators)),
            'description': example_findings[0].description,
            'remediation': example_findings[0].remediation,
            'generated_at': datetime.utcnow().isoformat(),
            'based_on_examples': len(example_findings),
        }
        
        self.custom_templates.append(template)
        
        return template
    
    def deduplicate_findings_ml(self, findings: List[Finding]) -> List[Finding]:
        """ML-assisted deduplication (better than simple fingerprinting)."""
        if len(findings) <= 1:
            return findings
        
        unique_findings = []
        seen_clusters = []
        
        for finding in findings:
            # Check if similar to any existing cluster
            is_duplicate = False
            
            for cluster in seen_clusters:
                similarity = self._calculate_similarity(finding, cluster['representative'])
                if similarity > 0.85:  # 85% similar = duplicate
                    cluster['duplicates'].append(finding)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                # Create new cluster
                seen_clusters.append({
                    'representative': finding,
                    'duplicates': [],
                })
                unique_findings.append(finding)
        
        return unique_findings
    
    def prioritize_findings_ml(self, findings: List[Finding]) -> List[Finding]:
        """ML-assisted prioritization."""
        if not findings:
            return findings
        
        # Calculate triage scores for all
        scored_findings = []
        for finding in findings:
            triage_result = self.triage_finding(finding)
            scored_findings.append({
                'finding': finding,
                'triage_score': triage_result['triage_score'],
                'priority': triage_result['priority_rank'],
            })
        
        # Sort by priority and triage score
        sorted_findings = sorted(
            scored_findings,
            key=lambda x: (x['priority'], x['triage_score']),
            reverse=True
        )
        
        return [item['finding'] for item in sorted_findings]
    
    def _calculate_similarity(self, finding1: Finding, finding2: Finding) -> float:
        """Calculate similarity score between findings."""
        score = 0.0
        
        # Same type (40% weight)
        if finding1.finding_type == finding2.finding_type:
            score += 0.4
        
        # Same severity (20% weight)
        if finding1.severity == finding2.severity:
            score += 0.2
        
        # Similar URL (20% weight)
        url_sim = self._url_similarity(finding1.url, finding2.url)
        score += url_sim * 0.2
        
        # Same parameter (20% weight)
        if finding1.parameter == finding2.parameter:
            score += 0.2
        
        return score
    
    def _url_similarity(self, url1: str, url2: str) -> float:
        """Calculate URL similarity."""
        from urllib.parse import urlparse
        
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        score = 0.0
        
        # Same domain
        if parsed1.netloc == parsed2.netloc:
            score += 0.5
        
        # Same path
        if parsed1.path == parsed2.path:
            score += 0.5
        
        return score
    
    def _calculate_priority(self, triage_score: float, severity: FindingSeverity) -> int:
        """Calculate priority (1-10)."""
        base = triage_score * 7
        
        bonus = {
            FindingSeverity.CRITICAL: 3,
            FindingSeverity.HIGH: 2,
            FindingSeverity.MEDIUM: 1,
            FindingSeverity.LOW: 0,
            FindingSeverity.INFO: -1,
        }
        
        priority = base + bonus.get(severity, 0)
        return max(1, min(10, int(priority)))
    
    def analyze_trends(self, findings: List[Finding]) -> Dict[str, Any]:
        """Analyze trends in findings using ML."""
        
        # Finding type distribution
        type_counts = Counter(f.finding_type for f in findings)
        
        # Severity distribution
        severity_counts = Counter(f.severity for f in findings)
        
        # Temporal analysis
        by_day = defaultdict(int)
        for finding in findings:
            day = finding.discovered_at.strftime("%Y-%m-%d")
            by_day[day] += 1
        
        # Detect trending vulnerability types
        trending = []
        if len(type_counts) > 0:
            avg_per_type = len(findings) / len(type_counts)
            for finding_type, count in type_counts.most_common(5):
                if count > avg_per_type * 1.5:  # 50% above average
                    trending.append({
                        'type': str(finding_type),
                        'count': count,
                        'percentage': (count / len(findings)) * 100,
                    })
        
        return {
            'total_findings': len(findings),
            'type_distribution': dict(type_counts),
            'severity_distribution': dict(severity_counts),
            'daily_counts': dict(by_day),
            'trending_types': trending,
            'avg_risk_score': sum(f.risk_score for f in findings) / len(findings) if findings else 0,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ML assistant statistics."""
        return {
            'training_samples': len(self.training_data),
            'known_patterns': len(self.known_patterns),
            'custom_templates': len(self.custom_templates),
            'feature_weights': self.feature_weights,
        }


class ResponseClusterer:
    """ML-based response clustering for anomaly detection."""
    
    def __init__(self):
        """Initialize response clusterer."""
        self.clusters = []
    
    def cluster_responses(self, responses: List[Dict[str, Any]]) -> List[List[Dict]]:
        """Cluster responses by similarity (simple k-means-like)."""
        if len(responses) < 2:
            return [responses] if responses else []
        
        # Extract features for clustering
        features = []
        for resp in responses:
            features.append([
                resp.get('status', 200) / 100.0,  # Normalize
                resp.get('size', 0) / 1000.0,  # Normalize to KB
                resp.get('response_time', 0),
            ])
        
        # Simple clustering by rounding features
        clusters = defaultdict(list)
        
        for resp, feat in zip(responses, features):
            # Create cluster key by rounding features
            cluster_key = (
                round(feat[0]),  # Status (1xx, 2xx, 3xx, 4xx, 5xx)
                round(feat[1]),  # Size (nearest KB)
                round(feat[2]),  # Time (nearest second)
            )
            clusters[cluster_key].append(resp)
        
        return list(clusters.values())
    
    def find_outliers(self, responses: List[Dict[str, Any]]) -> List[Dict]:
        """Find outlier responses using statistical methods."""
        if len(responses) < 10:
            return []
        
        outliers = []
        
        # Calculate statistics
        sizes = [r.get('size', 0) for r in responses]
        times = [r.get('response_time', 0) for r in responses]
        
        if len(sizes) > 1:
            mean_size = statistics.mean(sizes)
            stdev_size = statistics.stdev(sizes)
            
            mean_time = statistics.mean(times)
            stdev_time = statistics.stdev(times) if len(set(times)) > 1 else 0
            
            # Find outliers (3 standard deviations)
            for resp, size, time_val in zip(responses, sizes, times):
                is_outlier = False
                
                if stdev_size > 0:
                    z_score_size = abs((size - mean_size) / stdev_size)
                    if z_score_size > 3.0:
                        is_outlier = True
                
                if stdev_time > 0:
                    z_score_time = abs((time_val - mean_time) / stdev_time)
                    if z_score_time > 3.0:
                        is_outlier = True
                
                if is_outlier:
                    outliers.append(resp)
        
        return outliers


# Simple placeholder for actual ML model
class SimpleMLModel:
    """Simple ML model for finding classification."""
    
    def __init__(self):
        """Initialize simple ML model."""
        self.weights = {}
        self.trained = False
    
    def train(self, X: List[Dict], y: List[str]):
        """Train simple model."""
        # In production, use scikit-learn, TensorFlow, or PyTorch
        # For now, just store training data
        self.trained = True
    
    def predict(self, X: Dict) -> Tuple[str, float]:
        """Predict classification and confidence."""
        # Placeholder - would use actual ML model
        return ('true_positive', 0.75)


# Global ML assistant instance
_global_ml_assistant = None

def get_ml_assistant() -> MLAssistedTriage:
    """Get global ML assistant instance."""
    global _global_ml_assistant
    if _global_ml_assistant is None:
        _global_ml_assistant = MLAssistedTriage()
    return _global_ml_assistant


"""Anomaly detection engine for BugBountyCrawler."""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime
import statistics
import re

from ..models.finding import Finding, FindingSeverity, FindingType


class AnomalyDetector:
    """Advanced anomaly detection for security testing."""
    
    def __init__(self, settings=None):
        """Initialize anomaly detector."""
        self.settings = settings
        
        # Response clustering data
        self.response_clusters = defaultdict(list)
        
        # Baseline statistics
        self.response_time_baseline = []
        self.response_size_baseline = []
        self.status_code_baseline = defaultdict(int)
        
        # Anomaly thresholds (standard deviations)
        self.time_threshold = 3.0
        self.size_threshold = 3.0
        
        # Pattern detection
        self.pattern_history = defaultdict(list)
        
        # Behavioral baselines
        self.behavioral_patterns = {}
    
    def detect_response_anomalies(self, url: str, status: int, size: int, 
                                  response_time: float, content: str) -> List[Dict[str, Any]]:
        """Detect anomalies in HTTP responses."""
        anomalies = []
        
        # 1. Timing anomaly
        if self.response_time_baseline:
            timing_anomaly = self._detect_timing_anomaly(response_time)
            if timing_anomaly:
                anomalies.append({
                    'type': 'timing_anomaly',
                    'severity': FindingSeverity.MEDIUM,
                    'description': f'Response time {response_time:.2f}s is {timing_anomaly:.1f} std devs above mean',
                    'confidence': 'high' if timing_anomaly > 3.0 else 'medium',
                    'risk_score': min(4.0 + timing_anomaly, 8.0)
                })
        
        # 2. Size anomaly
        if self.response_size_baseline:
            size_anomaly = self._detect_size_anomaly(size)
            if size_anomaly:
                anomalies.append({
                    'type': 'size_anomaly',
                    'severity': FindingSeverity.LOW,
                    'description': f'Response size {size} bytes is {size_anomaly:.1f} std devs from mean',
                    'confidence': 'medium',
                    'risk_score': min(3.0 + size_anomaly, 7.0)
                })
        
        # 3. Status code anomaly
        status_anomaly = self._detect_status_anomaly(status)
        if status_anomaly:
            anomalies.append({
                'type': 'status_code_anomaly',
                'severity': FindingSeverity.MEDIUM,
                'description': f'Unusual status code: {status}',
                'confidence': 'high',
                'risk_score': 6.0
            })
        
        # 4. Content anomaly (unusual patterns)
        content_anomaly = self._detect_content_anomaly(content)
        if content_anomaly:
            anomalies.append({
                'type': 'content_anomaly',
                'severity': FindingSeverity.LOW,
                'description': content_anomaly,
                'confidence': 'low',
                'risk_score': 3.5
            })
        
        # Update baselines
        self._update_baselines(status, size, response_time)
        
        return anomalies
    
    def cluster_responses(self, responses: List[Dict[str, Any]]) -> List[List[Dict]]:
        """Cluster responses by similarity."""
        if len(responses) < 2:
            return [responses] if responses else []
        
        # Simple clustering by size and status code
        clusters = defaultdict(list)
        
        for response in responses:
            # Create cluster key based on status and approximate size
            status = response.get('status', 0)
            size = response.get('size', 0)
            size_bucket = (size // 1000) * 1000  # Bucket by 1KB
            
            cluster_key = f"{status}_{size_bucket}"
            clusters[cluster_key].append(response)
        
        return list(clusters.values())
    
    def detect_emerging_patterns(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        """Detect emerging attack patterns."""
        patterns = []
        
        # Group findings by type and look for trends
        by_type = defaultdict(list)
        for finding in findings:
            by_type[finding.finding_type].append(finding)
        
        # Check for increasing frequency
        for finding_type, type_findings in by_type.items():
            if len(type_findings) >= 5:  # Significant number
                # Check temporal clustering
                timestamps = [f.discovered_at for f in type_findings]
                if self._is_temporally_clustered(timestamps):
                    patterns.append({
                        'pattern_type': 'temporal_cluster',
                        'finding_type': finding_type,
                        'count': len(type_findings),
                        'description': f'Spike in {finding_type} findings detected',
                        'severity': FindingSeverity.MEDIUM,
                    })
        
        # Check for unusual parameter patterns
        param_pattern = self._detect_parameter_patterns(findings)
        if param_pattern:
            patterns.append(param_pattern)
        
        return patterns
    
    def detect_behavioral_anomaly(self, user_id: str, action: str, 
                                 metadata: Dict[str, Any]) -> Optional[Dict]:
        """Detect behavioral anomalies (unusual user actions)."""
        
        # Track user behavior
        user_key = f"{user_id}_{action}"
        
        if user_key not in self.behavioral_patterns:
            self.behavioral_patterns[user_key] = {
                'count': 0,
                'avg_frequency': 0.0,
                'last_seen': None,
            }
        
        pattern = self.behavioral_patterns[user_key]
        pattern['count'] += 1
        
        # Check for unusual frequency
        if pattern['last_seen']:
            time_diff = (datetime.utcnow() - pattern['last_seen']).total_seconds()
            
            # Unusually fast repeated actions (< 1 second)
            if time_diff < 1.0:
                return {
                    'anomaly_type': 'rapid_action',
                    'description': f'Rapid repeated {action} in {time_diff:.2f}s',
                    'severity': FindingSeverity.MEDIUM,
                    'risk_score': 6.0,
                }
        
        pattern['last_seen'] = datetime.utcnow()
        
        return None
    
    def _detect_timing_anomaly(self, response_time: float) -> Optional[float]:
        """Detect timing anomaly using statistical analysis."""
        if len(self.response_time_baseline) < 10:
            return None
        
        mean = statistics.mean(self.response_time_baseline)
        stdev = statistics.stdev(self.response_time_baseline)
        
        if stdev == 0:
            return None
        
        # Calculate z-score
        z_score = (response_time - mean) / stdev
        
        if abs(z_score) > self.time_threshold:
            return abs(z_score)
        
        return None
    
    def _detect_size_anomaly(self, size: int) -> Optional[float]:
        """Detect size anomaly using statistical analysis."""
        if len(self.response_size_baseline) < 10:
            return None
        
        mean = statistics.mean(self.response_size_baseline)
        stdev = statistics.stdev(self.response_size_baseline)
        
        if stdev == 0:
            return None
        
        z_score = (size - mean) / stdev
        
        if abs(z_score) > self.size_threshold:
            return abs(z_score)
        
        return None
    
    def _detect_status_anomaly(self, status: int) -> bool:
        """Detect unusual status codes."""
        total_requests = sum(self.status_code_baseline.values())
        
        if total_requests < 10:
            return False
        
        # Status codes that rarely occur
        if status in [400, 500, 502, 503, 504]:
            frequency = self.status_code_baseline[status] / total_requests
            if frequency < 0.05:  # Less than 5%
                return True
        
        return False
    
    def _detect_content_anomaly(self, content: str) -> Optional[str]:
        """Detect unusual content patterns."""
        
        # Check for stack traces
        if re.search(r'at [a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\(', content):
            return "Stack trace detected in response"
        
        # Check for SQL errors
        sql_errors = ['mysql', 'postgresql', 'oracle', 'sqlserver', 'sqlite']
        if any(err in content.lower() for err in sql_errors):
            return "Database error message detected"
        
        # Check for path disclosure
        if re.search(r'[C-Z]:\\.*\\|/etc/|/var/|/usr/', content):
            return "Filesystem path disclosed"
        
        return None
    
    def _update_baselines(self, status: int, size: int, response_time: float):
        """Update baseline statistics."""
        self.response_time_baseline.append(response_time)
        self.response_size_baseline.append(size)
        self.status_code_baseline[status] += 1
        
        # Keep only recent data (last 100 requests)
        if len(self.response_time_baseline) > 100:
            self.response_time_baseline = self.response_time_baseline[-100:]
        if len(self.response_size_baseline) > 100:
            self.response_size_baseline = self.response_size_baseline[-100:]
    
    def _is_temporally_clustered(self, timestamps: List[datetime]) -> bool:
        """Check if timestamps are clustered in time."""
        if len(timestamps) < 3:
            return False
        
        # Sort timestamps
        sorted_times = sorted(timestamps)
        
        # Check if most occur within a short window
        time_window = 3600  # 1 hour in seconds
        
        for i in range(len(sorted_times) - 2):
            window_start = sorted_times[i]
            within_window = sum(
                1 for t in sorted_times[i:]
                if (t - window_start).total_seconds() <= time_window
            )
            
            if within_window >= len(sorted_times) * 0.7:  # 70% within window
                return True
        
        return False
    
    def _detect_parameter_patterns(self, findings: List[Finding]) -> Optional[Dict]:
        """Detect unusual patterns in parameters."""
        param_counts = defaultdict(int)
        
        for finding in findings:
            if finding.parameter:
                param_counts[finding.parameter] += 1
        
        # Check for parameters with many findings
        for param, count in param_counts.items():
            if count >= 5:  # Same parameter vulnerable multiple ways
                return {
                    'pattern_type': 'parameter_hotspot',
                    'parameter': param,
                    'count': count,
                    'description': f'Parameter "{param}" has {count} different vulnerabilities',
                    'severity': FindingSeverity.HIGH,
                }
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get anomaly detection statistics."""
        return {
            'response_time_samples': len(self.response_time_baseline),
            'response_size_samples': len(self.response_size_baseline),
            'status_code_distribution': dict(self.status_code_baseline),
            'clusters': len(self.response_clusters),
            'behavioral_patterns': len(self.behavioral_patterns),
        }


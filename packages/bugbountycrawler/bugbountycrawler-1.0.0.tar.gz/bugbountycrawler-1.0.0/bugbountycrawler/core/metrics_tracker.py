"""Metrics tracking and KPI management for BugBountyCrawler."""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field
import json

from ..models.finding import Finding, FindingSeverity, FindingType


@dataclass
class ScanMetrics:
    """Metrics for a single scan."""
    scan_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    target_url: str = ""
    status: str = "running"  # running, completed, failed
    
    # Scan statistics
    total_requests: int = 0
    failed_requests: int = 0
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    
    # Performance metrics
    avg_response_time: float = 0.0
    total_scan_time: float = 0.0
    
    # Confidence metrics
    high_confidence: int = 0
    medium_confidence: int = 0
    low_confidence: int = 0
    
    # False positive metrics
    false_positives: int = 0
    true_positives: int = 0
    unverified: int = 0


@dataclass
class FindingMetrics:
    """Metrics for findings management."""
    finding_id: str
    discovered_at: datetime
    severity: str
    finding_type: str
    confidence: str
    
    # Triage metrics
    time_to_triage: Optional[float] = None  # hours
    triaged_at: Optional[datetime] = None
    triaged_by: Optional[str] = None
    
    # Resolution metrics
    time_to_fix: Optional[float] = None  # hours
    resolved_at: Optional[datetime] = None
    resolution_status: str = "open"  # open, confirmed, false_positive, resolved, wontfix
    
    # Bounty metrics (if applicable)
    bounty_amount: Optional[float] = None
    bounty_paid_at: Optional[datetime] = None


class MetricsTracker:
    """Comprehensive metrics tracking for BugBountyCrawler."""
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.scan_metrics: Dict[str, ScanMetrics] = {}
        self.finding_metrics: Dict[str, FindingMetrics] = {}
        
        # Aggregated metrics
        self.total_scans = 0
        self.total_findings = 0
        self.total_bounty_earned = 0.0
        
        # Time-series data (last 30 days)
        self.daily_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Performance tracking
        self.scanner_performance: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "total_runs": 0,
                "total_findings": 0,
                "avg_time": 0.0,
                "false_positive_rate": 0.0,
            }
        )
    
    def start_scan(self, scan_id: str, target_url: str) -> ScanMetrics:
        """Start tracking a new scan."""
        metrics = ScanMetrics(
            scan_id=scan_id,
            start_time=datetime.utcnow(),
            target_url=target_url,
            status="running"
        )
        
        self.scan_metrics[scan_id] = metrics
        self.total_scans += 1
        
        return metrics
    
    def end_scan(self, scan_id: str, status: str = "completed"):
        """Mark scan as completed."""
        if scan_id in self.scan_metrics:
            metrics = self.scan_metrics[scan_id]
            metrics.end_time = datetime.utcnow()
            metrics.status = status
            
            if metrics.start_time:
                metrics.total_scan_time = (
                    metrics.end_time - metrics.start_time
                ).total_seconds()
            
            # Update daily metrics
            self._update_daily_metrics(metrics)
    
    def record_finding(self, scan_id: str, finding: Finding):
        """Record a finding."""
        if scan_id in self.scan_metrics:
            metrics = self.scan_metrics[scan_id]
            metrics.total_findings += 1
            
            # Count by severity
            if finding.severity == FindingSeverity.CRITICAL:
                metrics.critical_findings += 1
            elif finding.severity == FindingSeverity.HIGH:
                metrics.high_findings += 1
            elif finding.severity == FindingSeverity.MEDIUM:
                metrics.medium_findings += 1
            elif finding.severity == FindingSeverity.LOW:
                metrics.low_findings += 1
            
            # Count by confidence
            if finding.confidence == "high":
                metrics.high_confidence += 1
            elif finding.confidence == "medium":
                metrics.medium_confidence += 1
            elif finding.confidence == "low":
                metrics.low_confidence += 1
        
        # Create finding metrics
        finding_metrics = FindingMetrics(
            finding_id=finding.id or f"finding_{int(time.time())}",
            discovered_at=finding.discovered_at,
            severity=str(finding.severity),
            finding_type=str(finding.finding_type),
            confidence=finding.confidence
        )
        
        self.finding_metrics[finding_metrics.finding_id] = finding_metrics
        self.total_findings += 1
    
    def record_request(self, scan_id: str, success: bool, response_time: float):
        """Record HTTP request metrics."""
        if scan_id in self.scan_metrics:
            metrics = self.scan_metrics[scan_id]
            metrics.total_requests += 1
            
            if not success:
                metrics.failed_requests += 1
            
            # Update average response time
            if metrics.avg_response_time == 0:
                metrics.avg_response_time = response_time
            else:
                metrics.avg_response_time = (
                    (metrics.avg_response_time * (metrics.total_requests - 1) + response_time)
                    / metrics.total_requests
                )
    
    def triage_finding(self, finding_id: str, triaged_by: str, 
                      resolution: str = "confirmed"):
        """Mark finding as triaged."""
        if finding_id in self.finding_metrics:
            metrics = self.finding_metrics[finding_id]
            metrics.triaged_at = datetime.utcnow()
            metrics.triaged_by = triaged_by
            metrics.resolution_status = resolution
            
            # Calculate time to triage
            if metrics.discovered_at:
                time_diff = metrics.triaged_at - metrics.discovered_at
                metrics.time_to_triage = time_diff.total_seconds() / 3600.0  # hours
    
    def resolve_finding(self, finding_id: str, resolution: str = "resolved"):
        """Mark finding as resolved."""
        if finding_id in self.finding_metrics:
            metrics = self.finding_metrics[finding_id]
            metrics.resolved_at = datetime.utcnow()
            metrics.resolution_status = resolution
            
            # Calculate time to fix
            if metrics.discovered_at:
                time_diff = metrics.resolved_at - metrics.discovered_at
                metrics.time_to_fix = time_diff.total_seconds() / 3600.0  # hours
    
    def record_bounty(self, finding_id: str, amount: float):
        """Record bounty payment for finding."""
        if finding_id in self.finding_metrics:
            metrics = self.finding_metrics[finding_id]
            metrics.bounty_amount = amount
            metrics.bounty_paid_at = datetime.utcnow()
            
            self.total_bounty_earned += amount
    
    def update_scanner_performance(self, scanner_name: str, findings_count: int,
                                   execution_time: float, false_positives: int = 0):
        """Update scanner-specific performance metrics."""
        perf = self.scanner_performance[scanner_name]
        perf["total_runs"] += 1
        perf["total_findings"] += findings_count
        
        # Update average time
        if perf["avg_time"] == 0:
            perf["avg_time"] = execution_time
        else:
            perf["avg_time"] = (
                (perf["avg_time"] * (perf["total_runs"] - 1) + execution_time)
                / perf["total_runs"]
            )
        
        # Update false positive rate
        if findings_count > 0:
            fp_rate = false_positives / findings_count
            if perf["false_positive_rate"] == 0:
                perf["false_positive_rate"] = fp_rate
            else:
                perf["false_positive_rate"] = (
                    (perf["false_positive_rate"] * (perf["total_runs"] - 1) + fp_rate)
                    / perf["total_runs"]
                )
    
    def _update_daily_metrics(self, scan_metrics: ScanMetrics):
        """Update daily aggregated metrics."""
        date_key = scan_metrics.start_time.strftime("%Y-%m-%d")
        
        if date_key not in self.daily_metrics:
            self.daily_metrics[date_key] = {
                "scans": 0,
                "findings": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "avg_scan_time": 0.0,
            }
        
        daily = self.daily_metrics[date_key]
        daily["scans"] += 1
        daily["findings"] += scan_metrics.total_findings
        daily["critical"] += scan_metrics.critical_findings
        daily["high"] += scan_metrics.high_findings
        daily["medium"] += scan_metrics.medium_findings
        daily["low"] += scan_metrics.low_findings
        
        # Update average scan time
        if daily["avg_scan_time"] == 0:
            daily["avg_scan_time"] = scan_metrics.total_scan_time
        else:
            daily["avg_scan_time"] = (
                (daily["avg_scan_time"] * (daily["scans"] - 1) + scan_metrics.total_scan_time)
                / daily["scans"]
            )
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics."""
        # Overall statistics
        total_scans = len(self.scan_metrics)
        completed_scans = sum(1 for m in self.scan_metrics.values() if m.status == "completed")
        
        # Finding statistics
        total_findings = sum(m.total_findings for m in self.scan_metrics.values())
        critical_findings = sum(m.critical_findings for m in self.scan_metrics.values())
        high_findings = sum(m.high_findings for m in self.scan_metrics.values())
        
        # Triage statistics
        triaged_findings = sum(
            1 for m in self.finding_metrics.values() if m.triaged_at is not None
        )
        avg_triage_time = self._calculate_avg_triage_time()
        
        # Resolution statistics
        resolved_findings = sum(
            1 for m in self.finding_metrics.values() 
            if m.resolution_status == "resolved"
        )
        avg_time_to_fix = self._calculate_avg_time_to_fix()
        
        # False positive statistics
        false_positives = sum(
            1 for m in self.finding_metrics.values()
            if m.resolution_status == "false_positive"
        )
        true_positives = sum(
            1 for m in self.finding_metrics.values()
            if m.resolution_status in ["confirmed", "resolved"]
        )
        
        fp_rate = (false_positives / (false_positives + true_positives) * 100) if (false_positives + true_positives) > 0 else 0.0
        
        # Recent activity (last 7 days)
        recent_scans = self._get_recent_scans(days=7)
        recent_findings = self._get_recent_findings(days=7)
        
        return {
            "overview": {
                "total_scans": total_scans,
                "completed_scans": completed_scans,
                "total_findings": total_findings,
                "critical_findings": critical_findings,
                "high_findings": high_findings,
                "total_bounty_earned": self.total_bounty_earned,
            },
            "triage": {
                "triaged_findings": triaged_findings,
                "untriaged_findings": len(self.finding_metrics) - triaged_findings,
                "avg_triage_time_hours": avg_triage_time,
                "triage_percentage": (triaged_findings / len(self.finding_metrics) * 100) if self.finding_metrics else 0.0,
            },
            "resolution": {
                "resolved_findings": resolved_findings,
                "open_findings": len(self.finding_metrics) - resolved_findings,
                "avg_time_to_fix_hours": avg_time_to_fix,
                "resolution_rate": (resolved_findings / len(self.finding_metrics) * 100) if self.finding_metrics else 0.0,
            },
            "quality": {
                "false_positives": false_positives,
                "true_positives": true_positives,
                "false_positive_rate": fp_rate,
                "high_confidence_findings": sum(
                    1 for m in self.finding_metrics.values() if m.confidence == "high"
                ),
            },
            "recent_activity": {
                "scans_last_7_days": recent_scans,
                "findings_last_7_days": recent_findings,
            },
            "scanner_performance": self.scanner_performance,
        }
    
    def get_kpi_summary(self) -> Dict[str, Any]:
        """Get key performance indicators summary."""
        metrics = self.get_dashboard_metrics()
        
        return {
            "scan_completion_rate": (
                metrics["overview"]["completed_scans"] / metrics["overview"]["total_scans"] * 100
                if metrics["overview"]["total_scans"] > 0 else 0.0
            ),
            "avg_findings_per_scan": (
                metrics["overview"]["total_findings"] / metrics["overview"]["total_scans"]
                if metrics["overview"]["total_scans"] > 0 else 0.0
            ),
            "critical_finding_rate": (
                metrics["overview"]["critical_findings"] / metrics["overview"]["total_findings"] * 100
                if metrics["overview"]["total_findings"] > 0 else 0.0
            ),
            "false_positive_rate": metrics["quality"]["false_positive_rate"],
            "avg_triage_time_hours": metrics["triage"]["avg_triage_time_hours"],
            "avg_time_to_fix_hours": metrics["resolution"]["avg_time_to_fix_hours"],
            "total_bounty_earned": metrics["overview"]["total_bounty_earned"],
            "avg_bounty_per_finding": self._calculate_avg_bounty(),
        }
    
    def get_trend_data(self, days: int = 30) -> Dict[str, List]:
        """Get trend data for charts."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        dates = []
        scans = []
        findings = []
        critical = []
        
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            dates.append(date_key)
            
            daily = self.daily_metrics.get(date_key, {})
            scans.append(daily.get("scans", 0))
            findings.append(daily.get("findings", 0))
            critical.append(daily.get("critical", 0))
            
            current_date += timedelta(days=1)
        
        return {
            "dates": dates,
            "scans": scans,
            "findings": findings,
            "critical_findings": critical,
        }
    
    def _calculate_avg_triage_time(self) -> float:
        """Calculate average time to triage."""
        triage_times = [
            m.time_to_triage for m in self.finding_metrics.values()
            if m.time_to_triage is not None
        ]
        
        return sum(triage_times) / len(triage_times) if triage_times else 0.0
    
    def _calculate_avg_time_to_fix(self) -> float:
        """Calculate average time to fix."""
        fix_times = [
            m.time_to_fix for m in self.finding_metrics.values()
            if m.time_to_fix is not None
        ]
        
        return sum(fix_times) / len(fix_times) if fix_times else 0.0
    
    def _calculate_avg_bounty(self) -> float:
        """Calculate average bounty per finding."""
        bounties = [
            m.bounty_amount for m in self.finding_metrics.values()
            if m.bounty_amount is not None
        ]
        
        return sum(bounties) / len(bounties) if bounties else 0.0
    
    def _get_recent_scans(self, days: int = 7) -> int:
        """Get number of scans in recent days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return sum(
            1 for m in self.scan_metrics.values()
            if m.start_time >= cutoff
        )
    
    def _get_recent_findings(self, days: int = 7) -> int:
        """Get number of findings in recent days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return sum(
            1 for m in self.finding_metrics.values()
            if m.discovered_at >= cutoff
        )
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file."""
        data = {
            "dashboard_metrics": self.get_dashboard_metrics(),
            "kpi_summary": self.get_kpi_summary(),
            "trend_data": self.get_trend_data(),
            "export_timestamp": datetime.utcnow().isoformat(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def print_summary(self):
        """Print metrics summary to console."""
        kpis = self.get_kpi_summary()
        
        print("\n" + "="*60)
        print("📊 BugBountyCrawler Metrics Summary")
        print("="*60)
        
        print(f"\n🎯 Key Performance Indicators:")
        print(f"   Scan Completion Rate: {kpis['scan_completion_rate']:.1f}%")
        print(f"   Avg Findings/Scan: {kpis['avg_findings_per_scan']:.1f}")
        print(f"   Critical Finding Rate: {kpis['critical_finding_rate']:.1f}%")
        print(f"   False Positive Rate: {kpis['false_positive_rate']:.1f}%")
        
        print(f"\n⏱️ Time Metrics:")
        print(f"   Avg Triage Time: {kpis['avg_triage_time_hours']:.1f} hours")
        print(f"   Avg Time to Fix: {kpis['avg_time_to_fix_hours']:.1f} hours")
        
        print(f"\n💰 Bounty Metrics:")
        print(f"   Total Earned: ${kpis['total_bounty_earned']:.2f}")
        print(f"   Avg per Finding: ${kpis['avg_bounty_per_finding']:.2f}")
        
        print("="*60 + "\n")


# Global metrics tracker instance
_global_tracker = None

def get_metrics_tracker() -> MetricsTracker:
    """Get global metrics tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = MetricsTracker()
    return _global_tracker


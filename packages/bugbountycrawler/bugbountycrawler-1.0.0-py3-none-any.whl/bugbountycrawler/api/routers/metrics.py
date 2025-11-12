"""Metrics API router for BugBountyCrawler."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ...core.metrics_tracker import get_metrics_tracker

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_metrics() -> Dict[str, Any]:
    """Get comprehensive dashboard metrics."""
    try:
        tracker = get_metrics_tracker()
        return tracker.get_dashboard_metrics()
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpi")
async def get_kpi_summary() -> Dict[str, Any]:
    """Get key performance indicators summary."""
    try:
        tracker = get_metrics_tracker()
        return tracker.get_kpi_summary()
    except Exception as e:
        logger.error(f"Error getting KPI summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_trend_data(days: int = 30) -> Dict[str, Any]:
    """Get trend data for specified number of days."""
    try:
        tracker = get_metrics_tracker()
        return tracker.get_trend_data(days=days)
    except Exception as e:
        logger.error(f"Error getting trend data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan/{scan_id}/start")
async def start_scan_tracking(scan_id: str, target_url: str):
    """Start tracking a new scan."""
    try:
        tracker = get_metrics_tracker()
        metrics = tracker.start_scan(scan_id, target_url)
        return {"status": "started", "scan_id": scan_id}
    except Exception as e:
        logger.error(f"Error starting scan tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan/{scan_id}/end")
async def end_scan_tracking(scan_id: str, status: str = "completed"):
    """Mark scan as completed."""
    try:
        tracker = get_metrics_tracker()
        tracker.end_scan(scan_id, status)
        return {"status": "ended", "scan_id": scan_id}
    except Exception as e:
        logger.error(f"Error ending scan tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finding/{finding_id}/triage")
async def triage_finding(finding_id: str, triaged_by: str, resolution: str = "confirmed"):
    """Mark finding as triaged."""
    try:
        tracker = get_metrics_tracker()
        tracker.triage_finding(finding_id, triaged_by, resolution)
        return {"status": "triaged", "finding_id": finding_id}
    except Exception as e:
        logger.error(f"Error triaging finding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finding/{finding_id}/resolve")
async def resolve_finding(finding_id: str, resolution: str = "resolved"):
    """Mark finding as resolved."""
    try:
        tracker = get_metrics_tracker()
        tracker.resolve_finding(finding_id, resolution)
        return {"status": "resolved", "finding_id": finding_id}
    except Exception as e:
        logger.error(f"Error resolving finding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finding/{finding_id}/bounty")
async def record_bounty(finding_id: str, amount: float):
    """Record bounty payment for finding."""
    try:
        tracker = get_metrics_tracker()
        tracker.record_bounty(finding_id, amount)
        return {"status": "recorded", "finding_id": finding_id, "amount": amount}
    except Exception as e:
        logger.error(f"Error recording bounty: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scanner/{scanner_name}/performance")
async def get_scanner_performance(scanner_name: str) -> Dict[str, Any]:
    """Get performance metrics for specific scanner."""
    try:
        tracker = get_metrics_tracker()
        dashboard = tracker.get_dashboard_metrics()
        perf = dashboard["scanner_performance"].get(scanner_name)
        
        if not perf:
            raise HTTPException(status_code=404, detail=f"Scanner {scanner_name} not found")
        
        return {"scanner_name": scanner_name, "performance": perf}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scanner performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_metrics():
    """Export all metrics to JSON."""
    try:
        tracker = get_metrics_tracker()
        
        return {
            "dashboard": tracker.get_dashboard_metrics(),
            "kpi": tracker.get_kpi_summary(),
            "trends": tracker.get_trend_data()
        }
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache")
async def clear_metrics_cache():
    """Clear metrics cache."""
    try:
        tracker = get_metrics_tracker()
        tracker.cleanup_old_cache_entries()
        return {"status": "cache_cleared"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics():
    """Get high-level statistics."""
    try:
        tracker = get_metrics_tracker()
        dashboard = tracker.get_dashboard_metrics()
        kpi = tracker.get_kpi_summary()
        
        return {
            "total_scans": dashboard["overview"]["total_scans"],
            "total_findings": dashboard["overview"]["total_findings"],
            "total_bounty": dashboard["overview"]["total_bounty_earned"],
            "false_positive_rate": kpi["false_positive_rate"],
            "avg_triage_time": kpi["avg_triage_time_hours"],
            "completion_rate": kpi["scan_completion_rate"]
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


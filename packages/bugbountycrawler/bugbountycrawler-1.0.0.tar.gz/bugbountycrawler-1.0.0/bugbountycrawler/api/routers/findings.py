"""Findings API router for BugBountyCrawler."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import logging

from ...database.connection import get_database
from ...models.finding import Finding, FindingStatus, FindingSeverity

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get database session
def get_db():
    db = next(get_database())
    try:
        yield db
    finally:
        db.close()


class FindingUpdateRequest(BaseModel):
    """Request model for updating a finding."""
    status: Optional[FindingStatus] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None


@router.get("/", response_model=List[Finding])
async def list_findings(
    skip: int = 0,
    limit: int = 100,
    status: Optional[FindingStatus] = None,
    severity: Optional[FindingSeverity] = None,
    scan_id: Optional[str] = None,
    db = Depends(get_db)
):
    """List all findings."""
    try:
        query = db.query(Finding)
        
        if status:
            query = query.filter(Finding.status == status)
        if severity:
            query = query.filter(Finding.severity == severity)
        if scan_id:
            query = query.filter(Finding.scan_id == scan_id)
        
        findings = query.offset(skip).limit(limit).all()
        return findings
    
    except Exception as e:
        logger.error(f"Error listing findings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{finding_id}", response_model=Finding)
async def get_finding(finding_id: str, db = Depends(get_db)):
    """Get a specific finding."""
    try:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        
        if not finding:
            raise HTTPException(status_code=404, detail="Finding not found")
        
        return finding
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting finding {finding_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{finding_id}", response_model=Finding)
async def update_finding(
    finding_id: str,
    finding_data: FindingUpdateRequest,
    db = Depends(get_db)
):
    """Update a finding."""
    try:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        
        if not finding:
            raise HTTPException(status_code=404, detail="Finding not found")
        
        # Update fields
        if finding_data.status is not None:
            finding.status = finding_data.status
        if finding_data.approved_by is not None:
            finding.approved_by = finding_data.approved_by
        if finding_data.rejection_reason is not None:
            finding.rejection_reason = finding_data.rejection_reason
        
        db.commit()
        db.refresh(finding)
        
        return finding
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating finding {finding_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{finding_id}")
async def delete_finding(finding_id: str, db = Depends(get_db)):
    """Delete a finding."""
    try:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        
        if not finding:
            raise HTTPException(status_code=404, detail="Finding not found")
        
        db.delete(finding)
        db.commit()
        
        return {"message": "Finding deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting finding {finding_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{finding_id}/approve")
async def approve_finding(finding_id: str, db = Depends(get_db)):
    """Approve a finding."""
    try:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        
        if not finding:
            raise HTTPException(status_code=404, detail="Finding not found")
        
        finding.status = FindingStatus.APPROVED
        finding.approved_by = "system"  # TODO: Get from authentication
        db.commit()
        
        return {"message": "Finding approved successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving finding {finding_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{finding_id}/reject")
async def reject_finding(
    finding_id: str,
    rejection_reason: str,
    db = Depends(get_db)
):
    """Reject a finding."""
    try:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        
        if not finding:
            raise HTTPException(status_code=404, detail="Finding not found")
        
        finding.status = FindingStatus.REJECTED
        finding.rejection_reason = rejection_reason
        db.commit()
        
        return {"message": "Finding rejected successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting finding {finding_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))





















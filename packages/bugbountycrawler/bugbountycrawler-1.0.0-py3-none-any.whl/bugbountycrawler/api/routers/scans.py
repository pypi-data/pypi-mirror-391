"""Scan API router for BugBountyCrawler."""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
import logging

from ...database.connection import get_database
from ...models.scan import Scan, ScanStatus, ScanConfig
from ...scanners.manager import ScannerManager
from ...crawlers.manager import CrawlerManager
from ...core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get database session
def get_db():
    db = next(get_database())
    try:
        yield db
    finally:
        db.close()


class ScanCreateRequest(BaseModel):
    """Request model for creating a scan."""
    name: str
    description: Optional[str] = None
    program_id: str
    target_urls: List[str]
    config: Optional[ScanConfig] = None


class ScanUpdateRequest(BaseModel):
    """Request model for updating a scan."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ScanStatus] = None
    config: Optional[ScanConfig] = None


@router.post("/", response_model=Scan)
async def create_scan(
    scan_data: ScanCreateRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Create a new scan."""
    try:
        # Create scan
        scan = Scan(
            name=scan_data.name,
            description=scan_data.description,
            program_id=scan_data.program_id,
            target_urls=scan_data.target_urls,
            config=scan_data.config or ScanConfig(),
            created_by="system"  # TODO: Get from authentication
        )
        
        db.add(scan)
        db.commit()
        db.refresh(scan)
        
        # Start scan in background
        background_tasks.add_task(run_scan_background, scan.id)
        
        return scan
    
    except Exception as e:
        logger.error(f"Error creating scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Scan])
async def list_scans(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ScanStatus] = None,
    db = Depends(get_db)
):
    """List all scans."""
    try:
        query = db.query(Scan)
        
        if status:
            query = query.filter(Scan.status == status)
        
        scans = query.offset(skip).limit(limit).all()
        return scans
    
    except Exception as e:
        logger.error(f"Error listing scans: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scan_id}", response_model=Scan)
async def get_scan(scan_id: str, db = Depends(get_db)):
    """Get a specific scan."""
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        return scan
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan {scan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{scan_id}", response_model=Scan)
async def update_scan(
    scan_id: str,
    scan_data: ScanUpdateRequest,
    db = Depends(get_db)
):
    """Update a scan."""
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Update fields
        if scan_data.name is not None:
            scan.name = scan_data.name
        if scan_data.description is not None:
            scan.description = scan_data.description
        if scan_data.status is not None:
            scan.status = scan_data.status
        if scan_data.config is not None:
            scan.config = scan_data.config
        
        db.commit()
        db.refresh(scan)
        
        return scan
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scan {scan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{scan_id}")
async def delete_scan(scan_id: str, db = Depends(get_db)):
    """Delete a scan."""
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        db.delete(scan)
        db.commit()
        
        return {"message": "Scan deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scan {scan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{scan_id}/start")
async def start_scan(scan_id: str, db = Depends(get_db)):
    """Start a scan."""
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        if scan.status != ScanStatus.PENDING:
            raise HTTPException(status_code=400, detail="Scan is not in pending status")
        
        # Update scan status
        scan.status = ScanStatus.RUNNING
        db.commit()
        
        # Start scan in background
        from .scans import run_scan_background
        run_scan_background(scan_id)
        
        return {"message": "Scan started successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting scan {scan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{scan_id}/stop")
async def stop_scan(scan_id: str, db = Depends(get_db)):
    """Stop a scan."""
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        if scan.status != ScanStatus.RUNNING:
            raise HTTPException(status_code=400, detail="Scan is not running")
        
        # Update scan status
        scan.status = ScanStatus.CANCELLED
        db.commit()
        
        return {"message": "Scan stopped successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping scan {scan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_scan_background(scan_id: str):
    """Run scan in background."""
    try:
        logger.info(f"Starting background scan {scan_id}")
        
        # Get scan from database
        db = next(get_database())
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        
        if not scan:
            logger.error(f"Scan {scan_id} not found")
            return
        
        # Initialize managers
        settings = get_settings()
        scanner_manager = ScannerManager(settings)
        crawler_manager = CrawlerManager(settings)
        
        # Update scan status
        scan.status = ScanStatus.RUNNING
        db.commit()
        
        # Process each target
        for target_url in scan.target_urls:
            try:
                # Crawl target
                discovered_urls = await crawler_manager.crawl_target(target_url)
                scan.add_discovered_url(target_url)
                
                # Scan discovered URLs
                for url in discovered_urls:
                    scan_results = await scanner_manager.scan_url(url)
                    
                    # Process findings
                    for result in scan_results:
                        for finding in result.findings:
                            # TODO: Save finding to database
                            pass
                
                # Update progress
                scan.update_progress(completed_targets=scan.progress.completed_targets + 1)
                db.commit()
                
            except Exception as e:
                logger.error(f"Error processing target {target_url}: {str(e)}")
                scan.update_progress(errors_encountered=scan.progress.errors_encountered + 1)
                db.commit()
        
        # Mark scan as completed
        scan.status = ScanStatus.COMPLETED
        db.commit()
        
        logger.info(f"Background scan {scan_id} completed")
    
    except Exception as e:
        logger.error(f"Error in background scan {scan_id}: {str(e)}")
        
        # Mark scan as failed
        db = next(get_database())
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = ScanStatus.FAILED
            db.commit()





















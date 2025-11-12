"""Targets API router for BugBountyCrawler."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from ...database.connection import get_database
from ...models.target import Target

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get database session
def get_db():
    db = next(get_database())
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[Target])
async def list_targets(
    skip: int = 0,
    limit: int = 100,
    program_id: Optional[str] = None,
    db = Depends(get_db)
):
    """List all targets."""
    try:
        query = db.query(Target)
        
        if program_id:
            query = query.filter(Target.program_id == program_id)
        
        targets = query.offset(skip).limit(limit).all()
        return targets
    except Exception as e:
        logger.error(f"Error listing targets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{target_id}", response_model=Target)
async def get_target(target_id: str, db = Depends(get_db)):
    """Get a specific target."""
    try:
        target = db.query(Target).filter(Target.id == target_id).first()
        
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        return target
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting target {target_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))





















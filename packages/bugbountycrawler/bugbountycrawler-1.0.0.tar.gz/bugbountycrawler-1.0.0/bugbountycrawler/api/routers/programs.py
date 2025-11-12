"""Programs API router for BugBountyCrawler."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import logging

from ...database.connection import get_database
from ...models.program import Program, ProgramScope

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get database session
def get_db():
    db = next(get_database())
    try:
        yield db
    finally:
        db.close()


class ProgramCreateRequest(BaseModel):
    """Request model for creating a program."""
    name: str
    description: Optional[str] = None
    platform: str
    scope: ProgramScope


@router.get("/", response_model=List[Program])
async def list_programs(db = Depends(get_db)):
    """List all programs."""
    try:
        programs = db.query(Program).all()
        return programs
    except Exception as e:
        logger.error(f"Error listing programs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Program)
async def create_program(program_data: ProgramCreateRequest, db = Depends(get_db)):
    """Create a new program."""
    try:
        program = Program(
            name=program_data.name,
            description=program_data.description,
            platform=program_data.platform,
            scope=program_data.scope
        )
        
        db.add(program)
        db.commit()
        db.refresh(program)
        
        return program
    except Exception as e:
        logger.error(f"Error creating program: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{program_id}", response_model=Program)
async def get_program(program_id: str, db = Depends(get_db)):
    """Get a specific program."""
    try:
        program = db.query(Program).filter(Program.id == program_id).first()
        
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        return program
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting program {program_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))





















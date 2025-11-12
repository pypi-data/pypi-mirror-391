"""Users API router for BugBountyCrawler."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from ...database.connection import get_database
from ...models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get database session
def get_db():
    db = next(get_database())
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[User])
async def list_users(db = Depends(get_db)):
    """List all users."""
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, db = Depends(get_db)):
    """Get a specific user."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))





















"""
Users Router
Endpoints for user management
"""

from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.user import UserPublic
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user data

    This is a protected endpoint that requires a valid JWT access token

    Args:
        current_user: Current authenticated user (from JWT token)

    Returns:
        UserPublic: Current user's public data
    """
    return current_user

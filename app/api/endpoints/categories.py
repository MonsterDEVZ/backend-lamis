"""
Categories API Endpoints
Handles category operations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryPublic

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryPublic])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Get list of all categories

    Returns list of all available categories
    """
    query = select(Category).order_by(Category.name)
    result = await db.execute(query)
    categories = result.scalars().all()

    return categories


@router.get("/{category_id}", response_model=CategoryPublic)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get single category by ID

    Parameters:
    - category_id: Category ID

    Returns category details
    """
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category

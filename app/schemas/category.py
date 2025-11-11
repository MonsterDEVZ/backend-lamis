"""
Category Schemas
Pydantic models for Category API validation and serialization
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CategoryBase(BaseModel):
    """Base category schema with common attributes"""

    name: str
    slug: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category"""

    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None


class CategoryPublic(CategoryBase):
    """
    Public category schema for API responses
    Includes all category information
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

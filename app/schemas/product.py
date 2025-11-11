"""
Product Schemas
Pydantic models for Product API validation and serialization
"""

from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    """Base product schema with common attributes"""

    name: str
    price: Decimal
    is_new: bool = False
    main_image_url: str
    category_id: int
    description: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for creating a new product"""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product"""

    name: Optional[str] = None
    price: Optional[Decimal] = None
    is_new: Optional[bool] = None
    main_image_url: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None


class ProductPublic(BaseModel):
    """
    Public product schema for API responses in catalog
    Includes product information with category name
    """

    id: int
    name: str
    price: Decimal
    is_new: bool
    main_image_url: str
    category_id: int
    category_name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductDetail(ProductPublic):
    """
    Detailed product schema with full category information
    Used for single product views
    """

    pass


class ProductBatchRequest(BaseModel):
    """
    Schema for batch product request
    Used for fetching multiple products by IDs
    """

    ids: list[int]

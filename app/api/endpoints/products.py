"""
Products API Endpoints
Handles product catalog operations
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import joinedload
from typing import Optional
from app.db.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductPublic, ProductBatchRequest

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductPublic])
async def get_products(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    sort_by: Optional[str] = Query(
        None, description="Sort by: price_asc, price_desc, newest"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(12, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of products with filtering, sorting, and pagination

    Parameters:
    - category_id: Filter products by category
    - sort_by: Sort options (price_asc, price_desc, newest)
    - page: Page number (starts from 1)
    - limit: Number of items per page

    Returns list of products with category information
    """

    # Build base query with eager loading of category to avoid N+1 queries
    query = select(Product).join(Category).options(joinedload(Product.category))

    # Apply category filter
    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    # Apply sorting
    if sort_by == "price_asc":
        query = query.order_by(asc(Product.price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Product.price))
    elif sort_by == "newest":
        query = query.order_by(desc(Product.created_at))
    else:
        # Default sorting by id
        query = query.order_by(asc(Product.id))

    # Calculate offset for pagination
    offset = (page - 1) * limit

    # Apply pagination
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    products = result.scalars().unique().all()

    # Transform to response format with category name
    products_response = []
    for product in products:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "is_new": product.is_new,
            "main_image_url": product.main_image_url,
            "category_id": product.category_id,
            "category_name": product.category.name,
            "description": product.description,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
        }
        products_response.append(ProductPublic(**product_dict))

    return products_response


@router.get("/{product_id}", response_model=ProductPublic)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get single product by ID

    Parameters:
    - product_id: Product ID

    Returns product details with category information
    """
    query = (
        select(Product)
        .where(Product.id == product_id)
        .options(joinedload(Product.category))
    )
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_dict = {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "is_new": product.is_new,
        "main_image_url": product.main_image_url,
        "category_id": product.category_id,
        "category_name": product.category.name,
        "description": product.description,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }

    return ProductPublic(**product_dict)


@router.post("/batch", response_model=list[ProductPublic])
async def get_products_batch(
    request: ProductBatchRequest, db: AsyncSession = Depends(get_db)
):
    """
    Get multiple products by IDs in a single request

    Parameters:
    - request: JSON body with list of product IDs {"ids": [1, 5, 23]}

    Returns list of products matching the provided IDs
    Optimized with single database query using WHERE IN clause
    """

    if not request.ids:
        return []

    # Single optimized query with WHERE IN clause to fetch all products
    query = (
        select(Product)
        .where(Product.id.in_(request.ids))
        .options(joinedload(Product.category))
    )

    result = await db.execute(query)
    products = result.scalars().unique().all()

    # Transform to response format with category name
    products_response = []
    for product in products:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "is_new": product.is_new,
            "main_image_url": product.main_image_url,
            "category_id": product.category_id,
            "category_name": product.category.name,
            "description": product.description,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
        }
        products_response.append(ProductPublic(**product_dict))

    return products_response

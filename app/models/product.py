"""
Product Model
SQLAlchemy model for products table
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Product(Base):
    """
    Product model for e-commerce catalog

    Fields:
        id: Primary key
        name: Product name
        price: Product price (Decimal for precise currency handling)
        is_new: Flag for "Новинка" badge
        main_image_url: URL of the main product image
        category_id: Foreign key to categories table
        description: Optional product description
        created_at: Timestamp of product creation
        updated_at: Timestamp of last update
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    is_new = Column(Boolean, default=False, nullable=False)
    main_image_url = Column(String, nullable=False)
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with category
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"

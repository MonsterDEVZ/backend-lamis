"""
URL Configuration for Products App
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views import (
    BrandViewSet,
    CategoryViewSet,
    CollectionViewSet,
    ProductViewSet
)

router = DefaultRouter()
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'collections', CollectionViewSet, basename='collection')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]

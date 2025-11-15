"""
URL Configuration for Products App
НОВАЯ АРХИТЕКТУРА: Section → Brand → Category → Collection/Type → Product
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views import (
    SectionViewSet,
    BrandViewSet,
    CategoryViewSet,
    CollectionViewSet,
    TypeViewSet,
    ProductViewSet,
    TutorialCategoryViewSet,
    PlumbingSectionViewSet,
    MaterialCategoryViewSet,
    MaterialViewSet
)
from apps.products.search_views import SearchViewSet
from apps.products.catalog_views import (
    CatalogBrowseView,
    CatalogSectionView,
    CatalogCategoryView,
    CatalogProductsView
)

router = DefaultRouter()
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'collections', CollectionViewSet, basename='collection')
router.register(r'types', TypeViewSet, basename='type')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'search', SearchViewSet, basename='search')
router.register(r'tutorials', TutorialCategoryViewSet, basename='tutorial')
router.register(r'plumbing-section', PlumbingSectionViewSet, basename='plumbing-section')
router.register(r'material-categories', MaterialCategoryViewSet, basename='material-category')
router.register(r'materials', MaterialViewSet, basename='material')

urlpatterns = [
    # SEO-Friendly Catalog Navigation
    # Order matters: more specific patterns first
    path('catalog/browse/', CatalogBrowseView.as_view(), name='catalog-browse'),
    path('catalog/<slug:section_slug>/<slug:category_slug>/<slug:item_slug>/',
         CatalogProductsView.as_view(), name='catalog-products'),
    path('catalog/<slug:section_slug>/<slug:category_slug>/',
         CatalogCategoryView.as_view(), name='catalog-category'),
    path('catalog/<slug:section_slug>/',
         CatalogSectionView.as_view(), name='catalog-section'),

    # Standard REST API endpoints
    path('', include(router.urls)),
]

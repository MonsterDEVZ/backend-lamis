"""
Main URL Configuration for LAMIS E-commerce Backend
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API v1 - Public endpoints
    path('api/v1/', include('apps.products.urls')),
     path('api/v1/', include('apps.partners.urls')),
    path('api/v1/auth/', include('apps.authentication.urls')),

    # API v1 - Admin endpoints
    # path('api/v1/admin/', include('apps.logs.urls')),  # Disabled - apps.logs doesn't exist
    path('api/v1/admin/', include('apps.uploads.urls')),

    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

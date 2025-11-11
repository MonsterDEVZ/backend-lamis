"""
Views for file uploads
Admin-only access
"""

import os
import uuid
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from apps.products.permissions import IsAdmin


class ImageUploadView(APIView):
    """
    Upload image file
    POST /api/v1/admin/upload/

    Returns:
    {
        "url": "/media/products/uuid-filename.jpg"
    }
    """
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser, FormParser]

    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    def post(self, request):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES['file']

        # Validate file extension
        file_ext = file.name.split('.')[-1].lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return Response(
                {'error': f'Invalid file type. Allowed: {", ".join(self.ALLOWED_EXTENSIONS)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file size
        if file.size > self.MAX_FILE_SIZE:
            return Response(
                {'error': f'File too large. Max size: {self.MAX_FILE_SIZE / 1024 / 1024}MB'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}_{file.name}"
        file_path = os.path.join(settings.MEDIA_ROOT, 'products', unique_filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save file
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Return URL
        file_url = f"{settings.MEDIA_URL}products/{unique_filename}"

        return Response({
            'url': file_url,
            'filename': unique_filename,
            'size': file.size
        }, status=status.HTTP_201_CREATED)

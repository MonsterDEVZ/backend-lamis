"""
Management command to create default superuser
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config


class Command(BaseCommand):
    help = 'Create default superuser if not exists'

    def handle(self, *args, **options):
        User = get_user_model()

        # Get credentials from environment or use defaults
        username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
        email = config('DJANGO_SUPERUSER_EMAIL', default='admin@lamis.kg')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='Admin123!@#')

        # Check if superuser already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already exists. Skipping.')
            )
            return

        # Create superuser
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Superuser "{username}" created successfully!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'   Username: {username}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'   Email: {email}')
            )
            self.stdout.write(
                self.style.WARNING(f'   Password: {password}')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  Please change the password after first login!')
            )
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(f'🌐 Admin URL: https://backend-lamis-production.up.railway.app/admin/')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating superuser: {e}')
            )

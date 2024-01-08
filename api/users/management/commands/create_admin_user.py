from django.core.management.base import BaseCommand
from api.users.models import User, Role
from django.db import transaction


class Command(BaseCommand):
    help = 'Create Admin User'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                User.objects.create_superuser(
                    first_name="admin",
                    last_name="natije",
                    email="natije-admin@gmail.com",
                    password="natije123"
                )
            self.stdout.write(self.style.SUCCESS('Successfully created'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))

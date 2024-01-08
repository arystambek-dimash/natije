from django.core.management.base import BaseCommand
from api.users.models import Role
from django.db import transaction


class Command(BaseCommand):
    help = 'Create roles'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                Role.objects.create(name='teacher')
                Role.objects.create(name='student')
            self.stdout.write(self.style.SUCCESS('Roles created successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))

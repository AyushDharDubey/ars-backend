from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create default user groups'

    def handle(self, *args, **kwargs):
        groups = ['Admin', 'Reviewer', 'Reviewee']

        for group in groups:
            group_obj, created = Group.objects.get_or_create(name=group)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Group "{group}" created.'))
            else:
                self.stdout.write(f'Group "{group}" already exists.')

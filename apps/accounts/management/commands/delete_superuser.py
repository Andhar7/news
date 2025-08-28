from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete superuser accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the superuser to delete',
        )
        parser.add_argument(
            '--id',
            type=int,
            help='ID of the superuser to delete',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all superusers',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete all superusers (use with caution)',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_superusers()
        elif options['username']:
            self.delete_by_username(options['username'])
        elif options['id']:
            self.delete_by_id(options['id'])
        elif options['all']:
            self.delete_all_superusers()
        else:
            self.list_superusers()
            self.stdout.write(
                self.style.SUCCESS(
                    '\nUsage examples:'
                    '\n  python manage.py delete_superuser --list'
                    '\n  python manage.py delete_superuser --username admin'
                    '\n  python manage.py delete_superuser --id 1'
                    '\n  python manage.py delete_superuser --all'
                )
            )

    def list_superusers(self):
        superusers = User.objects.filter(is_superuser=True)
        if superusers.exists():
            self.stdout.write(self.style.SUCCESS('Current superusers:'))
            for user in superusers:
                self.stdout.write(
                    f'  ID: {user.id}, Username: {user.username}, Email: {user.email}'
                )
        else:
            self.stdout.write(self.style.WARNING('No superusers found.'))

    def delete_by_username(self, username):
        try:
            user = User.objects.get(username=username, is_superuser=True)
            user.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted superuser: {username}')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Superuser "{username}" not found.')
            )

    def delete_by_id(self, user_id):
        try:
            user = User.objects.get(id=user_id, is_superuser=True)
            username = user.username
            user.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted superuser: {username} (ID: {user_id})')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Superuser with ID {user_id} not found.')
            )

    def delete_all_superusers(self):
        superusers = User.objects.filter(is_superuser=True)
        count = superusers.count()
        if count > 0:
            superusers.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {count} superuser(s).')
            )
        else:
            self.stdout.write(self.style.WARNING('No superusers found to delete.'))

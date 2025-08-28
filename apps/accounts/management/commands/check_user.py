from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Check and fix user permissions for admin access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email of the user to check/fix',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the user to check/fix',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix permissions for the specified user',
        )
        parser.add_argument(
            '--list-all',
            action='store_true',
            help='List all users with their permissions',
        )

    def handle(self, *args, **options):
        if options['list_all']:
            self.list_all_users()
        elif options['email']:
            self.check_user_by_email(options['email'], options['fix'])
        elif options['username']:
            self.check_user_by_username(options['username'], options['fix'])
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'Usage examples:'
                    '\n  python manage.py check_user --list-all'
                    '\n  python manage.py check_user --email user@example.com'
                    '\n  python manage.py check_user --email user@example.com --fix'
                    '\n  python manage.py check_user --username username --fix'
                )
            )

    def list_all_users(self):
        users = User.objects.all()
        if users.exists():
            self.stdout.write(self.style.SUCCESS('All users:'))
            for user in users:
                status = []
                if user.is_superuser:
                    status.append('SUPERUSER')
                if user.is_staff:
                    status.append('STAFF')
                if user.is_active:
                    status.append('ACTIVE')
                else:
                    status.append('INACTIVE')
                
                status_str = ', '.join(status) if status else 'NO PERMISSIONS'
                
                self.stdout.write(
                    f'  ID: {user.id}, Username: {user.username}, '
                    f'Email: {user.email}, Status: {status_str}'
                )
        else:
            self.stdout.write(self.style.WARNING('No users found.'))

    def check_user_by_email(self, email, fix=False):
        try:
            user = User.objects.get(email=email)
            self.display_user_info(user, fix)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email "{email}" not found.')
            )

    def check_user_by_username(self, username, fix=False):
        try:
            user = User.objects.get(username=username)
            self.display_user_info(user, fix)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with username "{username}" not found.')
            )

    def display_user_info(self, user, fix=False):
        self.stdout.write(f'\nUser Information:')
        self.stdout.write(f'  ID: {user.id}')
        self.stdout.write(f'  Username: {user.username}')
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Is Active: {user.is_active}')
        self.stdout.write(f'  Is Staff: {user.is_staff}')
        self.stdout.write(f'  Is Superuser: {user.is_superuser}')
        
        # Check for admin access issues
        issues = []
        if not user.is_active:
            issues.append('User is not active')
        if not user.is_staff:
            issues.append('User is not staff (required for admin access)')
        if not user.is_superuser:
            issues.append('User is not superuser')
            
        if issues:
            self.stdout.write(self.style.ERROR('\nIssues found:'))
            for issue in issues:
                self.stdout.write(f'  - {issue}')
                
            if fix:
                self.stdout.write(self.style.WARNING('\nFixing issues...'))
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'User "{user.username}" has been updated with full admin permissions.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('\nTo fix these issues, run the command again with --fix flag.')
                )
        else:
            self.stdout.write(self.style.SUCCESS('\nNo issues found. User should be able to access admin.'))

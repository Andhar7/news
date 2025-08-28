from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with specified credentials'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email for the superuser')
        parser.add_argument('--username', type=str, help='Username for the superuser')
        parser.add_argument('--password', type=str, help='Password for the superuser')

    def handle(self, *args, **options):
        email = options.get('email') or input('Email: ')
        username = options.get('username') or input('Username: ')
        password = options.get('password') or input('Password: ')

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email "{email}" already exists.')
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User with username "{username}" already exists.')
            )
            return

        # Create the superuser
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        
        # Make sure all permissions are set
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Superuser created successfully!\n'
                f'Email: {email}\n'
                f'Username: {username}\n'
                f'Staff: {user.is_staff}\n'
                f'Superuser: {user.is_superuser}\n'
                f'Active: {user.is_active}'
            )
        )

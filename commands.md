# Django Management Commands

## Superuser Management
```bash
# List all superusers
python manage.py delete_superuser --list

# Delete by username
python manage.py delete_superuser --username USERNAME

# Delete by ID
python manage.py delete_superuser --id USER_ID

# Delete ALL superusers (use with extreme caution!)
python manage.py delete_superuser --all

# Check user details and permissions
python manage.py check_user --email EMAIL

# Create superuser
python manage.py create_superuser --email EMAIL --username USERNAME --password PASSWORD
```

## Examples
```bash
python manage.py delete_superuser --list
python manage.py delete_superuser --username ckg27
python manage.py delete_superuser --id 1
```

# The management folder structure you need:
apps/accounts/management/
├── __init__.py
└── commands/
    ├── __init__.py
    ├── delete_superuser.py  ✅ Keep this one
    ├── check_user.py
    └── create_superuser.py
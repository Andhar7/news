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
├── **init**.py
└── commands/
├── **init**.py
├── delete_superuser.py ✅ Keep this one
├── check_user.py
└── create_superuser.py

# TESTING

## Running Tests

```bash
# Run all tests
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests --verbosity=2

# Run specific test that prints all CURL commands
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests.UserAPICurlTests.test_print_all_curl_commands --verbosity=2

# Run only API tests
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests.UserAPICurlTests --verbosity=2

# Run only model tests
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests.UserModelCurlTests --verbosity=2
```

## Test Coverage

✅ User Model Tests:

- User creation
- String representation
- Full name property

✅ API Endpoint Tests:

- User registration
- User login
- Get user profile
- Update user profile
- Unauthorized access
- Invalid login
- Invalid registration

✅ CURL Command Generation:

- Complete CURL commands for all endpoints
- Error scenario testing
- Step-by-step testing guide
- Sample API responses

# How to Use:
# Get all CURL commands:
```bash
python manage.py test apps.accounts.tests.UserAPICurlTests.test_print_all_curl_commands --verbosity=2

# Run all tests:
python manage.py test apps.accounts.tests --verbosity=2

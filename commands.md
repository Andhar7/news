# Django Management Commands

## Superuser Management

```bash
# List all superusers
python3 manage.py delete_superuser --list

# Delete by username
python3 manage.py delete_superuser --username USERNAME

# Delete by ID
python3 manage.py delete_superuser --id USER_ID

# Delete ALL superusers (use with extreme caution!)
python3 manage.py delete_superuser --all

# Check user details and permissions
python3 manage.py check_user --email EMAIL

# Create superuser
python3 manage.py create_superuser --email EMAIL --username USERNAME --password PASSWORD
```

## Examples

```bash
python3 manage.py delete_superuser --list
python3 manage.py delete_superuser --username ckg27
python3 manage.py delete_superuser --id 1
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

### Accounts Tests

```bash
# Run all accounts tests
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests --verbosity=2

# Run specific test that prints all CURL commands for accounts
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests.UserAPICurlTests.test_print_all_curl_commands --verbosity=2

# Run only accounts API tests
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests.UserAPICurlTests --verbosity=2

# Run only accounts model tests
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests.UserModelCurlTests --verbosity=2
```

### Main App Tests (Posts & Categories)

```bash
# Run all main app tests
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.main.tests --verbosity=2
python3 manage.py runserver
python3 manage.py test apps.main.tests --verbosity=2

# Run specific test that prints all CURL commands for main app
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.main.tests.MainAPICurlTests.test_print_all_curl_commands --verbosity=2

# Run only main app API tests
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.main.tests.MainAPICurlTests --verbosity=2

# Run only main app model tests
/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.main.tests.MainModelTests --verbosity=2

# Run ALL tests for the entire project
/Users/kling/Desktop/news/ckg/bin/python manage.py test --verbosity=2
```

## Quick API Testing

### ✅ Your API is Live and Working!

```bash
# Test basic endpoints (server must be running)
curl -X GET http://127.0.0.1:8000/api/v1/posts/categories/ -H "Content-Type: application/json"
# Response: {"count":0,"next":null,"previous":null,"results":[]}

# Test root endpoint
curl -X GET http://127.0.0.1:8000/ -H "Content-Type: application/json"
# Response: {"message":"Welcome to News API","version":"v1","endpoints":{"admin":"/admin/","auth":"/api/v1/auth/"}}
```

### Quick Setup for Real Testing:

```bash
# 1. Start server
/Users/kling/Desktop/news/ckg/bin/python manage.py runserver

# 2. In another terminal, register a user
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# 3. Copy the access token from response and use it for authenticated requests
```

/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.main.tests.MainModelTests --verbosity=2

````

### Run All Tests

```bash
# Run all tests in the project
/Users/kling/Desktop/news/ckg/bin/python manage.py test --verbosity=2
````

# Run specific test that prints all CURL commands

/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests.UserAPICurlTests.test_print_all_curl_commands --verbosity=2

# Run only API tests

/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests.UserAPICurlTests --verbosity=2

# Run only model tests

/Users/kling/Desktop/news/ckg/bin/python manage.py test apps.accounts.tests.UserModelCurlTests --verbosity=2

````

## Test Coverage

### ✅ User Model Tests (Accounts):
- User creation
- String representation
- Full name property

### ✅ User API Endpoint Tests (Accounts):
- User registration
- User login
- Get user profile
- Update user profile
- Unauthorized access
- Invalid login
- Invalid registration

### ✅ Category Model Tests (Main):
- Category creation
- String representation
- Slug generation

### ✅ Post Model Tests (Main):
- Post creation
- String representation
- Views increment
- Slug generation

### ✅ Posts & Categories API Endpoint Tests (Main):
- **Categories:** List, Create, Detail, Update, Delete
- **Posts:** List, Create, Detail, Update, Delete
- **Special endpoints:** My posts, Popular posts, Recent posts, Featured posts, Pinned posts
- **Filtering & Search:** By category, by author, text search
- **Authorization:** Proper permission handling
- **Error scenarios:** Unauthorized access, non-existent resources

### ✅ CURL Command Generation:
- Complete CURL commands for all endpoints (accounts & main)
- Error scenario testing
- Step-by-step testing guides
- Sample API responses

# How to Use:
# Get all CURL commands:
```bash
python3 manage.py test apps.accounts.tests.UserAPICurlTests.test_print_all_curl_commands --verbosity=2

# Run all tests:
python3 manage.py test apps.accounts.tests --verbosity=2
````

 <!-- What You Can Build Next:
With this solid foundation, you could easily add:

Comment systems
File uploads (images, documents)
Email notifications
Social media integration
Advanced search with Elasticsearch
Real-time features with WebSockets
Mobile app APIs -->


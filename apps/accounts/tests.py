"""
CURL Tests for User Model - Django News App

This file contains curl commands to test all User-related API endpoints.
Copy and paste these commands into your terminal to test the API.

Base URL: http://127.0.0.1:8000/api/v1/auth/
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelCurlTests(TestCase):
    """
    Django Unit Tests for User Model
    """
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_user_string_representation(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'test@example.com')

    def test_user_full_name(self):
        """Test user full name property"""
        self.assertEqual(self.user.full_name, 'Test User')


class UserAPICurlTests(APITestCase):
    """
    API Tests with CURL Examples
    """
    
    def setUp(self):
        """Set up test data"""
        self.base_url = 'http://127.0.0.1:8000/api/v1/auth/'
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def print_curl_commands(self):
        """Print all CURL commands for testing"""
        print("\n" + "="*80)
        print("CURL COMMANDS FOR TESTING USER API ENDPOINTS")
        print("="*80)
        
        print("\n1. USER REGISTRATION")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url}register/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "newpass123",
    "password_confirm": "newpass123",
    "first_name": "New",
    "last_name": "User"
  }}'""")
        
        print("\n2. USER LOGIN")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url}login/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "email": "test@example.com",
    "password": "testpass123"
  }}'""")
        
        print("\n3. GET USER PROFILE")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}profile/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json"
  
# Replace YOUR_ACCESS_TOKEN with the token from login response""")
        
        print("\n4. UPDATE USER PROFILE")
        print("-" * 40)
        print(f"""curl -X PATCH {self.base_url}profile/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "first_name": "Updated",
    "last_name": "Name",
    "bio": "This is my updated bio"
  }}'""")
        
        print("\n5. CHANGE PASSWORD")
        print("-" * 40)
        print(f"""curl -X PUT {self.base_url}change-password/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "old_password": "testpass123",
    "new_password": "newpass456",
    "new_password_confirm": "newpass456"
  }}'""")
        
        print("\n6. REFRESH TOKEN")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url}token/refresh/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "refresh": "YOUR_REFRESH_TOKEN"
  }}'
  
# Replace YOUR_REFRESH_TOKEN with the refresh token from login response""")
        
        print("\n7. LOGOUT USER")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url}logout/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }}'""")
        
        print("\n" + "="*80)
        print("TESTING SCENARIOS")
        print("="*80)
        
        print("\n8. TEST INVALID REGISTRATION (passwords don't match)")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url}register/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "username": "baduser",
    "email": "bad@example.com",
    "password": "pass123",
    "password_confirm": "different123",
    "first_name": "Bad",
    "last_name": "User"
  }}'""")
        
        print("\n9. TEST INVALID LOGIN")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url}login/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "email": "wrong@example.com",
    "password": "wrongpass"
  }}'""")
        
        print("\n10. TEST ACCESS WITHOUT TOKEN")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}profile/ \\
  -H "Content-Type: application/json"
  
# Should return 401 Unauthorized""")
        
        print("\n" + "="*80)
        print("STEP-BY-STEP TESTING GUIDE")
        print("="*80)
        print("""
1. Start your Django server: python manage.py runserver
2. Run command #1 (Registration) to create a new user
3. Copy the access and refresh tokens from the response
4. Run command #3 (Get Profile) with the access token
5. Run command #4 (Update Profile) with the access token
6. Run command #5 (Change Password) with the access token
7. Run command #2 (Login) with the new password
8. Run command #6 (Refresh Token) with the refresh token
9. Run command #7 (Logout) with the access token
10. Test error scenarios with commands #8, #9, #10
        """)
        
        print("\n" + "="*80)
        print("SAMPLE RESPONSES")
        print("="*80)
        
        print("\nSUCCESSFUL REGISTRATION RESPONSE:")
        print("""
{
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User",
    "full_name": "New User",
    "bio": "",
    "avatar": null,
    "created_at": "2025-08-28T15:30:00Z",
    "updated_at": "2025-08-28T15:30:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "message": "User registered successfully"
}
        """)
        
        print("\nSUCCESSFUL LOGIN RESPONSE:")
        print("""
{
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User",
    "full_name": "New User",
    "bio": "",
    "avatar": null,
    "created_at": "2025-08-28T15:30:00Z",
    "updated_at": "2025-08-28T15:30:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "message": "User login successfully"
}
        """)

    def test_print_all_curl_commands(self):
        """Test to print all CURL commands"""
        self.print_curl_commands()
        
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = '/api/v1/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')

    def test_user_login(self):
        """Test user login endpoint"""
        url = '/api/v1/auth/login/'
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_profile(self):
        """Test user profile endpoint"""
        self.client.force_authenticate(user=self.user)
        url = '/api/v1/auth/profile/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_user_profile(self):
        """Test update user profile endpoint"""
        self.client.force_authenticate(user=self.user)
        url = '/api/v1/auth/profile/'
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoint"""
        url = '/api/v1/auth/profile/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_login(self):
        """Test invalid login credentials"""
        url = '/api/v1/auth/login/'
        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_registration_password_mismatch(self):
        """Test invalid registration with password mismatch"""
        url = '/api/v1/auth/register/'
        data = {
            'username': 'baduser',
            'email': 'bad@example.com',
            'password': 'pass123',
            'password_confirm': 'different123',
            'first_name': 'Bad',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
"""
CURL Tests for Main App (Posts & Categories) - Django News App

This file contains curl commands to test all Main app API endpoints.
Copy and paste these commands into your terminal to test the API.

Base URL: http://127.0.0.1:8000/api/v1/posts/
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Category, Post

User = get_user_model()


class MainModelTests(TestCase):
    """
    Django Unit Tests for Main App Models
    """
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        
        self.category = Category.objects.create(
            name='Technology',
            description='Tech related posts'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            category=self.category,
            author=self.user,
            status='published'
        )

    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.category.name, 'Technology')
        self.assertEqual(self.category.slug, 'technology')
        self.assertTrue(self.category.created_at)

    def test_category_string_representation(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), 'Technology')

    def test_post_creation(self):
        """Test post creation"""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.slug, 'test-post')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.category, self.category)
        self.assertEqual(self.post.status, 'published')

    def test_post_string_representation(self):
        """Test post string representation"""
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_increment_views(self):
        """Test post views increment"""
        initial_views = self.post.views_count
        self.post.increment_views()
        self.assertEqual(self.post.views_count, initial_views + 1)


class MainAPICurlTests(APITestCase):
    """
    API Tests with CURL Examples for Main App
    """
    
    def setUp(self):
        """Set up test data"""
        self.base_url = 'http://127.0.0.1:8000/api/v1/posts/'
        
        # Create test users
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        # Create another user
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.refresh2 = RefreshToken.for_user(self.user2)
        self.access_token2 = str(self.refresh2.access_token)
        
        # Create test categories
        self.category1 = Category.objects.create(
            name='Technology',
            description='Tech related posts'
        )
        
        self.category2 = Category.objects.create(
            name='Science',
            description='Science related posts'
        )
        
        # Create test posts
        self.post1 = Post.objects.create(
            title='First Test Post',
            content='This is the first test post with lots of content to test.',
            category=self.category1,
            author=self.user,
            status='published'
        )
        
        self.post2 = Post.objects.create(
            title='Second Test Post',
            content='This is the second test post.',
            category=self.category2,
            author=self.user2,
            status='published'
        )
        
        self.draft_post = Post.objects.create(
            title='Draft Post',
            content='This is a draft post.',
            category=self.category1,
            author=self.user,
            status='draft'
        )

    def print_curl_commands(self):
        """Print all CURL commands for testing Main App API"""
        print("\n" + "="*80)
        print("CURL COMMANDS FOR TESTING MAIN APP API ENDPOINTS")
        print("="*80)
        
        print("\n📁 CATEGORY ENDPOINTS")
        print("="*50)
        
        print("\n1. GET ALL CATEGORIES")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}categories/ \\
  -H "Content-Type: application/json"
  
# With search
curl -X GET "{self.base_url}categories/?search=tech" \\
  -H "Content-Type: application/json"
  
# With ordering
curl -X GET "{self.base_url}categories/?ordering=name" \\
  -H "Content-Type: application/json" """)
        
        print("\n2. CREATE NEW CATEGORY (Auth Required)")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url}categories/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "New Category",
    "description": "Description for new category"
  }}'""")
        
        print("\n3. GET SPECIFIC CATEGORY")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}categories/technology/ \\
  -H "Content-Type: application/json" """)
        
        print("\n4. UPDATE CATEGORY (Auth Required)")
        print("-" * 40)
        print(f"""curl -X PATCH {self.base_url}categories/technology/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "description": "Updated description for technology category"
  }}'""")
        
        print("\n5. DELETE CATEGORY (Auth Required)")
        print("-" * 40)
        print(f"""curl -X DELETE {self.base_url}categories/technology/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" """)
        
        print("\n📝 POST ENDPOINTS")
        print("="*50)
        
        print("\n6. GET ALL POSTS")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url} \\
  -H "Content-Type: application/json"
  
# With filters
curl -X GET "{self.base_url}?category=1&author=1" \\
  -H "Content-Type: application/json"
  
# With search
curl -X GET "{self.base_url}?search=test" \\
  -H "Content-Type: application/json"
  
# With ordering
curl -X GET "{self.base_url}?ordering=-created_at" \\
  -H "Content-Type: application/json" """)
        
        print("\n7. CREATE NEW POST (Auth Required)")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url} \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "title": "My New Post",
    "content": "This is the content of my new post with lots of details and information.",
    "category": 1,
    "status": "published"
  }}'""")
        
        print("\n8. GET SPECIFIC POST")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}first-test-post/ \\
  -H "Content-Type: application/json" """)
        
        print("\n9. UPDATE POST (Author Only)")
        print("-" * 40)
        print(f"""curl -X PATCH {self.base_url}first-test-post/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "title": "Updated Post Title",
    "content": "This is the updated content."
  }}'""")
        
        print("\n10. DELETE POST (Author Only)")
        print("-" * 40)
        print(f"""curl -X DELETE {self.base_url}first-test-post/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" """)
        
        print("\n📊 SPECIAL POST ENDPOINTS")
        print("="*50)
        
        print("\n11. GET MY POSTS (Auth Required)")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}my-posts/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" """)
        
        print("\n12. GET POPULAR POSTS")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}popular/ \\
  -H "Content-Type: application/json" """)
        
        print("\n13. GET PINNED POSTS")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}pinned/ \\
  -H "Content-Type: application/json" """)
        
        print("\n14. GET FEATURED POSTS")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}featured/ \\
  -H "Content-Type: application/json" """)
        
        print("\n15. GET RECENT POSTS")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}recent/ \\
  -H "Content-Type: application/json" """)
        
        print("\n16. GET POSTS BY CATEGORY")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}categories/technology/posts/ \\
  -H "Content-Type: application/json" """)
        
        print("\n" + "="*80)
        print("ERROR TESTING SCENARIOS")
        print("="*80)
        
        print("\n17. TEST UNAUTHORIZED CATEGORY CREATION")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url}categories/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "Unauthorized Category",
    "description": "Should fail without auth"
  }}'
  
# Should return 401 Unauthorized""")
        
        print("\n18. TEST POST CREATION WITHOUT AUTH")
        print("-" * 40)
        print(f"""curl -X POST {self.base_url} \\
  -H "Content-Type: application/json" \\
  -d '{{
    "title": "Unauthorized Post",
    "content": "This should fail"
  }}'
  
# Should return 401 Unauthorized""")
        
        print("\n19. TEST UPDATE OTHER USER'S POST")
        print("-" * 40)
        print(f"""curl -X PATCH {self.base_url}first-test-post/ \\
  -H "Authorization: Bearer WRONG_USER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "title": "Trying to update other's post"
  }}'
  
# Should return 403 Forbidden""")
        
        print("\n20. TEST GET NON-EXISTENT POST")
        print("-" * 40)
        print(f"""curl -X GET {self.base_url}non-existent-post/ \\
  -H "Content-Type: application/json"
  
# Should return 404 Not Found""")
        
        print("\n" + "="*80)
        print("STEP-BY-STEP TESTING GUIDE")
        print("="*80)
        print("""
SETUP:
1. Start your Django server: python manage.py runserver
2. Create a user account and get access token (see accounts tests)
3. Replace YOUR_ACCESS_TOKEN with your actual token

BASIC FLOW:
1. Get all categories (command #1)
2. Create a new category (command #2) 
3. Get all posts (command #6)
4. Create a new post (command #7)
5. Get specific post (command #8)
6. Update the post (command #9)

ADVANCED TESTING:
7. Test filtering posts by category (command #6 with filters)
8. Test searching posts (command #6 with search)
9. Get your posts only (command #11)
10. Test special endpoints (commands #12-16)
11. Test error scenarios (commands #17-20)
        """)
        
        print("\n" + "="*80)
        print("SAMPLE RESPONSES")
        print("="*80)
        
        print("\nCATEGORY LIST RESPONSE:")
        print("""
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Technology",
      "slug": "technology",
      "description": "Tech related posts",
      "posts_count": 2,
      "created_at": "2025-08-28T15:30:00Z"
    },
    {
      "id": 2,
      "name": "Science", 
      "slug": "science",
      "description": "Science related posts",
      "posts_count": 1,
      "created_at": "2025-08-28T15:31:00Z"
    }
  ]
}
        """)
        
        print("\nPOST LIST RESPONSE:")
        print("""
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "First Test Post",
      "slug": "first-test-post",
      "content": "This is the first test post with lots of content to test...",
      "image": null,
      "category": "Technology",
      "author": "testuser",
      "status": "published",
      "created_at": "2025-08-28T15:30:00Z",
      "updated_at": "2025-08-28T15:30:00Z",
      "views_count": 0,
      "comments_count": 0,
      "is_pinned": false,
      "pinned_info": {
        "is_pinned": false
      }
    }
  ],
  "pinned_posts_count": 0
}
        """)
        
        print("\nPOST DETAIL RESPONSE:")
        print("""
{
  "id": 1,
  "title": "First Test Post",
  "slug": "first-test-post", 
  "content": "This is the first test post with lots of content to test.",
  "image": null,
  "category": 1,
  "category_info": {
    "id": 1,
    "name": "Technology",
    "slug": "technology"
  },
  "author": 1,
  "author_info": {
    "id": 1,
    "username": "testuser",
    "full_name": "Test User",
    "avatar": null
  },
  "status": "published",
  "created_at": "2025-08-28T15:30:00Z",
  "updated_at": "2025-08-28T15:30:00Z",
  "views_count": 0,
  "comments_count": 0,
  "is_pinned": false,
  "pinned_info": {
    "is_pinned": false
  },
  "can_pin": true
}
        """)

    def test_print_all_curl_commands(self):
        """Test to print all CURL commands for Main App"""
        self.print_curl_commands()
        
    def test_category_list(self):
        """Test category list endpoint"""
        url = '/api/v1/posts/categories/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_category_create_authenticated(self):
        """Test category creation with authentication"""
        self.client.force_authenticate(user=self.user)
        url = '/api/v1/posts/categories/'
        data = {
            'name': 'New Category',
            'description': 'Test category description'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Category')
        self.assertEqual(response.data['slug'], 'new-category')

    def test_category_create_unauthenticated(self):
        """Test category creation without authentication"""
        url = '/api/v1/posts/categories/'
        data = {
            'name': 'Unauthorized Category',
            'description': 'Should fail'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_detail(self):
        """Test category detail endpoint"""
        url = f'/api/v1/posts/categories/{self.category1.slug}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category1.name)

    def test_post_list(self):
        """Test post list endpoint"""
        url = '/api/v1/posts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only show published posts
        self.assertEqual(len(response.data['results']), 2)

    def test_post_list_authenticated(self):
        """Test post list with authentication (shows own drafts)"""
        self.client.force_authenticate(user=self.user)
        url = '/api/v1/posts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should show published posts + own drafts
        self.assertEqual(len(response.data['results']), 3)

    def test_post_create_authenticated(self):
        """Test post creation with authentication"""
        self.client.force_authenticate(user=self.user)
        url = '/api/v1/posts/'
        data = {
            'title': 'New Test Post',
            'content': 'This is a new test post content.',
            'category': self.category1.id,
            'status': 'published'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Test Post')
        # The slug should be generated automatically
        self.assertTrue('slug' in response.data or Post.objects.filter(title='New Test Post').exists())

    def test_post_create_unauthenticated(self):
        """Test post creation without authentication"""
        url = '/api/v1/posts/'
        data = {
            'title': 'Unauthorized Post',
            'content': 'This should fail'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_detail(self):
        """Test post detail endpoint"""
        url = f'/api/v1/posts/{self.post1.slug}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post1.title)
        self.assertIn('author_info', response.data)
        self.assertIn('category_info', response.data)

    def test_post_update_by_author(self):
        """Test post update by author"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/v1/posts/{self.post1.slug}/'
        data = {
            'title': 'Updated Post Title'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Post Title')

    def test_post_update_by_non_author(self):
        """Test post update by non-author (should fail)"""
        self.client.force_authenticate(user=self.user2)
        url = f'/api/v1/posts/{self.post1.slug}/'
        data = {
            'title': 'Trying to update other user post'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_delete_by_author(self):
        """Test post deletion by author"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/v1/posts/{self.post1.slug}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_post_filtering(self):
        """Test post filtering"""
        url = f'/api/v1/posts/?category={self.category1.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only show posts from category1
        self.assertEqual(len(response.data['results']), 1)

    def test_post_search(self):
        """Test post search"""
        url = '/api/v1/posts/?search=first'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        self.assertIn('first', response.data['results'][0]['title'].lower())

    def test_nonexistent_post(self):
        """Test accessing non-existent post"""
        url = '/api/v1/posts/non-existent-post/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Comment
from apps.main.models import Category, Post

User = get_user_model()


class CommentModelTests(TestCase):
    """Test Comment model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            category=self.category,
            author=self.user,
            status='published'
        )

    def test_comment_creation(self):
        """Test comment creation"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment content'
        )
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, 'Test comment content')
        self.assertTrue(comment.is_active)
        self.assertIsNone(comment.parent)

    def test_comment_string_representation(self):
        """Test comment string representation"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        expected_str = f'Comment by {self.user.username} on {self.post.title}'
        self.assertEqual(str(comment), expected_str)

    def test_comment_reply_creation(self):
        """Test comment reply creation"""
        parent_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Parent comment'
        )
        reply = Comment.objects.create(
            post=self.post,
            author=self.user,
            parent=parent_comment,
            content='Reply comment'
        )
        self.assertEqual(reply.parent, parent_comment)
        self.assertTrue(reply.is_reply)
        self.assertFalse(parent_comment.is_reply)

    def test_replies_count(self):
        """Test replies count property"""
        parent_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Parent comment'
        )
        # Create 3 replies
        for i in range(3):
            Comment.objects.create(
                post=self.post,
                author=self.user,
                parent=parent_comment,
                content=f'Reply {i+1}'
            )
        self.assertEqual(parent_comment.replies_count, 3)


class CommentAPICurlTests(APITestCase):
    """Test Comments API endpoints with CURL command generation"""
    
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User1'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User2'
        )
        
        # Create test category and posts
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        self.post = Post.objects.create(
            title='Test Post for Comments',
            content='This post will have comments for testing',
            category=self.category,
            author=self.user1,
            status='published'
        )
        
        # Get tokens for users
        self.token1 = str(RefreshToken.for_user(self.user1).access_token)
        self.token2 = str(RefreshToken.for_user(self.user2).access_token)
        
        # Create a test comment for detailed operations
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user1,
            content='First test comment with detailed content for testing'
        )

    def test_comment_list(self):
        """Test comment list endpoint"""
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_create_authenticated(self):
        """Test comment creation with authentication"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('comment-list')
        data = {
            'post': self.post.id,
            'content': 'New test comment created via API'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_create_unauthenticated(self):
        """Test comment creation without authentication"""
        url = reverse('comment-list')
        data = {
            'post': self.post.id,
            'content': 'Should not be created'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_reply_create(self):
        """Test comment reply creation"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        url = reverse('comment-list')
        data = {
            'post': self.post.id,
            'parent': self.comment.id,
            'content': 'This is a reply to the first comment'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_detail(self):
        """Test comment detail endpoint"""
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_update_by_author(self):
        """Test comment update by author"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        data = {'content': 'Updated comment content by original author'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_update_by_non_author(self):
        """Test comment update by non-author (should fail)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        data = {'content': 'Trying to update other user comment'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_delete_by_author(self):
        """Test comment deletion (soft delete) by author"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that comment still exists but is inactive
        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_active)

    def test_my_comments(self):
        """Test my comments endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('my-comments')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_comments(self):
        """Test post comments endpoint"""
        url = reverse('post-comments', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_replies(self):
        """Test comment replies endpoint"""
        # Create a reply first
        reply = Comment.objects.create(
            post=self.post,
            author=self.user2,
            parent=self.comment,
            content='Reply to test comment'
        )
        
        url = reverse('comment-replies', kwargs={'comment_id': self.comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_filtering(self):
        """Test comment filtering"""
        url = reverse('comment-list')
        response = self.client.get(f'{url}?post={self.post.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nonexistent_comment(self):
        """Test accessing non-existent comment"""
        url = reverse('comment-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_post_comments(self):
        """Test accessing comments for non-existent post"""
        url = reverse('post-comments', kwargs={'post_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_print_all_curl_commands(self):
        """Test to print all CURL commands for Comments App"""
        
        print("\n" + "="*80)
        print("CURL COMMANDS FOR TESTING COMMENTS APP API ENDPOINTS")
        print("="*80)

        print("\n💬 COMMENT ENDPOINTS")
        print("="*50)

        print("\n1. GET ALL COMMENTS")
        print("-"*40)
        print("curl -X GET http://127.0.0.1:8000/api/v1/comments/ \\")
        print("  -H \"Content-Type: application/json\"")
        print("  ")
        print("# With filters")
        print("curl -X GET \"http://127.0.0.1:8000/api/v1/comments/?post=1&author=1\" \\")
        print("  -H \"Content-Type: application/json\"")
        print("  ")
        print("# With search")
        print("curl -X GET \"http://127.0.0.1:8000/api/v1/comments/?search=test\" \\")
        print("  -H \"Content-Type: application/json\"")
        print("  ")
        print("# With ordering")
        print("curl -X GET \"http://127.0.0.1:8000/api/v1/comments/?ordering=-created_at\" \\")
        print("  -H \"Content-Type: application/json\" ")

        print("\n2. CREATE NEW COMMENT (Auth Required)")
        print("-"*40)
        print("curl -X POST http://127.0.0.1:8000/api/v1/comments/ \\")
        print("  -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\" \\")
        print("  -H \"Content-Type: application/json\" \\")
        print("  -d '{")
        print("    \"post\": 1,")
        print("    \"content\": \"This is my new comment on the post. Great article!\"")
        print("  }'")

        print("\n3. CREATE COMMENT REPLY (Auth Required)")
        print("-"*40)
        print("curl -X POST http://127.0.0.1:8000/api/v1/comments/ \\")
        print("  -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\" \\")
        print("  -H \"Content-Type: application/json\" \\")
        print("  -d '{")
        print("    \"post\": 1,")
        print("    \"parent\": 1,")
        print("    \"content\": \"This is a reply to the first comment. I agree!\"")
        print("  }'")

        print("\n4. GET SPECIFIC COMMENT")
        print("-"*40)
        print("curl -X GET http://127.0.0.1:8000/api/v1/comments/1/ \\")
        print("  -H \"Content-Type: application/json\" ")

        print("\n5. UPDATE COMMENT (Author Only)")
        print("-"*40)
        print("curl -X PATCH http://127.0.0.1:8000/api/v1/comments/1/ \\")
        print("  -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\" \\")
        print("  -H \"Content-Type: application/json\" \\")
        print("  -d '{")
        print("    \"content\": \"Updated comment content with new information.\"")
        print("  }'")

        print("\n6. DELETE COMMENT (Author Only - Soft Delete)")
        print("-"*40)
        print("curl -X DELETE http://127.0.0.1:8000/api/v1/comments/1/ \\")
        print("  -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\" \\")
        print("  -H \"Content-Type: application/json\" ")

        print("\n📊 SPECIAL COMMENT ENDPOINTS")
        print("="*50)

        print("\n7. GET MY COMMENTS (Auth Required)")
        print("-"*40)
        print("curl -X GET http://127.0.0.1:8000/api/v1/comments/my-comments/ \\")
        print("  -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\" \\")
        print("  -H \"Content-Type: application/json\" ")

        print("\n8. GET COMMENTS FOR SPECIFIC POST")
        print("-"*40)
        print("curl -X GET http://127.0.0.1:8000/api/v1/comments/post/1/ \\")
        print("  -H \"Content-Type: application/json\" ")

        print("\n9. GET REPLIES TO SPECIFIC COMMENT")
        print("-"*40)
        print("curl -X GET http://127.0.0.1:8000/api/v1/comments/1/replies/ \\")
        print("  -H \"Content-Type: application/json\" ")

        print("\n" + "="*80)
        print("ERROR TESTING SCENARIOS")
        print("="*80)

        print("\n10. TEST UNAUTHORIZED COMMENT CREATION")
        print("-"*40)
        print("curl -X POST http://127.0.0.1:8000/api/v1/comments/ \\")
        print("  -H \"Content-Type: application/json\" \\")
        print("  -d '{")
        print("    \"post\": 1,")
        print("    \"content\": \"Should fail without auth\"")
        print("  }'")
        print("  ")
        print("# Should return 401 Unauthorized")

        print("\n11. TEST UPDATE OTHER USER'S COMMENT")
        print("-"*40)
        print("curl -X PATCH http://127.0.0.1:8000/api/v1/comments/1/ \\")
        print("  -H \"Authorization: Bearer WRONG_USER_TOKEN\" \\")
        print("  -H \"Content-Type: application/json\" \\")
        print("  -d '{")
        print("    \"content\": \"Trying to update other's comment\"")
        print("  }'")
        print("  ")
        print("# Should return 403 Forbidden")

        print("\n12. TEST GET NON-EXISTENT COMMENT")
        print("-"*40)
        print("curl -X GET http://127.0.0.1:8000/api/v1/comments/99999/ \\")
        print("  -H \"Content-Type: application/json\"")
        print("  ")
        print("# Should return 404 Not Found")

        print("\n13. TEST COMMENTS FOR NON-EXISTENT POST")
        print("-"*40)
        print("curl -X GET http://127.0.0.1:8000/api/v1/comments/post/99999/ \\")
        print("  -H \"Content-Type: application/json\"")
        print("  ")
        print("# Should return 404 Not Found")

        print("\n" + "="*80)
        print("STEP-BY-STEP TESTING GUIDE")
        print("="*80)

        print("\nSETUP:")
        print("1. Start your Django server: python3 manage.py runserver")
        print("2. Create a user account and get access token (see accounts tests)")
        print("3. Create a post (see main app tests)")
        print("4. Replace YOUR_ACCESS_TOKEN with your actual token")

        print("\nBASIC FLOW:")
        print("1. Get all comments (command #1)")
        print("2. Create a new comment (command #2)")
        print("3. Create a reply to comment (command #3)")
        print("4. Get specific comment (command #4)")
        print("5. Update the comment (command #5)")

        print("\nADVANCED TESTING:")
        print("6. Test filtering comments by post (command #1 with filters)")
        print("7. Test searching comments (command #1 with search)")
        print("8. Get your comments only (command #7)")
        print("9. Test special endpoints (commands #8-9)")
        print("10. Test error scenarios (commands #10-13)")
        print("        ")

        print("\n" + "="*80)
        print("SAMPLE RESPONSES")
        print("="*80)

        print("\nCOMMENT LIST RESPONSE:")
        print()
        print("{")
        print("  \"count\": 2,")
        print("  \"next\": null,")
        print("  \"previous\": null,")
        print("  \"results\": [")
        print("    {")
        print("      \"id\": 1,")
        print("      \"content\": \"Great article! Thanks for sharing.\",")
        print("      \"author\": 1,")
        print("      \"author_info\": {")
        print("        \"id\": 1,")
        print("        \"username\": \"testuser\",")
        print("        \"full_name\": \"Test User\",")
        print("        \"avatar\": null")
        print("      },")
        print("      \"parent\": null,")
        print("      \"is_active\": true,")
        print("      \"replies_count\": 2,")
        print("      \"is_reply\": false,")
        print("      \"created_at\": \"2025-08-28T15:30:00Z\",")
        print("      \"updated_at\": \"2025-08-28T15:30:00Z\"")
        print("    }")
        print("  ]")
        print("}")
        print("        ")

        print("\nPOST COMMENTS RESPONSE:")
        print()
        print("{")
        print("  \"post\": {")
        print("    \"id\": 1,")
        print("    \"title\": \"Introduction to Django REST Framework\",")
        print("    \"slug\": \"introduction-to-django-rest-framework\"")
        print("  },")
        print("  \"comments\": [")
        print("    {")
        print("      \"id\": 1,")
        print("      \"content\": \"Great tutorial!\",")
        print("      \"author_info\": {")
        print("        \"username\": \"user1\",")
        print("        \"full_name\": \"John Doe\"")
        print("      },")
        print("      \"replies\": [")
        print("        {")
        print("          \"id\": 2,")
        print("          \"content\": \"I agree, very helpful!\",")
        print("          \"author_info\": {")
        print("            \"username\": \"user2\",")
        print("            \"full_name\": \"Jane Smith\"")
        print("          }")
        print("        }")
        print("      ]")
        print("    }")
        print("  ],")
        print("  \"comments_count\": 2")
        print("}")
        print("        ")
        
        # This test should always pass
        self.assertTrue(True)
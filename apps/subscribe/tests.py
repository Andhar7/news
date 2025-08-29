from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from .models import SubscriptionPlan, Subscription, PinnedPost, SubscriptionHistory
from apps.main.models import Post, Category

User = get_user_model()


class SubscribeModelTests(TestCase):
    """Тесты для моделей приложения subscribe"""

    def setUp(self):
        """Настройка данных для тестов"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.plan = SubscriptionPlan.objects.create(
            name='Premium',
            price=Decimal('9.99'),
            duration_days=30,
            features={'feature1': 'value1'},
            is_active=True
        )

    def test_subscription_plan_creation(self):
        """Тест создания тарифного плана"""
        self.assertEqual(self.plan.name, 'Premium')
        self.assertEqual(self.plan.price, Decimal('9.99'))
        self.assertEqual(self.plan.duration_days, 30)
        self.assertTrue(self.plan.is_active)

    def test_subscription_creation(self):
        """Тест создания подписки"""
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.plan, self.plan)
        self.assertEqual(subscription.status, 'pending')  # Default status is pending

    def test_subscription_is_active_property(self):
        """Тест свойства is_active подписки"""
        future_date = timezone.now() + timedelta(days=30)
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=timezone.now(),
            end_date=future_date,
            status='active'  # Set status to active explicitly
        )
        self.assertTrue(subscription.is_active)

    def test_subscription_days_remaining_property(self):
        """Тест свойства days_remaining подписки"""
        future_date = timezone.now() + timedelta(days=10)
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=timezone.now(),
            end_date=future_date,
            status='active'  # Set status to active explicitly
        )
        # Allow for slight time difference - should be 9 or 10 days
        self.assertIn(subscription.days_remaining, [9, 10])

    def test_pinned_post_creation(self):
        """Тест создания закрепленного поста"""
        # First create an active subscription for the user
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            status='active'
        )
        
        category = Category.objects.create(name='Test Category')
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            category=category,
            status='published',
            image=None
        )
        
        pinned_post = PinnedPost.objects.create(
            user=self.user,
            post=post
        )
        self.assertEqual(pinned_post.user, self.user)
        self.assertEqual(pinned_post.post, post)

    def test_subscription_history_creation(self):
        """Тест создания записи истории подписки"""
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            status='active'
        )
        
        history = SubscriptionHistory.objects.create(
            subscription=subscription,
            action='created',
            description='Subscription created'
        )
        self.assertEqual(history.subscription, subscription)
        self.assertEqual(history.action, 'created')


class SubscribeAPICurlTests(APITestCase):
    """CURL тесты для API приложения subscribe"""

    def setUp(self):
        """Настройка данных для тестов"""
        self.client = APIClient()
        
        # Создание пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )

        # Создание тарифных планов
        self.plan1 = SubscriptionPlan.objects.create(
            name='Basic',
            price=Decimal('5.99'),
            duration_days=30,
            stripe_price_id='price_basic_599',
            features={'posts': 10, 'comments': 'unlimited'},
            is_active=True
        )
        
        self.plan2 = SubscriptionPlan.objects.create(
            name='Premium',
            price=Decimal('9.99'),
            duration_days=30,
            stripe_price_id='price_premium_999',
            features={'posts': 'unlimited', 'comments': 'unlimited', 'pin_posts': True},
            is_active=True
        )

        # Создание категории и поста
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user1,
            category=self.category,
            status='published',
            image=None  # Explicitly set image to None
        )

        # Получение токенов
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user1)
        self.token1 = str(refresh.access_token)
        
        refresh = RefreshToken.for_user(self.user2)
        self.token2 = str(refresh.access_token)

    def test_subscription_plans_list_curl(self):
        """Тест получения списка тарифных планов"""
        print("\n=== CURL: Get Subscription Plans List ===")
        
        url = '/api/v1/subscribe/plans/'
        response = self.client.get(url)
        
        print(f"curl -X GET http://localhost:8000{url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_subscription_plan_detail_curl(self):
        """Тест получения деталей тарифного плана"""
        print("\n=== CURL: Get Subscription Plan Detail ===")
        
        url = f'/api/v1/subscribe/plans/{self.plan1.id}/'
        response = self.client.get(url)
        
        print(f"curl -X GET http://localhost:8000{url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Basic')

    def test_subscription_status_without_auth_curl(self):
        """Тест получения статуса подписки без авторизации"""
        print("\n=== CURL: Get Subscription Status (No Auth) ===")
        
        url = '/api/v1/subscribe/status/'
        response = self.client.get(url)
        
        print(f"curl -X GET http://localhost:8000{url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscription_status_with_auth_curl(self):
        """Тест получения статуса подписки с авторизацией"""
        print("\n=== CURL: Get Subscription Status (With Auth) ===")
        
        url = '/api/v1/subscribe/status/'
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X GET http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}"')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_subscription'])

    def test_my_subscription_no_subscription_curl(self):
        """Тест получения подписки пользователя (подписки нет)"""
        print("\n=== CURL: Get My Subscription (No Subscription) ===")
        
        url = '/api/v1/subscribe/my-subscription/'
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X GET http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}"')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_my_subscription_with_subscription_curl(self):
        """Тест получения подписки пользователя (подписка есть)"""
        print("\n=== CURL: Get My Subscription (With Subscription) ===")
        
        # Создаем подписку
        subscription = Subscription.objects.create(
            user=self.user1,
            plan=self.plan1,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            status='active'
        )
        
        url = '/api/v1/subscribe/my-subscription/'
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X GET http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}"')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan_info']['name'], 'Basic')

    def test_subscription_history_curl(self):
        """Тест получения истории подписки"""
        print("\n=== CURL: Get Subscription History ===")
        
        # Создаем подписку и историю
        subscription = Subscription.objects.create(
            user=self.user1,
            plan=self.plan1,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            status='active'
        )
        
        SubscriptionHistory.objects.create(
            subscription=subscription,
            action='created',
            description='Subscription created'
        )
        
        url = '/api/v1/subscribe/history/'
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X GET http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}"')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_pin_post_no_subscription_curl(self):
        """Тест закрепления поста без подписки"""
        print("\n=== CURL: Pin Post (No Subscription) ===")
        
        url = '/api/v1/subscribe/pin-post/'
        data = {'post_id': self.post.id}
        response = self.client.post(
            url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X POST http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f"  -d '{json.dumps(data)}'")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pin_post_with_subscription_curl(self):
        """Тест закрепления поста с подпиской"""
        print("\n=== CURL: Pin Post (With Subscription) ===")
        
        # Создаем подписку
        Subscription.objects.create(
            user=self.user1,
            plan=self.plan2,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        url = '/api/v1/subscribe/pin-post/'
        data = {'post_id': self.post.id}
        response = self.client.post(
            url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X POST http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f"  -d '{json.dumps(data)}'")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_pinned_post_curl(self):
        """Тест получения закрепленного поста"""
        print("\n=== CURL: Get Pinned Post ===")
        
        # Создаем подписку и закрепленный пост
        Subscription.objects.create(
            user=self.user1,
            plan=self.plan2,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        PinnedPost.objects.create(
            user=self.user1,
            post=self.post
        )
        
        url = '/api/v1/subscribe/pinned-post/'
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X GET http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}"')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unpin_post_curl(self):
        """Тест открепления поста"""
        print("\n=== CURL: Unpin Post ===")
        
        # Создаем подписку и закрепленный пост
        Subscription.objects.create(
            user=self.user1,
            plan=self.plan2,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        PinnedPost.objects.create(
            user=self.user1,
            post=self.post
        )
        
        url = '/api/v1/subscribe/unpin-post/'
        data = {}
        response = self.client.post(
            url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X POST http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f"  -d '{json.dumps(data)}'")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_subscription_curl(self):
        """Тест отмены подписки"""
        print("\n=== CURL: Cancel Subscription ===")
        
        # Создаем подписку
        Subscription.objects.create(
            user=self.user1,
            plan=self.plan2,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        url = '/api/v1/subscribe/cancel/'
        response = self.client.post(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X POST http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}"')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pinned_posts_list_curl(self):
        """Тест получения списка всех закрепленных постов"""
        print("\n=== CURL: Get Pinned Posts List ===")
        
        # Создаем подписку и закрепленный пост
        Subscription.objects.create(
            user=self.user1,
            plan=self.plan2,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        PinnedPost.objects.create(
            user=self.user1,
            post=self.post
        )
        
        url = '/api/v1/subscribe/pinned-posts/'
        response = self.client.get(url)
        
        print(f"curl -X GET http://localhost:8000{url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_pin_post_curl(self):
        """Тест проверки возможности закрепить пост"""
        print("\n=== CURL: Can Pin Post Check ===")
        
        url = f'/api/v1/subscribe/can-pin/{self.post.id}/'
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X GET http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}"')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['can_pin'])

    def test_pin_others_post_curl(self):
        """Тест закрепления чужого поста"""
        print("\n=== CURL: Pin Others Post (Should Fail) ===")
        
        # Создаем пост другого пользователя
        other_post = Post.objects.create(
            title='Other User Post',
            content='Other content',
            author=self.user2,
            category=self.category,
            status='published',
            image=None
        )
        
        # Создаем подписку
        Subscription.objects.create(
            user=self.user1,
            plan=self.plan2,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        url = '/api/v1/subscribe/pin-post/'
        data = {'post_id': other_post.id}
        response = self.client.post(
            url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X POST http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f"  -d '{json.dumps(data)}'")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_plan_curl(self):
        """Тест получения неактивного плана"""
        print("\n=== CURL: Get Inactive Plan ===")
        
        # Создаем неактивный план
        inactive_plan = SubscriptionPlan.objects.create(
            name='Inactive Plan',
            price=Decimal('19.99'),
            duration_days=30,
            features={'premium': True},
            is_active=False
        )
        
        url = f'/api/v1/subscribe/plans/{inactive_plan.id}/'
        response = self.client.get(url)
        
        print(f"curl -X GET http://localhost:8000{url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscription_with_expired_date_curl(self):
        """Тест подписки с истекшим сроком"""
        print("\n=== CURL: Expired Subscription Status ===")
        
        # Создаем просроченную подписку
        Subscription.objects.create(
            user=self.user1,
            plan=self.plan1,
            start_date=timezone.now() - timedelta(days=60),
            end_date=timezone.now() - timedelta(days=30),
            status='expired'
        )
        
        url = '/api/v1/subscribe/status/'
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X GET http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}"')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_subscription'])
        self.assertFalse(response.data['is_active'])

    def test_delete_pinned_post_curl(self):
        """Тест удаления закрепленного поста"""
        print("\n=== CURL: Delete Pinned Post ===")
        
        # Создаем подписку и закрепленный пост
        Subscription.objects.create(
            user=self.user1,
            plan=self.plan2,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        PinnedPost.objects.create(
            user=self.user1,
            post=self.post
        )
        
        url = '/api/v1/subscribe/pinned-post/'
        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=f'Bearer {self.token1}'
        )
        
        print(f'curl -X DELETE http://localhost:8000{url} \\')
        print(f'  -H "Authorization: Bearer {self.token1}"')
        print(f"Status: {response.status_code}")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_multiple_subscription_plans_filter_curl(self):
        """Тест фильтрации активных планов"""
        print("\n=== CURL: Filter Active Plans Only ===")
        
        # Создаем дополнительные планы
        SubscriptionPlan.objects.create(
            name='Inactive Premium',
            price=Decimal('15.99'),
            duration_days=30,
            features={'premium': True},
            is_active=False
        )
        
        url = '/api/v1/subscribe/plans/'
        response = self.client.get(url)
        
        print(f"curl -X GET http://localhost:8000{url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
        print(f"Active plans count: {len(response.data['results'])}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должно вернуть только активные планы (2 из setUp)
        self.assertEqual(len(response.data['results']), 2)
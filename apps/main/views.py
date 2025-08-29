# Full version of views.py after creating subscribe and payment apps

from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Category, Post
from .serializers import (
    CategorySerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer
)
from .permissions import IsAuthorOrReadOnly


class CategoryListCreateView(generics.ListCreateAPIView):
    """API endpoint для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint для конкретной категории"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class PostListCreateView(generics.ListCreateAPIView):
    """
    API endpoint для постов c поддержкой закрепленных постов.
    Закрепленные посты отображаются первыми в порядке закрепления.
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        """Возвращает посты с учетом прав доступа"""

        queryset = Post.objects.select_related('author', 'category')

        # фильрация по правам доступа
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        else:
            queryset = queryset.filter(
                Q(status='published') | Q(author=self.request.user)
            )

        # Проверяем, нужна ли сортировка с учетом закрепленных постов
        ordering = self.request.query_params.get('ordering', '')
        show_pinned_first = not ordering or ordering in ['-created_at', 'created_at']
        
        if show_pinned_first:
            return Post.get_posts_for_feed().filter(
                Q(status='published') | (
                    Q(author=self.request.user) if self.request.user.is_authenticated else Q()
                )
            )

        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostListSerializer
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Статистика закрепленных постов
        if hasattr(response, 'data') and 'results' in response.data:
            pinned_count = sum(1 for post in response.data['results'] if post.get('is_pinned', False))
            response.data['pinned_posts_count'] = pinned_count
        
        return response

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint для конкретного поста"""
    queryset = Post.objects.select_related('author', 'category')
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Увеличивает счетчик просмотров при GET запросе"""
        instance = self.get_object()

        if request.method == 'GET':
            instance.increment_views()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
class MyPostsView(generics.ListAPIView):
    """API endpoint для постов текущего пользователя"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user
        ).select_related('author', 'category')
    

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_by_category(request, category_slug):
    """Посты определенной категории"""
    category = get_object_or_404(Category, slug=category_slug)
    
    # Получаем посты с учетом закрепления
    # Используем менеджер модели для получения with_subscription_info
    posts = Post.objects.with_subscription_info().filter(
        category=category,
        status='published'
    )
    
    # Сортируем с учетом закрепленных постов
    # Используем сложную аннотацию для правильной сортировки
    from django.db.models import Case, When, Value, DateTimeField, BooleanField
    from django.utils import timezone
    
    posts = posts.annotate(
        effective_date=Case(
            When(
                pin_info__isnull=False,
                pin_info__user__subscription__status='active',
                pin_info__user__subscription__end_date__gt=timezone.now(),
                then='pin_info__pinned_at'
            ),
            default='created_at',
            output_field=DateTimeField()
        ),
        is_pinned_flag=Case(
            When(
                pin_info__isnull=False,
                pin_info__user__subscription__status='active',
                pin_info__user__subscription__end_date__gt=timezone.now(),
                then=Value(True)
            ),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('-is_pinned_flag', 'effective_date', '-created_at')
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    
    return Response({
        'category': CategorySerializer(category).data,
        'posts': serializer.data,
        'pinned_posts_count': sum(1 for post in serializer.data if post.get('is_pinned', False))
    })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_posts(request):
    """10 самых популярных постов"""
    posts = Post.objects.with_subscription_info().filter(
        status='published'
    ).order_by('-views_count')[:10]
    
    serializer = PostListSerializer(
        posts, 
        many=True, 
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recent_posts(request):
    """10 последних опубликованных постов"""
    posts = Post.objects.with_subscription_info().filter(
        status='published'
    ).order_by('-created_at')[:10]
    
    serializer = PostListSerializer(
        posts, 
        many=True, 
        context={'request': request}
    )
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def pinned_posts_only(request):
    """Только закрепленные посты"""
    posts = Post.objects.pinned_posts()
    serializer = PostListSerializer(
        posts,
        many=True,
        context={'request': request}
    )
    return Response({
        'count': posts.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_posts(request):
    """
    Рекомендуемые посты для главной страницы:
    - Закрепленные посты (максимум 3)
    - Популярные посты за последнюю неделю
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Получаем последние 3 закрепленных поста
    pinned_posts = Post.objects.pinned_posts()[:3]
    
    # Получаем популярные посты за неделю (исключая уже закрепленные)
    week_ago = timezone.now() - timedelta(days=7)
    popular_posts = Post.objects.with_subscription_info().filter(
        status='published',
        created_at__gte=week_ago
    ).exclude(
        id__in=[post.id for post in pinned_posts]
    ).order_by('-views_count')[:6]
    
    # Сериализуем данные
    pinned_serializer = PostListSerializer(
        pinned_posts, 
        many=True, 
        context={'request': request}
    )
    popular_serializer = PostListSerializer(
        popular_posts, 
        many=True, 
        context={'request': request}
    )
    
    return Response({
        'pinned_posts': pinned_serializer.data,
        'popular_posts': popular_serializer.data,
        'total_pinned': Post.objects.pinned_posts().count()
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_post_pin_status(request, slug):
    """
    Переключает статус закрепления поста.
    Если пост закреплен - открепляет, если не закреплен - закрепляет.
    """
    post = get_object_or_404(Post, slug=slug, author=request.user, status='published')
    
    # Проверяем подписку
    if not hasattr(request.user, 'subscription') or not request.user.subscription.is_active:
        return Response({
            'error': 'Active subscription required to pin posts'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from apps.subscribe.models import PinnedPost
        
        # Проверяем, закреплен ли пост
        if post.is_pinned:
            # Открепляем
            post.pin_info.delete()
            message = 'Post unpinned successfully'
            is_pinned = False
        else:
            # Удаляем существующий закрепленный пост пользователя, если есть
            if hasattr(request.user, 'pinned_post'):
                request.user.pinned_post.delete()
            
            # Закрепляем новый пост
            PinnedPost.objects.create(user=request.user, post=post)
            message = 'Post pinned successfully'
            is_pinned = True
        
        return Response({
            'message': message,
            'is_pinned': is_pinned,
            'post': PostDetailSerializer(post, context={'request': request}).data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)









# Simplified version of views.py before creating subscribe and payment apps

# from rest_framework import generics, permissions, status, filters
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
# from django.db.models import Q
# from django.shortcuts import get_object_or_404

# from .models import Category, Post
# from .serializers import (
#     CategorySerializer,
#     PostListSerializer,
#     PostDetailSerializer,
#     PostCreateUpdateSerializer
# )
# from .permissions import IsAuthorOrReadOnly


# class CategoryListCreateView(generics.ListCreateAPIView):
#     """API endpoint for categories"""
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['name', 'description']
#     ordering_fields = ['name', 'created_at']
#     ordering = ['name']


# class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """API endpoint for specific category"""
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#     lookup_field = 'slug'


# class PostListCreateView(generics.ListCreateAPIView):
#     """API endpoint for posts list and creation"""
#     serializer_class = PostListSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['category', 'author', 'status']
#     search_fields = ['title', 'content']
#     ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
#     ordering = ['-created_at']

#     def get_queryset(self):
#         """Returns posts based on user permissions"""
#         queryset = Post.objects.select_related('author', 'category')

#         # Filter by access permissions
#         if not self.request.user.is_authenticated:
#             queryset = queryset.filter(status='published')
#         else:
#             # Authenticated users can see published posts and their own posts
#             queryset = queryset.filter(
#                 Q(status='published') | Q(author=self.request.user)
#             )

#         return queryset.order_by('-created_at')
    
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return PostCreateUpdateSerializer
#         return PostListSerializer
    
#     def perform_create(self, serializer):
#         """Set the author to the current user"""
#         serializer.save(author=self.request.user)


# class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """API endpoint for specific post"""
#     queryset = Post.objects.select_related('author', 'category')
#     serializer_class = PostDetailSerializer
#     permission_classes = [IsAuthorOrReadOnly]
#     lookup_field = 'slug'

#     def get_serializer_class(self):
#         if self.request.method in ['PUT', 'PATCH']:
#             return PostCreateUpdateSerializer
#         return PostDetailSerializer
    
#     def retrieve(self, request, *args, **kwargs):
#         """Increments view count on GET request"""
#         instance = self.get_object()

#         if request.method == 'GET':
#             instance.increment_views()

#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)
    

# class MyPostsView(generics.ListAPIView):
#     """API endpoint for current user's posts"""
#     serializer_class = PostListSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['category', 'status']
#     search_fields = ['title', 'content']
#     ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
#     ordering = ['-created_at']

#     def get_queryset(self):
#         return Post.objects.filter(
#             author=self.request.user
#         ).select_related('author', 'category')
    

# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def post_by_category(request, category_slug):
#     """Posts from specific category"""
#     category = get_object_or_404(Category, slug=category_slug)
    
#     posts = Post.objects.filter(
#         category=category,
#         status='published'
#     ).select_related('author', 'category').order_by('-created_at')
    
#     serializer = PostListSerializer(posts, many=True, context={'request': request})
    
#     return Response({
#         'category': CategorySerializer(category).data,
#         'posts': serializer.data,
#         'posts_count': len(serializer.data)
#     })


# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def popular_posts(request):
#     """10 most popular posts"""
#     posts = Post.objects.filter(
#         status='published'
#     ).select_related('author', 'category').order_by('-views_count')[:10]
    
#     serializer = PostListSerializer(posts, many=True, context={'request': request})
#     return Response(serializer.data)


# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def recent_posts(request):
#     """10 most recent published posts"""
#     posts = Post.objects.filter(
#         status='published'
#     ).select_related('author', 'category').order_by('-created_at')[:10]
    
#     serializer = PostListSerializer(posts, many=True, context={'request': request})
#     return Response(serializer.data)


# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def featured_posts(request):
#     """Featured posts based on view count"""
#     posts = Post.objects.filter(
#         status='published'
#     ).select_related('author', 'category').order_by('-views_count')[:9]
    
#     serializer = PostListSerializer(posts, many=True, context={'request': request})
#     return Response(serializer.data)


# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def pinned_posts_only(request):
#     """Pinned posts (returns most popular for now)"""
#     posts = Post.objects.filter(
#         status='published'
#     ).select_related('author', 'category').order_by('-views_count')[:5]
    
#     serializer = PostListSerializer(posts, many=True, context={'request': request})
#     return Response(serializer.data)
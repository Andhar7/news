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
    """API endpoint for categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for specific category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class PostListCreateView(generics.ListCreateAPIView):
    """API endpoint for posts list and creation"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        """Returns posts based on user permissions"""
        queryset = Post.objects.select_related('author', 'category')

        # Filter by access permissions
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        else:
            # Authenticated users can see published posts and their own posts
            queryset = queryset.filter(
                Q(status='published') | Q(author=self.request.user)
            )

        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostListSerializer
    
    def perform_create(self, serializer):
        """Set the author to the current user"""
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for specific post"""
    queryset = Post.objects.select_related('author', 'category')
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Increments view count on GET request"""
        instance = self.get_object()

        if request.method == 'GET':
            instance.increment_views()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

class MyPostsView(generics.ListAPIView):
    """API endpoint for current user's posts"""
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
    """Posts from specific category"""
    category = get_object_or_404(Category, slug=category_slug)
    
    posts = Post.objects.filter(
        category=category,
        status='published'
    ).select_related('author', 'category').order_by('-created_at')
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    
    return Response({
        'category': CategorySerializer(category).data,
        'posts': serializer.data,
        'posts_count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_posts(request):
    """10 most popular posts"""
    posts = Post.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-views_count')[:10]
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recent_posts(request):
    """10 most recent published posts"""
    posts = Post.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-created_at')[:10]
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_posts(request):
    """Featured posts based on view count"""
    posts = Post.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-views_count')[:9]
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def pinned_posts_only(request):
    """Pinned posts (returns most popular for now)"""
    posts = Post.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-views_count')[:5]
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)
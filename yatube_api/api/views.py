from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CommentSerializer, FollowSerializer,
                             GroupSerializer, PostSerializer)
from posts.models import Group, Post


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet постов:
    Поддерживает все CRUD запросы (action) к постам,
    в зависимости от пермишен
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet комментарий:
    Поддерживает все CRUD запросы (action) к постам с комментариями,
    в зависимости от пермишен
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    # переопределяем объект запроса.
    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return post.comments.all()

    # переопределяем объект создания action.
    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(post=post)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet групп постов(только для чтения):
    1. Cписок групп (List());
    2. О конкретной группе по id (retrieve()).
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """ViewSet подписки (только для авторизованных пользователей):
    1. Cписок на подписанных авторов (List());
    2. Подписаться на автора (create()).
    """
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    # переопределяем объект запроса.
    def get_queryset(self):
        return self.request.user.follower.all()

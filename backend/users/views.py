from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from users.models import Subscription, User
from users.serializers import SubShowSerializer


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация для списка подписок."""
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class CustomUserViewSet(UserViewSet):
    """Кастомный ViewSet для работы с пользователями и подписками."""

    pagination_class = CustomPagination

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Обрабатывает подписку и отписку от пользователя."""
        author = get_object_or_404(User, id=id)
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'error': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=user, author=author)
            serializer = SubShowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(user=user, author=author).first()
            if not subscription:
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        """Возвращает список подписок текущего пользователя."""
        user = request.user
        subscribed_authors = User.objects.filter(
            subscribed__user=user
        ).prefetch_related('recipes')
        page = self.paginate_queryset(subscribed_authors)
        if page is not None:
            serializer = SubShowSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubShowSerializer(
            subscribed_authors, many=True, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

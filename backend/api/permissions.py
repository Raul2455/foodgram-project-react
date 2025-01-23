from rest_framework import permissions

class AdminOrReadOnlyPermission(permissions.BasePermission):
    """
    Разрешение, которое позволяет:
    - Чтение (GET, HEAD, OPTIONS) для всех пользователей.
    - Изменение (POST, PUT, PATCH, DELETE) только для администраторов.
    """

    def has_permission(self, request, view):
        # Разрешить чтение для всех пользователей
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить изменение только для администраторов
        return request.user and request.user.is_staff


class AuthorAdminOrReadOnlyPermission(permissions.BasePermission):
    """
    Разрешение, которое позволяет:
    - Чтение (GET, HEAD, OPTIONS) для всех пользователей.
    - Изменение (POST, PUT, PATCH, DELETE) только для автора объекта или администраторов.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить чтение для всех пользователей
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить изменение только для автора объекта или администраторов
        return obj.author == request.user or request.user.is_staff
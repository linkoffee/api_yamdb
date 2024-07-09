from rest_framework import permissions

from reviews.models import MyUser


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


# вроде как пользователей могут удалять только админы(кроме самих себя)
class UserRolePermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        если не работает, попробуйте написать роли с заглавной буквы
        использовать с моделью пользователя
        """
        if request.user.role == 'admin' or request.user.is_staff == 1:
            if request.method == 'DELETE' and obj.model == MyUser:
                return obj.id != request.user.id
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        return False


class RolePermissions(permissions.BasePermission):
    """с другими моделями"""

    def has_object_permission(self, request, view, obj):
        """если не работает, попробуйте написать роли с заглавной буквы"""
        if request.user.role == 'admin' or request.user.is_staff == 1:
            return True
        if request.user.role == 'moderator':
            ...
        if request.user.role == 'user':   # сейчас у меня в бд роль называется 'U'
            # но если сделать миграции и заполнить бд заново, то должно быть это
            ...
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.author == request.user
        return False

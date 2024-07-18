from rest_framework import permissions


class IsAdminOrStaffPermission(permissions.BasePermission):
    """Разрешает доступ администраторам или уполномоченным сотрудникам."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorOrModerPermission(permissions.BasePermission):
    """
    Разрешает доступ авторам объектов или модераторам.
    Позволяет безопасные методы всем пользователям.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or (request.user.is_authenticated and (
                request.user.is_admin
                or request.user.is_moderator)
                )
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает полный доступ администраторам.
    Позволяет только чтение другим пользователям.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_admin)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_admin)
        )

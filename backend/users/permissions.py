from rest_framework import permissions

from .models import RoleType


class AnonCreateAndUpdateOwnerOrAdminUserOnly(permissions.BasePermission):
    """
    Custom permission:
        - allow anonymous POST
        - allow authenticated GET and PUT on *own* record
        - allow all actions for users with ADMIN role
    """

    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        else:
            if request.user.is_authenticated:
                is_admin = request.user.roles.filter(
                    id=RoleType.ADMIN.value,
                ).first()
                return bool(is_admin)
            else:
                return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            is_admin = request.user.roles.filter(
                id=RoleType.ADMIN.value).first()
            if is_admin:
                return True
            else:
                return obj.id == request.user.id
        return False


class AdminOrOwnerUserOnly(permissions.BasePermission):
    """
    Custom permission:
        - allow authenticated GET and PUT on *own* record
        - allow all actions for users with ADMIN role
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated:
            is_admin = request.user.roles.filter(
                id=RoleType.ADMIN.value,
            ).first()
            return bool(is_admin)
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            is_admin = request.user.roles.filter(
                id=RoleType.ADMIN.value,
            ).first()
            if is_admin:
                return True
            else:
                return obj.id == request.user.id


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
        - allow SAFE_METHODS for all users
        - allow all actions for users with ADMIN role
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            is_admin = request.user.roles.filter(
                id=RoleType.ADMIN.value,
            ).first()
            return bool(is_admin)

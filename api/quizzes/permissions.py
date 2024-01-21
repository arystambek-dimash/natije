from datetime import datetime

from rest_framework import permissions, exceptions
from social_core.pipeline import user


class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS:
            if obj.is_trial:
                return True
            else:
                user_profile = getattr(request.user, 'profile', None)
                if user_profile and user_profile.test_limit.timestamp() - datetime.now().timestamp() > 0:
                    return True
                else:
                    return False


class IsBoughtUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS:
            if obj.is_trial:
                return True
            else:
                user_profile = getattr(request.user, 'profile', None)
                if user_profile and user_profile.test_limit.timestamp() - datetime.now().timestamp() > 0:
                    return True
                else:
                    return False


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

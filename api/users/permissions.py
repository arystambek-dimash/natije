from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsTeacherUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user and user.role.name == "teacher":
            return True
        else:
            raise PermissionDenied("You don't have permission to access this page")


class IsOwnerUser(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.user == user

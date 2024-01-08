from rest_framework import permissions
from rest_framework.permissions import BasePermission

from api.users.permissions import IsOwnerUser


class IsBoughtUserOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.is_prime:
            return True
        if request.user in obj.course_theme.course.bought_users.all():
            return True
        return False

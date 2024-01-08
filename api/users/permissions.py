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
    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(obj, "user") and obj.user == user:
            return True
        elif hasattr(obj, "course") and obj.course.user == user:
            return True
        elif hasattr(obj, "course_theme") and obj.course_theme.course.user == user:
            return True
        elif hasattr(obj, "lesson") and obj.lesson.course_theme.course.user == user:
            return True

        return False

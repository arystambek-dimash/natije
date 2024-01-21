from rest_framework.permissions import BasePermission
from .models import BoughtCourse


class IsBoughtOrFree(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.is_prime:
            return True
        return request.user in BoughtCourse.objects.filter(course=obj).exists()

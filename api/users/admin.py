from django.contrib import admin

from api.users.models import Role,Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model


class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    ordering = ['email']
    search_fields = ('email',)
    list_display = ['email', 'first_name', 'last_name', 'role']
    list_filter = ('is_active', 'is_staff', 'is_superuser')


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(Role)
admin.site.register(Profile)

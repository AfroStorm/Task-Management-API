from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

user = get_user_model()


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(user, CustomUserAdmin)

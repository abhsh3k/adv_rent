from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from toolx.admin import admin_site 

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'id_document']
    list_filter = ['is_verified', 'role']
    fieldsets = UserAdmin.fieldsets + (
        ('ToolX Profile', {'fields': ('role', 'phone', 'id_document', 'is_verified')}),
    )

# Use this instead of the @ decorator
admin_site.register(User, CustomUserAdmin)
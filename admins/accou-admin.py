from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from toolx.admin import admin_site 

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'id_document', 'date_joined']
    list_filter = ['is_verified', 'role']
    list_editable = ['is_verified']
    
    # Adding the ToolX specific fields to the edit page
    fieldsets = UserAdmin.fieldsets + (
        ('ToolX Profile', {'fields': (
            'role', 'phone', 'bio', 'avatar',
            'id_document', 'is_verified', 'terms_accepted',
            'telegram_chat_id', 'telegram_username',
            'email_verified',
        )}),
    )

# Explicitly register to your custom admin_site instance
admin_site.register(User, CustomUserAdmin)
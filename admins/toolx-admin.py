from django.contrib import admin
from django.contrib.auth import get_user_model

class ToolXAdminSite(admin.AdminSite):
    site_header = "ToolX Admin"
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        User = get_user_model()
        
        # Pulling real data for your index.html
        extra_context['total_users'] = User.objects.count()
        # Ensure this matches the variable in your index.html
        extra_context['unverified_users'] = User.objects.filter(is_verified=False).count()
        
        return super().index(request, extra_context)

admin_site = ToolXAdminSite(name='toolx_admin')
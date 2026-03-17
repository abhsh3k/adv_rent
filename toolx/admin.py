from django.contrib import admin
from django.apps import apps

class ToolXAdminSite(admin.AdminSite):
    site_header = "ToolX Admin"
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # We look these up ONLY when the page loads, not when the server starts
        User = apps.get_model('accounts', 'User')
        Tool = apps.get_model('tools', 'Tool')
        
        extra_context['total_users'] = User.objects.count()
        extra_context['unverified_users'] = User.objects.filter(is_verified=False).count()
        extra_context['total_tools'] = Tool.objects.count()
        
        return super().index(request, extra_context)

# This is the ONLY thing other files should touch
admin_site = ToolXAdminSite(name='toolx_admin')
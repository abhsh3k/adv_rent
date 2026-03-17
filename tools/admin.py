from django.contrib import admin
from toolx.admin import admin_site
from .models import Tool, Category

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')

class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'daily_rate', 'is_available')
    list_filter = ('category', 'is_available')

# Register at the VERY BOTTOM
admin_site.register(Category, CategoryAdmin)
admin_site.register(Tool, ToolAdmin)
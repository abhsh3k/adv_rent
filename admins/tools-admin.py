from django.contrib import admin
from toolx.admin import admin_site
from .models import Tool, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')



@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    # What you see in the main list
    list_display = ('name', 'owner', 'category', 'daily_rate', 'is_available', 'created_at')
    
    # Filters on the right side
    list_filter = ('category', 'condition', 'is_available', 'created_at')
    
    # Search functionality
    search_fields = ('name', 'description', 'owner__username', 'location')
    
    # Quick edit from the list view
    list_editable = ('daily_rate', 'is_available')
    
    # Organize the detail view
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'description', 'category', 'condition')
        }),
        ('Pricing & Availability', {
            'fields': ('daily_rate', 'is_available')
        }),
        ('Location & Media', {
            'fields': ('location', 'image', ('latitude', 'longitude'))
        }),
    )

admin_site.register(Tool)

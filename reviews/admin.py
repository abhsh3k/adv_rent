from django.contrib import admin
from toolx.admin import admin_site
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['tool', 'reviewer', 'rating']

admin_site.register(Review, ReviewAdmin)
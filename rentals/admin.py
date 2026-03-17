from django.contrib import admin
from toolx.admin import admin_site
from .models import Rental

class RentalAdmin(admin.ModelAdmin):
    list_display = ['tool', 'renter', 'status']

admin_site.register(Rental, RentalAdmin)
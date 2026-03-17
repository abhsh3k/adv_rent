from django.contrib import admin
from .models import Rental, Message

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['tool', 'renter', 'start_date', 'end_date', 'status', 'total_cost']
    list_filter  = ['status']
    search_fields = ['tool__name', 'renter__username']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'rental', 'body', 'is_read', 'created_at']
    list_filter  = ['is_read']
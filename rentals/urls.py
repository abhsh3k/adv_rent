from django.urls import path
from . import views

urlpatterns = [
    path('rent/<int:pk>/', views.rent_tool, name='rent_tool'),
    path('rental/<int:pk>/thread/', views.rental_thread, name='rental_thread'),  
    path('rental/<int:pk>/<str:action>/', views.rental_action, name='rental_action'),
    path('inbox/', views.inbox, name='inbox'),
]
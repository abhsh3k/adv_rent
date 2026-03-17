from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tools/', views.tool_list, name='tool_list'),
    path('tools/<int:pk>/', views.tool_detail, name='tool_detail'),
    path('tools/add/', views.tool_add, name='tool_add'),
    path('tools/<int:pk>/edit/', views.tool_edit, name='tool_edit'),
    path('tools/<int:pk>/delete/', views.tool_delete, name='tool_delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('review/<int:rental_pk>/', views.add_review, name='add_review'),
]
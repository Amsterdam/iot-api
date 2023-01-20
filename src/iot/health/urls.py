from django.urls import path

from . import views

urlpatterns = [
    path(r'health/', views.health, name='health'),
]

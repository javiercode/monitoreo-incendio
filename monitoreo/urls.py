# monitoreo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mapa/', views.mapa, name='mapa'),
    path('api/incendios/', views.api_incendios, name='api_incendios'),
]
# monitoreo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mapa/', views.mapa, name='mapa'),
    path('api/incendios/', views.api_incendios, name='api_incendios'),
    path('mapa-avanzado/', views.mapa_avanzado, name='mapa_avanzado'),
    path('api/incendios/json/', views.api_incendios_json, name='api_incendios_json'),
]
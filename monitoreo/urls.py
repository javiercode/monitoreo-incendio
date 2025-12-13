# monitoreo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mapa/', views.mapa, name='mapa'),
    path('api/incendios/', views.api_incendios, name='api_incendios'),
    path('mapa-avanzado/', views.mapa_avanzado, name='mapa_avanzado'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/incendios/', views.api_incendios, name='api_incendios'),
    path('api/incendios/json/', views.api_incendios_json, name='api_incendios_json'),
    path('api/nasa/actualizar/', views.actualizar_datos_nasa, name='actualizar_nasa'),
    path('api/nasa/estado/', views.estado_actualizacion, name='estado_nasa'),
]
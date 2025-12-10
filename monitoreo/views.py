# monitoreo/views.py - Versión segura
from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    """Página principal - versión segura sin dependencias de modelo"""
    return render(request, 'monitoreo/index.html', {
        'title': 'Sistema de Monitoreo de Incendios - Bolivia'
    })

def mapa(request):
    """Mapa de incendios"""
    return render(request, 'monitoreo/mapa.html', {
        'title': 'Mapa de Incendios Forestales'
    })

def api_incendios(request):
    """API de datos de incendios - versión básica"""
    data = {
        'status': 'ok',
        'message': 'API de incendios funcionando',
        'system': 'Django + Spatialite + GDAL',
        'endpoints': {
            'incendios': '/api/incendios/',
            'mapa': '/mapa/',
            'admin': '/admin/',
        }
    }
    return JsonResponse(data)
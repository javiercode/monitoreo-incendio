# monitoreo/views.py - Versión segura
import folium
from folium.plugins import HeatMap, MeasureControl, Geocoder
from django.shortcuts import render
from django.http import JsonResponse
import json

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

def mapa_avanzado(request):
    """Mapa interactivo con Folium - VERSIÓN CORREGIDA"""
    
    # Crear mapa centrado en Bolivia
    m = folium.Map(
        location=[-16.5, -64.5],
        zoom_start=6,
        tiles='OpenStreetMap',
        width='100%',
        height='700px',
        control_scale=True
    )
    
    # Datos de ejemplo (más tarde vendrán de tu base de datos)
    incendios_ejemplo = [
        {'nombre': 'Incendio La Paz', 'lat': -16.5, 'lon': -68.2, 'intensidad': 0.8, 'severidad': 'alto'},
        {'nombre': 'Incendio Santa Cruz', 'lat': -17.8, 'lon': -63.2, 'intensidad': 0.9, 'severidad': 'critico'},
        {'nombre': 'Incendio Cochabamba', 'lat': -17.4, 'lon': -66.2, 'intensidad': 0.6, 'severidad': 'medio'},
        {'nombre': 'Incendio Tarija', 'lat': -21.5, 'lon': -64.7, 'intensidad': 0.7, 'severidad': 'alto'},
    ]
    
    # Agregar cada incendio como marcador
    for incendio in incendios_ejemplo:
        # Determinar color según severidad
        color_map = {
            'bajo': 'green',
            'medio': 'orange', 
            'alto': 'red',
            'critico': 'darkred'
        }
        color = color_map.get(incendio['severidad'], 'red')
        
        # Crear popup con información
        popup_html = f"""
        <div style="min-width: 200px;">
            <h5><b>{incendio['nombre']}</b></h5>
            <hr>
            <p><b>Severidad:</b> {incendio['severidad'].title()}</p>
            <p><b>Intensidad:</b> {incendio['intensidad']:.2f}</p>
            <p><b>Coordenadas:</b><br>{incendio['lat']:.4f}, {incendio['lon']:.4f}</p>
        </div>
        """
        
        # Agregar marcador
        folium.Marker(
            location=[incendio['lat'], incendio['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{incendio['nombre']} - {incendio['severidad'].title()}",
            icon=folium.Icon(color=color, icon='fire', prefix='fa')
        ).add_to(m)
    
    # Agregar capa de calor
    heat_data = []
    for incendio in incendios_ejemplo:
        # Peso basado en intensidad
        weight = incendio['intensidad'] * 10
        heat_data.append([incendio['lat'], incendio['lon'], weight])
    
    HeatMap(heat_data, radius=15, blur=10, max_zoom=10).add_to(m)
    
    # Agregar controles de capas
    folium.TileLayer('cartodbpositron').add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    folium.TileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Satélite',
        attr='Esri'
    ).add_to(m)
    
    # Agregar controles
    folium.LayerControl().add_to(m)
    MeasureControl(position='bottomleft').add_to(m)
    Geocoder().add_to(m)
    
    # Agregar polígono de Bolivia (simplificado)
    bolivia_coords = [
        [-22.9, -69.6],
        [-22.9, -57.5],
        [-9.7, -57.5],
        [-9.7, -69.6]
    ]
    
    folium.Polygon(
        locations=bolivia_coords,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.1,
        weight=2,
        popup='<b>Bolivia</b><br>Área de monitoreo'
    ).add_to(m)
    
    # Convertir mapa a HTML
    mapa_html = m._repr_html_()
    
    # Estadísticas
    estadisticas = {
        'total_incendios': len(incendios_ejemplo),
        'activos': len(incendios_ejemplo),  # Todos activos en ejemplo
        'area_total': 1500.5,  # Ejemplo
        'por_departamento': {
            'La Paz': 1,
            'Santa Cruz': 1,
            'Cochabamba': 1,
            'Tarija': 1
        }
    }
    
    return render(request, 'monitoreo/mapa_avanzado.html', {
        'mapa_html': mapa_html,
        'estadisticas': estadisticas,
        'title': 'Mapa Interactivo de Incendios'
    })

def api_incendios_json(request):
    """API que devuelve incendios en formato JSON (sin GeoJSON por ahora)"""
    # Datos de ejemplo
    datos = {
        'status': 'ok',
        'incendios': [
            {
                'id': 1,
                'nombre': 'Incendio La Paz',
                'latitud': -16.5,
                'longitud': -68.2,
                'intensidad': 0.8,
                'severidad': 'alto',
                'departamento': 'La Paz'
            },
            {
                'id': 2,
                'nombre': 'Incendio Santa Cruz',
                'latitud': -17.8,
                'longitud': -63.2,
                'intensidad': 0.9,
                'severidad': 'critico',
                'departamento': 'Santa Cruz'
            }
        ],
        'metadata': {
            'total': 2,
            'fuente': 'Datos de ejemplo',
            'actualizado': '2024-12-10'
        }
    }
    
    return JsonResponse(datos)
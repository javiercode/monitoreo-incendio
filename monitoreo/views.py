# monitoreo/views.py - Versión segura
import folium
from folium.plugins import HeatMap, MeasureControl, Geocoder
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from monitoreo.utils.nasa_firms import NASAFirmsUpdater
from decouple import config
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
import pandas as pd
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

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

@csrf_exempt
@login_required
def actualizar_datos_nasa(request):
    """Endpoint para actualizar datos desde NASA FIRMS"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        api_key = config('NASA_FIRMS_API_KEY', default=None)
        if not api_key:
            return JsonResponse({'error': 'API Key no configurada'}, status=500)
        
        updater = NASAFirmsUpdater(api_key=api_key)
        
        # Obtener parámetros
        days = int(request.POST.get('days', 7))
        
        # Ejecutar actualización
        resultados = updater.ejecutar_actualizacion(days=days)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Datos actualizados correctamente',
            'resultados': resultados,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def estado_actualizacion(request):
    """Muestra estado de la última actualización"""
    from monitoreo.models import IncendioForestal
    
    # Obtener estadísticas
    total = IncendioForestal.objects.count()
    activos = IncendioForestal.objects.filter(estado='activo').count()
    ultimo = IncendioForestal.objects.order_by('-fecha_deteccion').first()
    
    return JsonResponse({
        'status': 'ok',
        'estadisticas': {
            'total_incendios': total,
            'activos': activos,
            'ultima_actualizacion': ultimo.fecha_deteccion.isoformat() if ultimo else None,
            'api_key_configurada': bool(config('NASA_FIRMS_API_KEY', default=None))
        }
    })

def dashboard(request):
    """Dashboard con gráficos de datos reales"""
    
    from monitoreo.models import IncendioForestal, Departamento
    
    # Obtener datos
    incendios = IncendioForestal.objects.all()
    
    # Gráfico 1: Incendios por departamento (TOP 5)
    depto_data = list(incendios.values('departamento__nombre').annotate(
        total=Count('id'),
        area_total=Sum('area_afectada_ha')
    ).order_by('-total')[:5])
    
    if depto_data:
        fig1 = go.Figure(data=[
            go.Bar(
                x=[d['departamento__nombre'] or 'Sin departamento' for d in depto_data],
                y=[d['total'] for d in depto_data],
                text=[d['total'] for d in depto_data],
                textposition='auto',
                marker_color='crimson'
            )
        ])
        fig1.update_layout(
            title='Top 5 Departamentos con más Incendios',
            xaxis_title="Departamento",
            yaxis_title="Número de Incendios",
            template="plotly_white"
        )
        grafico1 = plot(fig1, output_type='div', include_plotlyjs=False)
    else:
        grafico1 = "<p class='text-muted'>No hay datos para mostrar</p>"
    
    # Gráfico 2: Distribución por severidad
    severidad_data = list(incendios.values('severidad').annotate(total=Count('id')))
    
    if severidad_data:
        labels = [d['severidad'].title() for d in severidad_data]
        values = [d['total'] for d in severidad_data]
        
        colors = {'bajo': 'green', 'medio': 'yellow', 'alto': 'orange', 'critico': 'red'}
        color_sequence = [colors.get(sev.lower(), 'gray') for sev in labels]
        
        fig2 = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            marker=dict(colors=color_sequence)
        )])
        fig2.update_layout(title='Distribución por Severidad')
        grafico2 = plot(fig2, output_type='div', include_plotlyjs=False)
    else:
        grafico2 = "<p class='text-muted'>No hay datos para mostrar</p>"
    
    # Gráfico 3: Tendencia de últimos 30 días
    fecha_limite = timezone.now() - timedelta(days=30)
    tendencia_raw = incendios.filter(
        fecha_deteccion__gte=fecha_limite
    ).extra({
        'fecha': "date(fecha_deteccion)"
    }).values('fecha').annotate(total=Count('id')).order_by('fecha')
    
    if tendencia_raw:
        tendencia_df = pd.DataFrame(list(tendencia_raw))
        
        fig3 = px.line(
            tendencia_df,
            x='fecha',
            y='total',
            title='Tendencia de Incendios (Últimos 30 días)',
            markers=True,
            line_shape='spline'
        )
        fig3.update_traces(line=dict(color='firebrick', width=3))
        fig3.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Número de Incendios"
        )
        grafico3 = plot(fig3, output_type='div', include_plotlyjs=False)
    else:
        grafico3 = "<p class='text-muted'>No hay datos para mostrar</p>"
    
    # Estadísticas generales
    estadisticas = {
        'total_incendios': incendios.count(),
        'activos': incendios.filter(estado='activo').count(),
        'area_total': incendios.aggregate(Sum('area_afectada_ha'))['area_afectada_ha__sum'] or 0,
        'promedio_intensidad': incendios.aggregate(Avg('intensidad'))['intensidad__avg'] or 0,
        'incendios_hoy': incendios.filter(
            fecha_deteccion__date=timezone.now().date()
        ).count(),
        'departamento_mas_afectado': depto_data[0]['departamento__nombre'] if depto_data else 'N/A',
        'ultima_actualizacion': incendios.order_by('-fecha_ultima_actualizacion').first().fecha_ultima_actualizacion 
                               if incendios.exists() else None,
    }
    
    # Incendios más recientes
    incendios_recientes = incendios.order_by('-fecha_deteccion')[:10]
    
    return render(request, 'monitoreo/dashboard.html', {
        'grafico1': grafico1,
        'grafico2': grafico2,
        'grafico3': grafico3,
        'estadisticas': estadisticas,
        'incendios_recientes': incendios_recientes,
        'title': 'Dashboard de Monitoreo en Tiempo Real',
        'api_key_configurada': bool(config('NASA_FIRMS_API_KEY', default=None))
    })
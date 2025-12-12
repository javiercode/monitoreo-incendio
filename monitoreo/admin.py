# monitoreo/admin.py
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Departamento, IncendioForestal
import folium
from django.utils.safestring import mark_safe

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'capital', 'area_km2']
    search_fields = ['nombre', 'capital']
    list_filter = ['nombre']

@admin.register(IncendioForestal)
class IncendioForestalAdmin(GISModelAdmin):  # ¡Usa GISModelAdmin!
    list_display = ['nombre', 'departamento', 'fecha_deteccion', 'severidad', 'estado', 'area_afectada_ha']
    list_filter = ['estado', 'severidad', 'departamento', 'fecha_deteccion', 'satelite']
    search_fields = ['nombre', 'departamento__nombre', 'notas']
    readonly_fields = ['fecha_ultima_actualizacion', 'mapa_preview']
    
    # Campos organizados en pestañas
    fieldsets = [
        ('Información Básica', {
            'fields': ['nombre', 'departamento', 'estado', 'severidad']
        }),
        ('Ubicación Geoespacial', {
            'fields': ['ubicacion', 'mapa_preview']
        }),
        ('Métricas del Incendio', {
            'fields': ['intensidad', 'area_afectada_ha', 'confianza_deteccion']
        }),
        ('Datos Satelitales', {
            'fields': ['satelite', 'brillo_temperatura', 'pixel_size', 'fuente_datos']
        }),
        ('Fechas', {
            'fields': ['fecha_deteccion', 'fecha_ultima_actualizacion']
        }),
        ('Archivos', {
            'fields': ['imagen_satelital', 'reporte_pdf', 'notas']
        }),
    ]
    
    def mapa_preview(self, obj):
        """Muestra un pequeño mapa en el admin"""
        if obj.ubicacion:
            # Crear mapa centrado en la ubicación
            m = folium.Map(
                location=[obj.ubicacion.y, obj.ubicacion.x],
                zoom_start=10,
                width='100%',
                height='300px'
            )
            
            # Agregar marcador
            folium.Marker(
                [obj.ubicacion.y, obj.ubicacion.x],
                popup=f"<b>{obj.nombre}</b><br>Intensidad: {obj.intensidad}",
                icon=folium.Icon(color='red', icon='fire', prefix='fa')
            ).add_to(m)
            
            return mark_safe(m._repr_html_())
        return "Sin ubicación"
    
    mapa_preview.short_description = "Vista previa del mapa"
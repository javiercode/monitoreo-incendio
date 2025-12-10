# views.py
import requests
import geopandas as gpd
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from .models import IncendioForestal
from shapely.geometry import Point
import json
from datetime import datetime, timedelta

class IncendioAPIView(View):
    def get(self, request):
        """Obtiene datos actualizados de incendios"""
        
        # URL de API de FIRMS NASA (datos de incendios activos)
        api_url = "https://firms.modaps.eosdis.nasa.gov/api/country/csv"
        
        # Parámetros para Bolivia
        params = {
            'country': 'BOL',
            'source': 'MODIS_NRT',
            'days': 7  # Últimos 7 días
        }
        
        try:
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                # Procesar datos CSV
                df = pd.read_csv(pd.compat.StringIO(response.text))
                
                # Filtrar para Bolivia
                df_bolivia = df[
                    (df['latitude'].between(-22.9, -9.7)) & 
                    (df['longitude'].between(-69.6, -57.5))
                ]
                
                # Guardar en la base de datos
                self.guardar_incendios(df_bolivia)
                
                return JsonResponse({
                    'status': 'success',
                    'incendios_detectados': len(df_bolivia),
                    'data': df_bolivia.to_dict('records')
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def guardar_incendios(self, df):
        """Guarda los incendios en la base de datos"""
        for _, row in df.iterrows():
            IncendioForestal.objects.update_or_create(
                nombre=f"Incendio_{row['acq_date']}_{row['acq_time']}",
                defaults={
                    'fecha_deteccion': datetime.strptime(
                        f"{row['acq_date']} {row['acq_time']}", 
                        '%Y-%m-%d %H%M'
                    ),
                    'coordenadas': f"POINT({row['longitude']} {row['latitude']})",
                    'intensidad': row['brightness'] / 500,  # Normalizado
                    'area_afectada': row['frp'] * 0.1,  # Estimación
                    'departamento': self.identificar_departamento(
                        row['latitude'], 
                        row['longitude']
                    ),
                    'municipio': 'Por determinar',
                    'fuente_datos': 'MODIS'
                }
            )
    
    def identificar_departamento(self, lat, lon):
        """Identifica el departamento basado en coordenadas"""
        # Diccionario simplificado de departamentos de Bolivia
        departamentos = {
            'La Paz': {'min_lat': -17.5, 'max_lat': -12.0, 'min_lon': -69.5, 'max_lon': -66.0},
            'Cochabamba': {'min_lat': -18.5, 'max_lat': -15.5, 'min_lon': -66.5, 'max_lon': -63.5},
            'Santa Cruz': {'min_lat': -20.0, 'max_lat': -13.5, 'min_lon': -64.5, 'max_lon': -57.5},
            # ... agregar más departamentos
        }
        
        for depto, limites in departamentos.items():
            if (limites['min_lat'] <= lat <= limites['max_lat'] and
                limites['min_lon'] <= lon <= limites['max_lon']):
                return depto
        
        return 'No identificado'
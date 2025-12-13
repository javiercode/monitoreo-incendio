# monitoreo/utils/nasa_firms.py
import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from django.contrib.gis.geos import Point
from decouple import config
import time
import logging

logger = logging.getLogger(__name__)

class NASAFirmsUpdater:
    def __init__(self, api_key=None):
        self.api_key = api_key or config('NASA_FIRMS_API_KEY', default=None)
        self.base_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
        
        # Bounding Box de Bolivia
        self.bolivia_bbox = {
            'min_lon': -69.6,
            'min_lat': -22.9,
            'max_lon': -57.5,
            'max_lat': -9.7
        }
        
        # Mapeo de departamentos aproximado
        self.departamentos_coords = {
            'La Paz': {'min_lat': -17.5, 'max_lat': -12.0, 'min_lon': -69.5, 'max_lon': -66.0},
            'Cochabamba': {'min_lat': -18.5, 'max_lat': -15.5, 'min_lon': -66.5, 'max_lon': -63.5},
            'Santa Cruz': {'min_lat': -20.0, 'max_lat': -13.5, 'min_lon': -64.5, 'max_lon': -57.5},
            'Oruro': {'min_lat': -19.5, 'max_lat': -17.0, 'min_lon': -68.5, 'max_lon': -65.5},
            'Potosi': {'min_lat': -22.9, 'max_lat': -17.5, 'min_lon': -68.0, 'max_lon': -64.5},
            'Tarija': {'min_lat': -22.5, 'max_lat': -20.5, 'min_lon': -65.0, 'max_lon': -62.5},
            'Chuquisaca': {'min_lat': -21.0, 'max_lat': -18.5, 'min_lon': -65.5, 'max_lon': -62.0},
            'Beni': {'min_lat': -15.0, 'max_lat': -10.0, 'min_lon': -68.0, 'max_lon': -62.0},
            'Pando': {'min_lat': -12.0, 'max_lat': -9.7, 'min_lon': -70.0, 'max_lon': -64.5},
        }
    
    # monitoreo/utils/nasa_firms.py - VERSIÓN FINAL CORREGIDA
    def obtener_datos_nasa(self, days=1, source='MODIS_NRT'):
        """Obtiene datos de incendios de NASA FIRMS"""
        
        if not self.api_key:
            logger.error("API Key de NASA FIRMS no configurada")
            return pd.DataFrame()
        
        try:
            # URL directa (formato de NASA FIRMS)
            url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{self.api_key}/{source}/{self.bolivia_bbox['min_lat']},{self.bolivia_bbox['min_lon']},{self.bolivia_bbox['max_lat']},{self.bolivia_bbox['max_lon']}/{days}"
            
            logger.info(f"Consultando NASA FIRMS API...")
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Error HTTP {response.status_code}")
                return pd.DataFrame()
            
            # Verificar si hay contenido
            content = response.text.strip()
            if not content or len(content) < 100:
                logger.info("✅ No hay incendios detectados en el área especificada")
                return pd.DataFrame()
            
            # Parsear CSV - FORMA ROBUSTA
            # NASA FIRMS CSV tiene 14 columnas fijas
            try:
                df = pd.read_csv(
                    StringIO(content),
                    dtype={'acq_time': str}  # Mantener ceros a la izquierda
                )
            except pd.errors.ParserError:
                # Intentar con engine python para mejor manejo de errores
                df = pd.read_csv(
                    StringIO(content),
                    engine='python',
                    on_bad_lines='skip'
                )
            
            # Verificar que tenemos las columnas mínimas
            required_columns = ['latitude', 'longitude', 'acq_date', 'acq_time']
            missing = [col for col in required_columns if col not in df.columns]
            
            if missing:
                logger.error(f"Faltan columnas requeridas: {missing}")
                logger.info(f"Columnas disponibles: {df.columns.tolist()}")
                return pd.DataFrame()
            
            # Limpiar datos
            df = df.dropna(subset=['latitude', 'longitude'])
            
            if df.empty:
                logger.info("✅ CSV parseado pero sin datos válidos")
                return pd.DataFrame()
            
            logger.info(f"✅ {len(df)} incendios obtenidos exitosamente")
            return df
            
        except Exception as e:
            logger.error(f"Error en obtener_datos_nasa: {str(e)}")
            return pd.DataFrame()
    
    def identificar_departamento(self, lat, lon):
        """Identifica departamento basado en coordenadas"""
        from monitoreo.models import Departamento
        
        for depto_nombre, limites in self.departamentos_coords.items():
            if (limites['min_lat'] <= lat <= limites['max_lat'] and
                limites['min_lon'] <= lon <= limites['max_lon']):
                
                # Buscar o crear departamento
                depto, created = Departamento.objects.get_or_create(
                    nombre=depto_nombre,
                    defaults={'codigo': depto_nombre[:2].upper()}
                )
                return depto
        
        return None
    
    def procesar_incendios(self, df):
        """Procesa DataFrame y actualiza base de datos"""
        from monitoreo.models import IncendioForestal
        
        if df.empty:
            logger.warning("DataFrame vacío, nada que procesar")
            return 0, 0
        
        nuevos = 0
        actualizados = 0
        
        for _, row in df.iterrows():
            try:
                # Crear ID único para el incendio
                fire_id = f"{row['latitude']:.4f}_{row['longitude']:.4f}_{row['acq_date']}_{row['acq_time']}"
                
                # Crear nombre descriptivo
                nombre = f"Incendio_{row['acq_date']}_{row['acq_time'][:2]}h"
                
                # Identificar departamento
                departamento = self.identificar_departamento(row['latitude'], row['longitude'])
                
                # Calcular métricas
                intensidad = min(row.get('brightness', 300) / 500, 1.0)
                
                if intensidad < 0.3:
                    severidad = 'bajo'
                elif intensidad < 0.6:
                    severidad = 'medio'
                elif intensidad < 0.8:
                    severidad = 'alto'
                else:
                    severidad = 'critico'
                
                # Estimar área afectada basada en FRP (Fire Radiative Power)
                area_estimada = row.get('frp', 0) * 0.15  # Conversión aproximada
                
                # Crear fecha de detección
                fecha_deteccion = datetime.strptime(
                    f"{row['acq_date']} {str(row['acq_time']).zfill(4)}", 
                    '%Y-%m-%d %H%M'
                )
                
                # Buscar si ya existe un incendio similar
                incendio_existente = IncendioForestal.objects.filter(
                    latitud__range=(row['latitude'] - 0.01, row['latitude'] + 0.01),
                    longitud__range=(row['longitude'] - 0.01, row['longitude'] + 0.01),
                    fecha_deteccion__date=fecha_deteccion.date()
                ).first()
                
                if incendio_existente:
                    # Actualizar existente
                    incendio_existente.intensidad = intensidad
                    incendio_existente.severidad = severidad
                    incendio_existente.area_afectada_ha = area_estimada
                    incendio_existente.save()
                    actualizados += 1
                else:
                    # Crear nuevo
                    IncendioForestal.objects.create(
                        nombre=nombre,
                        latitud=row['latitude'],
                        longitud=row['longitude'],
                        departamento=departamento,
                        intensidad=intensidad,
                        severidad=severidad,
                        area_afectada_ha=area_estimada,
                        satelite=row.get('satellite', 'MODIS'),
                        fuente_datos='NASA FIRMS',
                        fecha_deteccion=fecha_deteccion,
                        confianza_deteccion=row.get('confidence', 50) / 100 if 'confidence' in row else 0.7,
                        estado='activo',
                        brillo_temperatura=row.get('bright_t31'),
                        pixel_size=1.0
                    )
                    nuevos += 1
                    
            except Exception as e:
                logger.error(f"Error procesando fila: {e}")
                continue
        
        logger.info(f"Procesados: {nuevos} nuevos, {actualizados} actualizados")
        return nuevos, actualizados
    
    def ejecutar_actualizacion(self, days=7):
        """Ejecuta la actualización completa"""
        
        # INICIALIZAR VARIABLES primero
        nuevos = 0
        actualizados = 0
        total = 0
        activos = 0
        
        logger.info("=" * 50)
        logger.info("INICIANDO ACTUALIZACIÓN NASA FIRMS")
        logger.info("=" * 50)
        
        # Obtener datos
        df = self.obtener_datos_nasa(days=days)
        
        if not df.empty:
            nuevos, actualizados = self.procesar_incendios(df)
            
            # Estadísticas
            from monitoreo.models import IncendioForestal
            total = IncendioForestal.objects.count()
            activos = IncendioForestal.objects.filter(estado='activo').count()
            
            logger.info(f"🎯 Resultados:")
            logger.info(f"   Nuevos incendios: {nuevos}")
            logger.info(f"   Actualizados: {actualizados}")
            logger.info(f"   Total en BD: {total}")
            logger.info(f"   Incendios activos: {activos}")
        else:
            logger.warning("No se obtuvieron datos de NASA FIRMS")
        
        logger.info("=" * 50)
        logger.info("ACTUALIZACIÓN COMPLETADA")
        logger.info("=" * 50)
        
        return {
            'nuevos': nuevos,
            'actualizados': actualizados,
            'total': total,
            'activos': activos
        }
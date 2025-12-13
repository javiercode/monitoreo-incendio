# test_nasa_detailed.py
import requests
import pandas as pd
from io import StringIO
import sys
import os

# Agregar ruta para importar settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incendios_bolivia.settings')

from decouple import config

def test_nasa_api():
    """Prueba detallada de la API de NASA FIRMS"""
    
    api_key = config('NASA_FIRMS_API_KEY', default=None)
    
    if not api_key:
        print("❌ API Key no configurada en .env")
        return
    
    print("=" * 60)
    print("PRUEBA DETALLADA NASA FIRMS API")
    print("=" * 60)
    
    # URL de prueba
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/MODIS_NRT/-69.6,-22.9,-57.5,-9.7/1"
    
    print(f"\n📡 URL de prueba:")
    print(f"   {url}")
    
    try:
        # 1. Hacer la petición
        response = requests.get(url, timeout=30)
        
        print(f"\n📊 Respuesta HTTP: {response.status_code}")
        print(f"   Tamaño respuesta: {len(response.text)} caracteres")
        
        # 2. Mostrar primeras líneas
        print(f"\n📝 Primeras 10 líneas del CSV:")
        lines = response.text.strip().split('\n')
        for i, line in enumerate(lines[:10]):
            print(f"   Línea {i}: {line}")
        
        # 3. Intentar parsear con pandas
        print(f"\n🔍 Intentando parsear con pandas...")
        
        if response.text.strip():
            try:
                df = pd.read_csv(StringIO(response.text))
                print(f"   ✅ Parseado exitoso")
                print(f"   📊 Filas: {len(df)}")
                print(f"   📋 Columnas: {', '.join(df.columns)}")
                
                if not df.empty:
                    print(f"\n📈 Primeros registros:")
                    print(df.head(3).to_string())
                    
                    # Estadísticas básicas
                    print(f"\n📊 Estadísticas:")
                    print(f"   Latitud min/max: {df['latitude'].min():.2f} / {df['latitude'].max():.2f}")
                    print(f"   Longitud min/max: {df['longitude'].min():.2f} / {df['longitude'].max():.2f}")
                    print(f"   Fechas: {df['acq_date'].min()} a {df['acq_date'].max()}")
                    
                    # Contar por departamento aproximado
                    print(f"\n🗺️  Distribución aproximada:")
                    # Bolivia: Norte (> -15), Centro (-15 a -18), Sur (< -18)
                    norte = df[df['latitude'] > -15]
                    centro = df[(df['latitude'] <= -15) & (df['latitude'] > -18)]
                    sur = df[df['latitude'] <= -18]
                    
                    print(f"   Norte (Beni/Pando): {len(norte)}")
                    print(f"   Centro (La Paz/Cochabamba): {len(centro)}")
                    print(f"   Sur (Santa Cruz/Potosi/Tarija): {len(sur)}")
                
            except pd.errors.ParserError as e:
                print(f"   ❌ Error parseando CSV: {e}")
                
                # Analizar líneas problemáticas
                print(f"\n🔍 Analizando líneas problemáticas...")
                for i, line in enumerate(lines):
                    parts = line.split(',')
                    if len(parts) != 14:  # NASA FIRMS tiene 14 columnas típicas
                        print(f"   Línea {i}: {len(parts)} columnas -> {line[:50]}...")
                        
        else:
            print("   ⚠️ Respuesta vacía (posiblemente no hay incendios)")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    test_nasa_api()
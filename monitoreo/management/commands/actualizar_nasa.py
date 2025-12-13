# monitoreo/management/commands/actualizar_nasa.py - VERSIÓN CORREGIDA
from django.core.management.base import BaseCommand
from monitoreo.utils.nasa_firms import NASAFirmsUpdater
from decouple import config

class Command(BaseCommand):
    help = 'Actualiza datos de incendios desde NASA FIRMS'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Número de días de datos a obtener (default: 7)'
        )
        parser.add_argument(
            '--source',
            type=str,
            default='MODIS_NRT',
            help='Fuente de datos (MODIS_NRT, VIIRS_NRT, etc.)'
        )
    
    def handle(self, *args, **options):
        # Verificar API Key
        api_key = config('NASA_FIRMS_API_KEY', default=None)
        if not api_key:
            self.stdout.write(
                self.style.ERROR('❌ API Key no configurada. Agrega NASA_FIRMS_API_KEY a .env')
            )
            self.stdout.write(self.style.WARNING('💡 Ejemplo en .env: NASA_FIRMS_API_KEY=tu_key_aqui'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'🚀 Iniciando actualización NASA FIRMS (últimos {options["days"]} días)...'))
        
        updater = NASAFirmsUpdater(api_key=api_key)
        
        try:
            resultados = updater.ejecutar_actualizacion(
                days=options['days']
            )
            
            # Mostrar resultados
            self.stdout.write(self.style.SUCCESS('✅ Actualización completada'))
            self.stdout.write("📊 Resultados:")
            self.stdout.write(f"   🔥 Nuevos incendios: {resultados['nuevos']}")
            self.stdout.write(f"   🔄 Actualizados: {resultados['actualizados']}")
            self.stdout.write(f"   📈 Total en BD: {resultados['total']}")
            self.stdout.write(f"   ⚡ Activos: {resultados['activos']}")
            
            if resultados['nuevos'] == 0 and resultados['actualizados'] == 0:
                self.stdout.write(self.style.WARNING('⚠️  No se encontraron incendios nuevos en el área de Bolivia'))
                self.stdout.write(self.style.WARNING('   Esto puede ser normal si no hay incendios activos en los últimos días'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error durante la actualización: {e}'))
            self.stdout.write(self.style.WARNING('💡 Verifica:'))
            self.stdout.write(self.style.WARNING('   1. Tu API Key es válida'))
            self.stdout.write(self.style.WARNING('   2. Tienes conexión a internet'))
            self.stdout.write(self.style.WARNING('   3. La API de NASA FIRMS está funcionando'))
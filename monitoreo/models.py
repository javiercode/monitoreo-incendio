# monitoreo/models.py
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils import timezone

class Incendio(models.Model):
    nombre = models.CharField(max_length=200)
    fecha_deteccion = models.DateTimeField(default=timezone.now)
    latitud = models.FloatField()
    longitud = models.FloatField()
    departamento = models.CharField(max_length=100)
    intensidad = models.FloatField(default=0.5)
    area_afectada = models.FloatField(default=0)  # en hectáreas
    estado = models.CharField(max_length=20, default='activo', 
                              choices=[('activo', 'Activo'), 
                                       ('controlado', 'Controlado'),
                                       ('extinto', 'Extinto')])
    
    def __str__(self):
        return f"{self.nombre} - {self.departamento}"
    
    class Meta:
        verbose_name = "Incendio Forestal"
        verbose_name_plural = "Incendios Forestales"

class Departamento(models.Model):
    """Departamentos de Bolivia"""
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    capital = models.CharField(max_length=100, blank=True)
    area_km2 = models.FloatField(default=0)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"

class IncendioForestal(gis_models.Model):
    """Modelo completo para incendios forestales"""
    ESTADO_CHOICES = [
        ('activo', '🔥 Activo'),
        ('controlado', '⚠️ Controlado'),
        ('extinto', '✅ Extinto'),
    ]
    
    SEVERIDAD_CHOICES = [
        ('bajo', '🟢 Bajo'),
        ('medio', '🟡 Medio'),
        ('alto', '🟠 Alto'),
        ('critico', '🔴 Crítico'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name="Nombre del incendio")
    fecha_deteccion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de detección")
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    # Ubicación geoespacial (IMPORTANTE: con GIS)
    latitud = models.FloatField(verbose_name="Latitud")
    longitud = models.FloatField(verbose_name="Longitud")
    
    # Relaciones
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Métricas
    intensidad = models.FloatField(default=0.5, help_text="Intensidad del incendio (0-1)")
    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES, default='medio')
    area_afectada_ha = models.FloatField(default=0, verbose_name="Área afectada (hectáreas)")
    confianza_deteccion = models.FloatField(default=0.8, help_text="Confianza en la detección (0-1)")
    
    # Datos satelitales
    satelite = models.CharField(max_length=50, default="MODIS", verbose_name="Satélite fuente")
    brillo_temperatura = models.FloatField(null=True, blank=True, verbose_name="Temperatura de brillo (°C)")
    pixel_size = models.FloatField(default=1.0, verbose_name="Tamaño de pixel (km)")
    
    # Metadatos
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fuente_datos = models.CharField(max_length=100, default="NASA FIRMS", verbose_name="Fuente de datos")
    notas = models.TextField(blank=True, verbose_name="Observaciones")
    
    # Imágenes/archivos
    imagen_satelital = models.URLField(blank=True, verbose_name="URL imagen satelital")
    reporte_pdf = models.FileField(upload_to='reportes/', null=True, blank=True)
    
    class Meta:
        verbose_name = "Incendio Forestal"
        verbose_name_plural = "Incendios Forestales"
        ordering = ['-fecha_deteccion']
    
    def __str__(self):
        return f"{self.nombre} - {self.departamento.nombre if self.departamento else 'Sin departamento'}"
    
    def save(self, *args, **kwargs):
        if not self.nombre:
            fecha_str = self.fecha_deteccion.strftime('%Y%m%d_%H%M')
            depto = self.departamento.nombre if self.departamento else 'Desconocido'
            self.nombre = f"Incendio_{depto}_{fecha_str}"
        super().save(*args, **kwargs)
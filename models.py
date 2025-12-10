# models.py
from django.db import models
from django.contrib.gis.db import models as gis_models

class IncendioForestal(gis_models.Model):
    nombre = models.CharField(max_length=200)
    fecha_deteccion = models.DateTimeField()
    coordenadas = gis_models.PointField(srid=4326)
    intensidad = models.FloatField(help_text="Índice de intensidad del incendio (0-1)")
    area_afectada = models.FloatField(help_text="Área en hectáreas")
    departamento = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    
    # Datos satelitales
    imagen_satelital = models.URLField(blank=True)
    fuente_datos = models.CharField(max_length=100, default="MODIS")
    
    class Meta:
        verbose_name = "Incendio Forestal"
        verbose_name_plural = "Incendios Forestales"
    
    def __str__(self):
        return f"{self.nombre} - {self.departamento}"

class AreaProtegida(gis_models.Model):
    nombre = models.CharField(max_length=200)
    poligono = gis_models.PolygonField(srid=4326)
    categoria = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre
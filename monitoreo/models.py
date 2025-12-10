# monitoreo/models.py
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
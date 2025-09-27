from django.db import models
from django.conf import settings
from django.utils import timezone

class UserStation(models.Model):
    station_id = models.CharField(primary_key=True, max_length=100)
    location = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    # Solo campos que existen en tu BD: station_id, location, user_id
    # Quitamos description y created_at que no existen
    
    class Meta:
        db_table = 'user_stations'
        verbose_name = 'Estación de usuario'
        verbose_name_plural = 'Estaciones de usuarios'

    def __str__(self):
        return f"{self.station_id} - {self.location}"

class StationData(models.Model):
    id = models.AutoField(primary_key=True)
    
    # TUS PARÁMETROS ORIGINALES - SE MANTIENEN
    temperatura = models.FloatField(null=True, blank=True)
    humedad = models.FloatField(null=True, blank=True)
    presion = models.FloatField(null=True, blank=True)
    gas_detectado = models.BooleanField(null=True, blank=True)
    voltaje_mq135 = models.FloatField(null=True, blank=True)
    indice_uv = models.FloatField(null=True, blank=True)
    nivel_uv = models.CharField(max_length=50, null=True, blank=True)
    
    station = models.ForeignKey(
        UserStation, 
        on_delete=models.CASCADE,
        db_column='station_id'
    )
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'station_data'
        verbose_name = 'Dato de estación'
        verbose_name_plural = 'Datos de estaciones'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Datos de {self.station.station_id} - {self.timestamp}"
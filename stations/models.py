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
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'user_stations'
        verbose_name = 'Estación de usuario'
        verbose_name_plural = 'Estaciones de usuarios'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.station_id} - {self.location}"

    def save(self, *args, **kwargs):
        # Actualizar el estado del usuario
        if not self.user.has_station:
            self.user.has_station = True
            self.user.save()
        super().save(*args, **kwargs)

class StationData(models.Model):
    id = models.AutoField(primary_key=True)
    
    # Datos del sensor AHT20
    temperature_aht20 = models.FloatField(null=True, blank=True)
    humidity_aht20 = models.FloatField(null=True, blank=True)
    
    # Datos del sensor BMP280
    temperature_bmp280 = models.FloatField(null=True, blank=True)
    pressure_bmp280 = models.FloatField(null=True, blank=True)
    
    # Datos del sensor MQ-2
    voltage_mq2 = models.FloatField(null=True, blank=True)
    digital_mq2 = models.BooleanField(null=True, blank=True)
    
    # Datos del sensor MQ-135
    voltage_mq135 = models.FloatField(null=True, blank=True)
    digital_mq135 = models.BooleanField(null=True, blank=True)
    
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
    
    @property
    def temperature(self):
        """Retorna la temperatura preferida (AHT20 tiene prioridad)"""
        return self.temperature_aht20 or self.temperature_bmp280
    
    @property
    def has_air_quality_data(self):
        """Verifica si tiene datos de calidad del aire"""
        return any([
            self.voltage_mq2 is not None,
            self.digital_mq2 is not None,
            self.voltage_mq135 is not None,
            self.digital_mq135 is not None
        ])
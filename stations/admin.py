from django.contrib import admin
from .models import UserStation, StationData

@admin.register(UserStation)
class UserStationAdmin(admin.ModelAdmin):
    list_display = ('station_id', 'location', 'user')
    list_filter = ('user',)
    search_fields = ('station_id', 'location', 'user__username', 'user__email')

@admin.register(StationData)
class StationDataAdmin(admin.ModelAdmin):
    list_display = ('station', 'temperatura', 'humedad', 'presion', 'gas_detectado', 'timestamp')
    list_filter = ('station', 'timestamp', 'gas_detectado', 'nivel_uv')
    search_fields = ('station__station_id', 'station__location', 'nivel_uv')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    list_per_page = 20
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('station', 'timestamp')
        }),
        ('Datos Ambientales', {
            'fields': ('temperatura', 'humedad', 'presion')
        }),
        ('Calidad del Aire', {
            'fields': ('gas_detectado', 'voltaje_mq135')
        }),
        ('Radiación UV', {
            'fields': ('indice_uv', 'nivel_uv')
        }),
    )
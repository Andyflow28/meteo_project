from django.contrib import admin
from .models import UserStation, StationData

@admin.register(UserStation)
class UserStationAdmin(admin.ModelAdmin):
    list_display = ('station_id', 'location', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('station_id', 'location', 'user__username', 'user__email')
    date_hierarchy = 'created_at'

@admin.register(StationData)
class StationDataAdmin(admin.ModelAdmin):
    list_display = ('station', 'temperature', 'humidity_aht20', 'pressure_bmp280', 'timestamp')
    list_filter = ('station', 'timestamp')
    search_fields = ('station__station_id', 'station__location')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    
    def temperature(self, obj):
        return obj.temperature
    temperature.short_description = 'Temperatura (°C)'
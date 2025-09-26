from django.urls import path
from . import views

app_name = 'stations'

urlpatterns = [
    # Cambia la raíz a la vista pública
    path('', views.public_showroom, name='public_showroom'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-station/', views.add_station, name='add_station'),
    path('station/<str:station_id>/', views.station_detail, name='station_detail'),
    path('station/<str:station_id>/add-data/', views.add_station_data, name='add_station_data'),
    path('station/<str:station_id>/delete/', views.delete_station, name='delete_station'),
    path('showroom/', views.showroom_dashboard, name='showroom_dashboard'),
    path('api/realtime-data/', views.realtime_data_api, name='realtime_data_api'),
    path('public-showroom/', views.public_showroom, name='public_showroom'),
    path('api/public/latest-data/', views.public_latest_data_api, name='public_latest_data_api'),
]
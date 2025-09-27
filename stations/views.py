from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import UserStation, StationData
from .forms import UserStationForm, StationDataForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.db import connection
from django.http import JsonResponse
import json


@never_cache
def public_showroom(request):
    """Vista pública para showroom - usando consultas SQL directas que coincidan con la BD"""
    try:
        # Consulta directa que funciona con la estructura actual de la BD
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM station_data 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            columns = [col[0] for col in cursor.description]
            latest_data_row = cursor.fetchone()
        
        latest_data = None
        if latest_data_row:
            latest_data = dict(zip(columns, latest_data_row))
        
        # Obtener información de la estación (solo campos existentes)
        station_info = None
        if latest_data and 'station_id' in latest_data:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT station_id, location, description 
                    FROM user_stations 
                    WHERE station_id = %s
                """, [latest_data['station_id']])
                station_row = cursor.fetchone()
                if station_row:
                    station_info = {
                        'station_id': station_row[0],
                        'location': station_row[1],
                        'description': station_row[2] if len(station_row) > 2 else ''
                    }
        
        # Convertir a objeto StationData para la plantilla
        station_data_obj = None
        if latest_data:
            station_data_obj = StationData(
                id=latest_data.get('id'),
                temperatura=latest_data.get('temperatura'),
                humedad=latest_data.get('humedad'),
                presion=latest_data.get('presion'),
                gas_detectado=latest_data.get('gas_detectado'),
                voltaje_mq135=latest_data.get('voltaje_mq135'),
                indice_uv=latest_data.get('indice_uv'),
                nivel_uv=latest_data.get('nivel_uv'),
                timestamp=latest_data.get('timestamp')
            )
            # Asignar la estación si existe
            if station_info:
                station_data_obj.station = UserStation(
                    station_id=station_info['station_id'],
                    location=station_info['location'],
                    description=station_info.get('description', '')
                )
        
        context = {
            'latest_data': station_data_obj,
            'station': station_data_obj.station if station_data_obj and hasattr(station_data_obj, 'station') else None,
            'has_data': latest_data is not None,
            'timestamp': timezone.now(),
        }
        
        return render(request, 'stations/public_showroom.html', context)
        
    except Exception as e:
        print(f"Error en public_showroom: {e}")
        context = {
            'latest_data': None,
            'station': None,
            'has_data': False,
            'timestamp': timezone.now(),
        }
        return render(request, 'stations/public_showroom.html', context)


@never_cache
def public_latest_data_api(request):
    """API pública usando consultas SQL directas que coincidan con la BD real"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM station_data 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            columns = [col[0] for col in cursor.description]
            latest_data_row = cursor.fetchone()
        
        if latest_data_row:
            latest_data = dict(zip(columns, latest_data_row))
            
            # Obtener información de la estación (solo campos existentes)
            station_info = {}
            if 'station_id' in latest_data:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT station_id, location, description 
                        FROM user_stations 
                        WHERE station_id = %s
                    """, [latest_data['station_id']])
                    station_row = cursor.fetchone()
                    if station_row:
                        station_info = {
                            'station_id': station_row[0],
                            'location': station_row[1],
                            'description': station_row[2] if len(station_row) > 2 else ''
                        }
            
            data = {
                'station_data': latest_data,
                'station_info': station_info,
                'timestamp': timezone.now().isoformat(),
                'status': 'success'
            }
        else:
            data = {
                'station_data': {},
                'station_info': {},
                'timestamp': timezone.now().isoformat(),
                'message': 'No hay datos disponibles',
                'status': 'no_data'
            }
            
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
            'status': 'error'
        }, status=500)


@login_required
def dashboard(request):
    try:
        user_stations = UserStation.objects.filter(user=request.user)
        
        # Obtener datos recientes para cada estación
        station_data = {}
        for station in user_stations:
            recent_data = StationData.objects.filter(station=station).order_by('-timestamp')[:5]
            station_data[station.station_id] = recent_data
        
        context = {
            'user_stations': user_stations,
            'station_data': station_data,
        }
        return render(request, 'stations/dashboard.html', context)
    except Exception as e:
        print(f"Error en dashboard: {e}")
        context = {
            'user_stations': [],
            'station_data': {},
        }
        return render(request, 'stations/dashboard.html', context)


@login_required
def add_station(request):
    if request.method == 'POST':
        form = UserStationForm(request.POST)
        if form.is_valid():
            station = form.save(commit=False)
            station.user = request.user
            station.save()
            messages.success(request, f'Estación {station.station_id} agregada exitosamente.')
            return redirect('stations:dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserStationForm()
    
    return render(request, 'stations/add_station.html', {'form': form})


@login_required
def station_detail(request, station_id):
    station = get_object_or_404(UserStation, station_id=station_id, user=request.user)
    
    # Filtrar datos por fecha
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    data = StationData.objects.filter(
        station=station,
        timestamp__gte=start_date
    ).order_by('timestamp')
    
    context = {
        'station': station,
        'data': data,
        'selected_days': days,
    }
    return render(request, 'stations/station_detail.html', context)


@login_required
def add_station_data(request, station_id):
    station = get_object_or_404(UserStation, station_id=station_id, user=request.user)
    
    if request.method == 'POST':
        form = StationDataForm(request.POST)
        if form.is_valid():
            station_data = form.save(commit=False)
            station_data.station = station
            station_data.save()
            messages.success(request, 'Datos agregados exitosamente.')
            return redirect('stations:station_detail', station_id=station.station_id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = StationDataForm()
    
    context = {
        'station': station,
        'form': form,
    }
    return render(request, 'stations/add_station_data.html', context)


@login_required
def delete_station(request, station_id):
    station = get_object_or_404(UserStation, station_id=station_id, user=request.user)
    
    if request.method == 'POST':
        station_id = station.station_id
        station.delete()
        messages.success(request, f'Estación {station_id} eliminada exitosamente.')
        return redirect('stations:dashboard')
    
    context = {
        'station': station,
    }
    return render(request, 'stations/delete_station.html', context)


def showroom_dashboard(request):
    """Vista para el showroom comercial"""
    return render(request, 'stations/showroom_dashboard.html')


def realtime_data_api(request):
    """API para datos en tiempo real del showroom"""
    try:
        # Obtener todas las estaciones con sus últimos datos usando consultas directas
        with connection.cursor() as cursor:
            cursor.execute("SELECT station_id, location, description FROM user_stations")
            stations_data = cursor.fetchall()
        
        data = {
            'timestamp': timezone.now().isoformat(),
            'active_stations': len(stations_data),
            'stations': [],
            'events': [],
            'avg_temperature': None,
            'avg_humidity': None,
            'avg_pressure': None,
        }
        
        temperatures = []
        humidities = []
        pressures = []
        
        for station_row in stations_data:
            station_id, location, description = station_row
            
            # Obtener último dato de la estación
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT temperatura, humedad, presion, timestamp 
                    FROM station_data 
                    WHERE station_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, [station_id])
                latest_row = cursor.fetchone()
            
            if latest_row:
                temperatura, humedad, presion, timestamp = latest_row
                
                station_data = {
                    'station_id': station_id,
                    'location': location,
                    'temperature': temperatura,
                    'humidity': humedad,
                    'pressure': presion,
                    'last_update': timestamp.isoformat() if timestamp else None,
                    'status': 'online',
                    'quality': 95,
                }
                
                if station_data['temperature'] is not None:
                    temperatures.append(station_data['temperature'])
                if station_data['humidity'] is not None:
                    humidities.append(station_data['humidity'])
                if station_data['pressure'] is not None:
                    pressures.append(station_data['pressure'])
                
                data['stations'].append(station_data)
        
        # Calcular promedios solo si hay datos
        if temperatures:
            data['avg_temperature'] = sum(temperatures) / len(temperatures)
        if humidities:
            data['avg_humidity'] = sum(humidities) / len(humidities)
        if pressures:
            data['avg_pressure'] = sum(pressures) / len(pressures)
            
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_receive_data(request):
    """API para recibir datos de las estaciones (POST)"""
    if request.method == 'POST':
        try:
            # Parsear JSON
            data = json.loads(request.body)
            
            # Validar campos requeridos
            required_fields = ['station_id', 'temperatura', 'humedad', 'presion']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Campo requerido faltante: {field}'
                    }, status=400)
            
            # Verificar si la estación existe usando consulta directa
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM user_stations WHERE station_id = %s", [data['station_id']])
                station_exists = cursor.fetchone()
            
            if not station_exists:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Estación no encontrada'
                }, status=404)
            
            # Insertar datos usando consulta directa
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO station_data 
                    (station_id, temperatura, humedad, presion, gas_detectado, voltaje_mq135, indice_uv, nivel_uv, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data['station_id'],
                    data['temperatura'],
                    data['humedad'],
                    data['presion'],
                    data.get('gas_detectado', False),
                    data.get('voltaje_mq135'),
                    data.get('indice_uv', 0.0),
                    data.get('nivel_uv', 'Muy bajo'),
                    timezone.now()
                ])
            
            return JsonResponse({
                'status': 'success',
                'message': 'Datos recibidos correctamente',
                'timestamp': timezone.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    }, status=405)
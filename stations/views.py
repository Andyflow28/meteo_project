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
    """Vista pública para showroom - muestra el registro más reciente de station_data"""
    try:
        # Obtener el registro más reciente de TODAS las estaciones con optimización
        latest_data = StationData.objects.select_related('station').order_by('-timestamp').first()
        
        context = {
            'latest_data': latest_data,
            'station': latest_data.station if latest_data else None,
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
    """API pública que devuelve el registro más reciente de cualquier estación"""
    try:
        # Obtener el registro más reciente de TODAS las estaciones con optimización
        latest_data = StationData.objects.select_related('station').order_by('-timestamp').first()
        
        if latest_data:
            station = latest_data.station
            data = {
                'station_data': {
                    'temperatura': latest_data.temperatura,
                    'humedad': latest_data.humedad,
                    'presion': latest_data.presion,
                    'gas_detectado': latest_data.gas_detectado,
                    'voltaje_mq135': latest_data.voltaje_mq135,
                    'indice_uv': latest_data.indice_uv,
                    'nivel_uv': latest_data.nivel_uv,
                    'timestamp': latest_data.timestamp.isoformat(),
                },
                'station_info': {
                    'station_id': station.station_id,
                    'location': station.location,
                    'description': station.description,
                } if station else {},
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
        
        # Obtener datos recientes para cada estación con optimización
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
        # Obtener todas las estaciones con sus últimos datos
        stations = UserStation.objects.all()
        
        data = {
            'timestamp': timezone.now().isoformat(),
            'active_stations': stations.count(),
            'stations': [],
            'events': [],
            'avg_temperature': None,
            'avg_humidity': None,
            'avg_pressure': None,
        }
        
        temperatures = []
        humidities = []
        pressures = []
        
        for station in stations:
            # Obtener último dato de la estación con optimización
            latest_data = StationData.objects.filter(station=station).order_by('-timestamp').first()
            
            if latest_data:
                station_data = {
                    'station_id': station.station_id,
                    'location': station.location,
                    'temperature': latest_data.temperatura,
                    'humidity': latest_data.humedad,
                    'pressure': latest_data.presion,
                    'gas_detectado': latest_data.gas_detectado,
                    'voltaje_mq135': latest_data.voltaje_mq135,
                    'indice_uv': latest_data.indice_uv,
                    'nivel_uv': latest_data.nivel_uv,
                    'last_update': latest_data.timestamp.isoformat(),
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
            
            # Buscar la estación
            try:
                station = UserStation.objects.get(station_id=data['station_id'])
            except UserStation.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Estación no encontrada'
                }, status=404)
            
            # Crear nuevo registro
            station_data = StationData(
                station=station,
                temperatura=data['temperatura'],
                humedad=data['humedad'],
                presion=data['presion'],
                gas_detectado=data.get('gas_detectado', False),
                voltaje_mq135=data.get('voltaje_mq135'),
                indice_uv=data.get('indice_uv', 0.0),
                nivel_uv=data.get('nivel_uv', 'Muy bajo')
            )
            station_data.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Datos recibidos correctamente',
                'id': station_data.id,
                'timestamp': station_data.timestamp.isoformat()
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
import json
import logging
from celery import shared_task
from django.conf import settings
from django.db.models import Max, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Device, DeviceData, AggregatedData
import redis
import uuid
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger(__name__)

# MVP Geofence: Center of Los Angeles
GEOFENCE_LAT = 34.0522
GEOFENCE_LNG = -118.2437
GEOFENCE_RADIUS_KM = 5.0

try:
    redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
except Exception:
    redis_client = None

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371 # km

@shared_task
def process_ingestion_queue():
    if not redis_client:
        return
        
    batch_size = 500
    batch = []
    
    for _ in range(batch_size):
        item = redis_client.rpop('raw_device_data')
        if not item:
            break
        batch.append(json.loads(item))
        
    if not batch:
        return
        
    device_data_instances = []
    valid_device_ids = set(Device.objects.values_list('id', flat=True))
    
    for data in batch:
        device_id_str = data['device_id']
        try:
            device_id = uuid.UUID(device_id_str)
        except ValueError:
            continue

        if device_id not in valid_device_ids:
            continue

        timestamp = data['timestamp']
        curr_lat = float(data['latitude'])
        curr_lng = float(data['longitude'])
        curr_fuel = float(data.get('fuel_level', 0))
        curr_speed = float(data.get('speed', 0))
        
        prev_state = redis_client.hgetall(f"device_state:{device_id}")
        if prev_state:
            prev_fuel = float(prev_state.get(b'fuel', curr_fuel))
            if prev_fuel - curr_fuel > 10.0:
                alert_msg = f"FUEL THEFT DETECTED: Device {device_id} dropped from {prev_fuel}% to {curr_fuel}%"
                redis_client.lpush('alerts', json.dumps({
                    "device_id": device_id_str,
                    "type": "FUEL_THEFT",
                    "message": alert_msg,
                    "timestamp": timestamp
                }))

        if curr_speed > 100.0:
            alert_msg = f"OVERSPEED: Device {device_id} is at {curr_speed} km/h"
            redis_client.lpush('alerts', json.dumps({
                "device_id": device_id_str,
                "type": "OVERSPEED",
                "message": alert_msg,
                "timestamp": timestamp
            }))

        dist_from_center = haversine(curr_lng, curr_lat, GEOFENCE_LNG, GEOFENCE_LAT)
        is_inside = dist_from_center <= GEOFENCE_RADIUS_KM
        
        if prev_state:
            prev_inside_bytes = prev_state.get(b'is_inside')
            if prev_inside_bytes is None:
                prev_inside = is_inside
            else:
                prev_inside = prev_inside_bytes.decode('utf-8') == 'true'

            if is_inside != prev_inside:
                status = "ENTERED" if is_inside else "EXITED"
                alert_msg = f"GEOFENCE {status}: Device {device_id} {status} the 5km zone around LA center."
                redis_client.lpush('alerts', json.dumps({
                    "device_id": device_id_str,
                    "type": f"GEOFENCE_{status}",
                    "message": alert_msg,
                    "timestamp": timestamp
                }))

        redis_client.hset(f"device_state:{device_id}", mapping={
            "lat": curr_lat, "lng": curr_lng, "speed": curr_speed, "fuel": curr_fuel, "timestamp": timestamp, "is_inside": 'true' if is_inside else 'false'
        })
        
        device_data_instances.append(
            DeviceData(
                device_id=device_id,
                timestamp=timestamp,
                latitude=curr_lat,
                longitude=curr_lng,
                speed=curr_speed,
                fuel_level=curr_fuel,
                metadata=data.get('metadata', {})
            )
        )
        
    DeviceData.objects.bulk_create(device_data_instances)

@shared_task
def aggregate_stats_task(period_type='hourly'):
    now = timezone.now()
    if period_type == 'hourly':
        start_time = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
    else: # daily
        start_time = now.date() - timedelta(days=1)
        end_time = now.date()
        
    devices = Device.objects.all()
    for device in devices:
        data_points = DeviceData.objects.filter(
            device=device,
            timestamp__gte=start_time,
            timestamp__lt=end_time
        ).order_by('timestamp')
        
        if not data_points.exists():
            continue
            
        total_distance = 0
        prev_point = None
        for point in data_points:
            if prev_point:
                total_distance += haversine(prev_point.longitude, prev_point.latitude, point.longitude, point.latitude)
            prev_point = point
            
        max_speed = data_points.aggregate(Max('speed'))['speed__max']
        fuel_consumed = data_points.first().fuel_level - data_points.last().fuel_level
        
        AggregatedData.objects.update_or_create(
            device=device,
            period_start=start_time,
            period_type=period_type,
            defaults={
                'distance_traveled': total_distance,
                'fuel_consumed': max(0, fuel_consumed),
                'max_speed': max_speed,
            }
        )

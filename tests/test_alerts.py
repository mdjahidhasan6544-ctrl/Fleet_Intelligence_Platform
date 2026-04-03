import pytest
import json
import uuid
from rest_framework.test import APIClient
from tracking.models import Device
from tracking.tasks import process_ingestion_queue
import redis
from django.conf import settings
from django.core.cache import cache

@pytest.fixture(autouse=True)
def clean_all():
    # Clear Redis
    r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
    r.delete('raw_device_data')
    r.delete('alerts')
    keys = r.keys('device_state:*')
    if keys: r.delete(*keys)
    # Clear Django Cache
    cache.clear()
    yield
    cache.clear()

@pytest.fixture
def redis_conn():
    return redis.Redis.from_url(settings.CELERY_BROKER_URL)

@pytest.mark.django_db(transaction=True)
def test_fuel_theft_alert(redis_conn):
    device = Device.objects.create(api_key="theft-test-key", name="Theft Test Device")
    device_id_obj = device.id
    device_id_str = str(device_id_obj)
    
    # Set initial state (90% fuel, and ensure geofence state matches position)
    # 34.0, -118.0 is outside the LA 5km geofence
    redis_conn.hset(f"device_state:{device_id_str}", mapping={
        "lat": 34.0, "lng": -118.0, "speed": 50.0, "fuel": 90.0, "timestamp": "2023-10-27T10:00:00Z",
        "is_inside": "false"
    })
    
    client = APIClient()
    payload = {
        "timestamp": "2023-10-27T10:01:00Z",
        "latitude": 34.001,
        "longitude": -118.001,
        "speed": 55.0,
        "fuel_level": 70.0
    }
    response = client.post('/api/v1/ingest/', payload, format='json', HTTP_X_API_KEY="theft-test-key")
    assert response.status_code == 202
    
    process_ingestion_queue()
    
    alerts = [json.loads(a) for a in redis_conn.lrange('alerts', 0, -1)]
    assert len(alerts) > 0
    # Find the fuel theft alert
    theft_alert = next((a for a in alerts if a['type'] == 'FUEL_THEFT'), None)
    assert theft_alert is not None
    assert device_id_str in theft_alert['message']

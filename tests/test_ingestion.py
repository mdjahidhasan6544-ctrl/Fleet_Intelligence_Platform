import pytest
from rest_framework.test import APIClient
from tracking.models import Device

@pytest.mark.django_db
def test_ingestion_valid_payload():
    # Setup
    Device.objects.create(api_key="test-key-123", name="Test Device")
    client = APIClient()
    headers = {'HTTP_X_API_KEY': 'test-key-123'}
    payload = {
        "timestamp": "2023-10-27T10:00:00Z",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "speed": 65.5,
        "fuel_level": 80.0
    }
    
    # Execution
    response = client.post('/api/v1/ingest/', payload, format='json', **headers)
    
    # Assertion
    assert response.status_code == 202
    assert response.data['status'] == 'queued'

@pytest.mark.django_db
def test_ingestion_unauthorized():
    client = APIClient()
    headers = {'HTTP_X_API_KEY': 'wrong-key'}
    payload = {
        "timestamp": "2023-10-27T10:00:00Z",
        "latitude": 34.0522,
        "longitude": -118.2437
    }
    response = client.post('/api/v1/ingest/', payload, format='json', **headers)
    assert response.status_code == 401

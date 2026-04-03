import json
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .serializers import IngestionSerializer
import redis

try:
    redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
except Exception:
    redis_client = None

class IngestDataView(APIView):
    def post(self, request, *args, **kwargs):
        # Authentication is handled by DeviceAuthMiddleware
        # and request.device_id is already populated.
        
        serializer = IngestionSerializer(data=request.data)
        if serializer.is_valid():
            payload = serializer.validated_data
            payload['device_id'] = request.device_id
            payload['timestamp'] = payload['timestamp'].isoformat()
            
            if redis_client:
                redis_client.lpush('raw_device_data', json.dumps(payload))
            
            return Response({"status": "queued"}, status=202)
        return Response(serializer.errors, status=400)

class LiveStateView(APIView):
    def get(self, request, *args, **kwargs):
        if not redis_client:
            return Response([])
        keys = redis_client.keys('device_state:*')
        data = []
        for key in keys:
            state = redis_client.hgetall(key)
            decoded_state = {k.decode('utf-8'): v.decode('utf-8') for k, v in state.items()}
            decoded_state['device_id'] = key.decode('utf-8').split(':')[1]
            data.append(decoded_state)
        return Response(data)

class AlertListView(APIView):
    def get(self, request, *args, **kwargs):
        if not redis_client:
            return Response([])
        # Return last 50 alerts
        alerts = redis_client.lrange('alerts', 0, 49)
        return Response([json.loads(a) for a in alerts])

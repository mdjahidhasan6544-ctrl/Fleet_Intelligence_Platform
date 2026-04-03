from django.core.cache import cache
from django.http import JsonResponse
from .models import Device

class DeviceAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/v1/ingest/'):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return JsonResponse({"error": "Missing X-API-Key header"}, status=401)
            
            device_id = cache.get(f'auth:{api_key}')
            if not device_id:
                try:
                    device = Device.objects.get(api_key=api_key)
                    device_id = str(device.id)
                    cache.set(f'auth:{api_key}', device_id, timeout=3600)
                except Device.DoesNotExist:
                    return JsonResponse({"error": "Unauthorized"}, status=401)
            
            # Attach device_id to request for use in views
            request.device_id = device_id

        return self.get_response(request)

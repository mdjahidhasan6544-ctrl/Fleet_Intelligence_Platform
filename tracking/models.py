import uuid
from django.db import models

class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DeviceData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fuel_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['device', '-timestamp']),
        ]

class AggregatedData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    period_start = models.DateTimeField()
    period_type = models.CharField(max_length=10) # 'hourly', 'daily'
    distance_traveled = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fuel_consumed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    alerts_triggered = models.IntegerField(default=0)

    class Meta:
        unique_together = ('device', 'period_start', 'period_type')

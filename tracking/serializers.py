from rest_framework import serializers

class IngestionSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    speed = serializers.FloatField(min_value=0, required=False)
    fuel_level = serializers.FloatField(min_value=0, max_value=100, required=False)
    metadata = serializers.JSONField(required=False, default=dict)

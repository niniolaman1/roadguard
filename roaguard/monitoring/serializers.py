from rest_framework import serializers
from .models import Trip, DrowsinessEvent

class DrowsinessEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrowsinessEvent
        fields = ['id', 'timestamp', 'severity', 'duration']

class TripSerializer(serializers.ModelSerializer):
    events = DrowsinessEventSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ['id', 'start_time', 'end_time', 'duration', 'events']

    def get_duration(self, obj):
        if obj.end_time and obj.start_time:
            delta = obj.end_time - obj.start_time
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} mins"
        return "In progress"
from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('name','description')

class CreateRecurrentEventsSerializer(serializers.Serializer):    
        start = serializers.DateTimeField()
        end = serializers.DateTimeField()
        weekdays = serializers.DateTimeField()


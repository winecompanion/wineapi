from rest_framework import serializers
from .models import Event, Winery

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('name','description')

class CreateRecurrentEventsSerializer(serializers.Serializer):    
        start = serializers.DateTimeField()
        end = serializers.DateTimeField()
        weekdays = serializers.DateTimeField()


class WinerySerializer(serializers.ModelSerializer):
    """Serializes a winery for the api endpoint"""   
    class Meta:
        model = Winery
        fields = ('name', 'description', 'website', 'available_since') 

    def create(self, validated_data):
        winery = Winery.objects.create(**validated_data)
        return winery

from rest_framework import serializers
from .models import Event, Winery

class ScheduleSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    weekdays = serializers.IntegerField()

class RecurrentEventSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(many=True)
    class Meta:
        model = Event
        fields = ('name', 'description', 'schedule')

    def Calculate(self, validated_data):
        name = validated_data.pop('name')
        description = validated_data.pop('description')
        schedules_data = validated_data.pop('schedule')
        event = Event.objects.create(name=name,description=description)
        for schedule in schedules_data:
            #print >>sys.stderr, 'Goodbye, cruel world!'
            response = event.calculate_dates_in_threshold(schedule['start'],schedule['end'],schedule['weekdays'])            
            # Aca hay que poner un for de nuevo con la info parseada de lo que devuelve la sentencia anterior
            #EventOccurrence.objects.create(start,end,vacencies,event) 
            #Track.objects.create(album=album, **track_data)
        return response


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('name', 'description')


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

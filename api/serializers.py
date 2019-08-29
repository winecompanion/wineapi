from rest_framework import serializers
from .models import Event, Winery


class ScheduleSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    weekdays = serializers.IntegerField(allow_null=True)


class EventSerializer(serializers.ModelSerializer):
    vacancies = serializers.IntegerField()
    schedule = ScheduleSerializer(many=True)

    class Meta:
        model = Event
        fields = ('name', 'description', 'vacancies', 'schedule')
        extra_kwargs = {
            'vacancies': {'write_only': True}
        }


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

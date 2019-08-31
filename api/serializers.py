import datetime
from rest_framework import serializers
from .models import Event, EventOccurrence, Winery


class ScheduleSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField(allow_null=True)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    weekdays = serializers.ListField(
        allow_null=True,
        child=serializers.IntegerField())


class EventSerializer(serializers.HyperlinkedModelSerializer):
    vacancies = serializers.IntegerField(write_only=True)
    schedule = ScheduleSerializer(many=True, write_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'vacancies', 'schedule']

    def create(self, data):
        # TODO: finish docstring
        """Creates and saves an Event associated to
        instances of EventOcurrence.

        Params:
        """
        schedule = data.pop('schedule')
        vacancies = data.pop('vacancies')
        event = Event.objects.create(**data)

        for elem in schedule:
            start_time = elem['start_time']
            end_time = elem['end_time']
            dates = Event.calculate_dates_in_threshold(
                    elem['from_date'],
                    elem['to_date'],
                    elem['weekdays'])

            for date in dates:
                start = datetime.datetime(
                    date.year,
                    date.month,
                    date.day,
                    start_time.hour,
                    start_time.minute,
                )
                end = datetime.datetime(
                    date.year,
                    date.month,
                    date.day,
                    end_time.hour,
                    end_time.minute,
                )

                EventOccurrence.objects.create(
                    start=start,
                    end=end,
                    vacancies=vacancies,
                    event=event
                )

        return event


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

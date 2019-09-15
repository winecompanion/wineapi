import datetime
from rest_framework import serializers
from .models import (
    Event,
    EventOccurrence,
    Winery,
    WineLine,
    Wine,
    EventCategory,
)


class ScheduleSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField(allow_null=True)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    weekdays = serializers.ListField(
        allow_null=True,
        child=serializers.IntegerField())


class EventCategorySerializer(serializers.Serializer):
    """Serializer for event categories"""
    id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        # model = EventCategory
        fields = ('id', 'name')


class EventSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    vacancies = serializers.IntegerField(write_only=True)
    schedule = ScheduleSerializer(many=True, write_only=True, allow_empty=False)
    categories = EventCategorySerializer(many=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'cancelled',  'winery', 'categories', 'vacancies', 'schedule']

    def create(self, data):
        # TODO: finish docstring
        """Creates and saves an Event associated to
        instances of EventOcurrence.

        Params:
        """
        schedule = data.pop('schedule')
        vacancies = data.pop('vacancies')
        categories = data.pop('categories')
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
        for category in categories:
            event.categories.add(EventCategory.objects.get(pk=category['id']))
        return event


class WinerySerializer(serializers.ModelSerializer):
    """Serializes a winery for the api endpoint"""
    id = serializers.ReadOnlyField()

    class Meta:
        model = Winery
        fields = ('id', 'name', 'description', 'website', 'available_since', 'location')


class WineLineSerializer(serializers.ModelSerializer):
    """Serializes a wine line for the api endpoint"""
    id = serializers.ReadOnlyField()

    class Meta:
        model = WineLine
        fields = ('id', 'name', 'description', 'winery')


class WineSerializer(serializers.ModelSerializer):
    """Serializes wines for the api endpoint"""
    id = serializers.ReadOnlyField()

    class Meta:
        model = Wine
        fields = ('id', 'name', 'description', 'winery', 'varietal', 'wine_line')

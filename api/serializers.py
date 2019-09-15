import datetime
from rest_framework import serializers
from .models import (
    Event,
    EventOccurrence,
    Winery,
    WineLine,
    Wine,
    EventCategory,
    Tag,
)


class ScheduleSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField(allow_null=True)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    weekdays = serializers.ListField(
        allow_null=True,
        child=serializers.IntegerField())


class EventCategorySerializer(serializers.ModelSerializer):
    """Serializer for event categories"""
    id = serializers.ReadOnlyField()

    class Meta:
        model = EventCategory
        fields = ('id', 'name')


class TagSerializer(serializers.ModelSerializer):
    """Serializer for info Tags"""
    id = serializers.ReadOnlyField

    class Meta:
        model = Tag
        fields = ['id', 'name']


class EventSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    vacancies = serializers.IntegerField(write_only=True)
    schedule = ScheduleSerializer(many=True, write_only=True, allow_empty=False)
    categories = EventCategorySerializer(many=True)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'cancelled',  'winery', 'categories', 'tags', 'vacancies', 'schedule']

    def create(self, data):
        # TODO: finish docstring
        """Creates and saves an Event associated to
        instances of EventOcurrence.

        Params:
        """
        schedule = data.pop('schedule')
        vacancies = data.pop('vacancies')
        categories = data.pop('categories')
        tags = data.pop('tags') if 'tags' in data else []

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
            event.categories.add(EventCategory.objects.get(name=category['name']))

        for tag in tags:
            event.tags.add(Tag.objects.get(name=tag['name']))

        return event

    def validate_categories(self, categories):
        """
        Check that the categories are valid
        """
        for category in categories:
            try:
                EventCategory.objects.get(name=category['name'])
            except Exception:
                raise serializers.ValidationError("category {} does not exist".format(category['name']))

        return categories

    def validate_tags(self, tags):
        """
        Check that the tags are valid
        """
        for tag in tags:
            try:
                Tag.objects.get(name=tag['name'])
            except Exception:
                raise serializers.ValidationError("tag {} does not exist".format(tag['name']))

        return tags


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


class MapsSerializer(serializers.Serializer):
    location = serializers.CharField()

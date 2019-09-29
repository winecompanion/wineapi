from datetime import datetime
from winecompanion import settings

from django.db.models import Avg

from rest_framework import serializers
from .models import (
    Event,
    EventOccurrence,
    Winery,
    WineLine,
    Wine,
    EventCategory,
    Tag,
    Rate,
    Reservation,
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


class VenueSerializer(serializers.ModelSerializer):
    """Serializer for event occurrences """
    id = serializers.ReadOnlyField()

    class Meta:
        model = EventOccurrence
        fields = ('id', 'start', 'end', 'vacancies')


class EventSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    categories = EventCategorySerializer(many=True)
    occurrences = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)
    schedule = ScheduleSerializer(many=True, write_only=True, allow_empty=False)
    tags = TagSerializer(many=True, required=False)
    vacancies = serializers.IntegerField(write_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'description',
            'cancelled',
            'price',
            'rating',
            'tags',
            'categories',
            'winery',
            'occurrences',
            'schedule',
            'vacancies',
        ]

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
                start = datetime(
                    date.year,
                    date.month,
                    date.day,
                    start_time.hour,
                    start_time.minute,
                )
                end = datetime(
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

    def get_occurrences(self, event):
        occurrences = EventOccurrence.objects.filter(event=event, start__gt=datetime.now())
        serializer = VenueSerializer(instance=occurrences, many=True)
        return serializer.data

    def get_rating(self, event):
        rate = Rate.objects.filter(event=event).aggregate(Avg('rate'))
        return rate['rate__avg']

    def to_representation(self, obj):
        self.fields['winery'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        return super().to_representation(obj)


class WineSerializer(serializers.ModelSerializer):
    """Serializes wines for the api endpoint"""
    id = serializers.ReadOnlyField()

    class Meta:
        model = Wine
        fields = ('id', 'name', 'description', 'varietal')

    def create(self, data, winery_pk, wineline_pk):
        data['wine_line_id'] = wineline_pk
        data['winery_id'] = winery_pk
        wine = Wine.objects.create(**data)
        return wine


class WineLineSerializer(serializers.ModelSerializer):
    """Serializes a wine line for the api endpoint"""
    id = serializers.ReadOnlyField()
    wines = WineSerializer(many=True, read_only=True)

    class Meta:
        model = WineLine
        fields = ('id', 'name', 'description', 'wines')

    def create(self, data, winery_pk):
        data['winery_id'] = winery_pk
        wine_line = WineLine.objects.create(**data)
        return wine_line


class ImageUrlField(serializers.RelatedField):
    def to_representation(self, value):
        url = settings.MEDIA_URL + str(value.filefield)
        return url


class FileSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True, allow_null=False)
    filefield = serializers.ListField(child=serializers.FileField())


class WinerySerializer(serializers.ModelSerializer):
    """Serializes a winery for the api endpoint"""
    id = serializers.ReadOnlyField()
    wine_lines = WineLineSerializer(many=True, read_only=True)
    images = ImageUrlField(read_only=True, many=True)

    class Meta:
        model = Winery
        fields = ('id', 'name', 'description', 'website', 'wine_lines', 'available_since', 'location', 'images')


class EventBriefSerializer(serializers.ModelSerializer):
    """Serializer for event with rediced infromation only for reading purposes"""
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    winery = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'name', 'winery')


class EventOccurrenceSerializer(serializers.ModelSerializer):
    """Serializer for event occurrences """
    id = serializers.ReadOnlyField()
    event = EventBriefSerializer()

    class Meta:
        model = EventOccurrence
        fields = ('id', 'start', 'end', 'vacancies', 'event')


class ReservationSerializer(serializers.ModelSerializer):
    """Seriazlizer for Reservation"""
    id = serializers.ReadOnlyField()
    created_on = serializers.ReadOnlyField()

    class Meta:
        model = Reservation
        fields = (
            'id',
            'attendee_number',
            'observations',
            'created_on',
            'paid_amount',
            'user',
            'event_occurrence',
        )

    def validate(self, data):
        """
        Other validations
        """
        if data['event_occurrence'].event.price * data['attendee_number'] != data['paid_amount']:
            raise serializers.ValidationError('The paid amount is not valid')
        if data['event_occurrence'].vacancies < data['attendee_number']:
            raise serializers.ValidationError('Not enough vacancies for the reservation')
        if data['event_occurrence'].start < datetime.now():
            raise serializers.ValidationError('The date is no longer available')
        if data['event_occurrence'].event.cancelled:
            raise serializers.ValidationError('The event is cancelled')

        return data

    # Override serialization of event_occurrence only when readed
    def to_representation(self, obj):
        self.fields['event_occurrence'] = EventOccurrenceSerializer()
        return super().to_representation(obj)


class RateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Rate
        fields = ('user', 'rate', 'comment')

    def get_user(self, rate):
        return rate.user.full_name()

    def create(self, data, event_pk, user_pk):
        data['event_id'] = event_pk
        data['user_id'] = user_pk
        rate = Rate.objects.create(**data)
        return rate

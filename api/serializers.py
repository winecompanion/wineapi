from datetime import datetime
from winecompanion import settings

from django.db.models import Avg
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework.exceptions import ParseError
from rest_framework import serializers

from .models import (
    Country,
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


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for Countries"""
    id = serializers.ReadOnlyField

    class Meta:
        model = Country
        fields = ['id', 'name']


class VenueSerializer(serializers.ModelSerializer):
    """Serializer for event occurrences """
    id = serializers.ReadOnlyField()

    class Meta:
        model = EventOccurrence
        fields = ('id', 'start', 'end', 'vacancies')


class ImageUrlField(serializers.RelatedField):
    def to_representation(self, value):
        url = settings.MEDIA_URL + str(value.filefield)
        return url


class EventSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    categories = EventCategorySerializer(many=True)
    occurrences = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)
    current_user_rating = serializers.SerializerMethodField(read_only=True)
    schedule = ScheduleSerializer(many=True, write_only=True, allow_empty=False)
    tags = TagSerializer(many=True, required=False)
    vacancies = serializers.IntegerField(write_only=True)
    images = ImageUrlField(read_only=True, many=True)
    winery = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'description',
            'cancelled',
            'price',
            'rating',
            'current_user_rating',
            'tags',
            'categories',
            'winery',
            'occurrences',
            'schedule',
            'vacancies',
            'images',
        ]

    def create(self, data):
        # TODO: finish docstring
        """Creates and saves an Event associated to
        instances of EventOcurrence.

        Params:
        """
        request = self.context.get("request")
        if request.user.is_anonymous or not request.user.winery:
            raise serializers.ValidationError('You must have a winery to create events.')

        schedule = data.pop('schedule')
        vacancies = data.pop('vacancies')
        categories = data.pop('categories')
        tags = data.pop('tags') if 'tags' in data else []
        data['winery'] = request.user.winery
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
            event.categories.add(get_object_or_404(EventCategory, name=category['name']))

        for tag in tags:
            event.tags.add(get_object_or_404(Tag, name=tag['name']))

        return event

    def validate_categories(self, categories):
        """
        Check that the categories are valid
        """
        for category in categories:
            try:
                EventCategory.objects.get(name=category['name'])
            except EventCategory.DoesNotExist:
                raise serializers.ValidationError("category {} does not exist".format(category['name']))

        return categories

    def validate_tags(self, tags):
        """
        Check that the tags are valid
        """
        for tag in tags:
            try:
                Tag.objects.get(name=tag['name'])
            except Tag.DoesNotExist:
                raise serializers.ValidationError("tag {} does not exist".format(tag['name']))

        return tags

    def validate_vacancies(self, vacancies):
        if vacancies <= 0:
            raise serializers.ValidationError('The vacancies must be greater than cero.')
        return vacancies

    def validate(self, data):
        schedules = data.get('schedule')
        for schedule in schedules:
            end_date = schedule.get('to_date')
            start_date = schedule.get('from_date')
            if not start_date or datetime.now() > datetime.combine(start_date, schedule.get('start_time')):
                raise serializers.ValidationError({'from_date': 'Invalid start date'})
            if end_date and start_date > end_date:
                raise serializers.ValidationError({'to_date': 'End date must be greater than start date'})
        return data

    def get_occurrences(self, event):
        occurrences = EventOccurrence.objects.filter(event=event, start__gt=datetime.now())
        serializer = VenueSerializer(instance=occurrences, many=True)
        return serializer.data

    def get_rating(self, event):
        rate = Rate.objects.filter(event=event).aggregate(Avg('rate'))
        return rate['rate__avg']

    def get_current_user_rating(self, event):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return None
        user = request.user
        rate = Rate.objects.filter(event=event, user=user).first()
        return RateSerializer(rate).data if rate else None


class WineSerializer(serializers.ModelSerializer):
    """Serializes wines for the api endpoint"""
    id = serializers.ReadOnlyField()

    class Meta:
        model = Wine
        fields = ('id', 'name', 'description', 'varietal')

    def create(self, data, winery_pk, wineline_pk):
        data['wine_line_id'] = wineline_pk
        data['winery_id'] = winery_pk
        try:
            wine = Wine.objects.create(**data)
        except IntegrityError:
            raise ParseError(datail='Invalid winery or wine line.')
        return wine

    def to_representation(self, obj):
        self.fields['varietal'] = serializers.CharField(source='get_varietal_display')
        return super().to_representation(obj)


class WineLineSerializer(serializers.ModelSerializer):
    """Serializes a wine line for the api endpoint"""
    id = serializers.ReadOnlyField()
    wines = WineSerializer(many=True, read_only=True)

    class Meta:
        model = WineLine
        fields = ('id', 'name', 'description', 'wines')

    def create(self, data, winery_pk):
        data['winery_id'] = winery_pk
        try:
            wine_line = WineLine.objects.create(**data)
        except IntegrityError:
            raise ParseError(detail='Invalid winery')
        return wine_line


class FileSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True, allow_null=False)
    type = serializers.CharField(required=True, allow_null=False)
    filefield = serializers.ListField(child=serializers.FileField())


class WinerySerializer(serializers.ModelSerializer):
    """Serializes a winery for the api endpoint"""
    id = serializers.ReadOnlyField()
    wine_lines = WineLineSerializer(many=True, read_only=True)
    images = ImageUrlField(read_only=True, many=True)

    class Meta:
        model = Winery
        fields = ('id', 'name', 'description', 'website', 'wine_lines', 'location', 'images')


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
    event = EventBriefSerializer(read_only=True)

    class Meta:
        model = EventOccurrence
        fields = ('id', 'start', 'end', 'vacancies', 'event')

    def create(self, data, event_pk):
        event = Event.objects.filter(pk=event_pk).first()
        if not event:
            raise ParseError(detail='Invalid event.')
        if event.cancelled:
            raise serializers.ValidationError('This event is cancelled.')

        data['event_id'] = event_pk
        occurrence = EventOccurrence.objects.create(**data)
        return occurrence

    def validate(self, data):
        if data['start'] >= data['end']:
            raise serializers.ValidationError({'end': ['end date must be greater than start date']})
        return data


class ReservationSerializer(serializers.ModelSerializer):
    """Seriazlizer for Reservation"""
    id = serializers.ReadOnlyField()
    created_on = serializers.ReadOnlyField()
    user = serializers.SlugRelatedField(read_only=True, slug_field='email')

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

    def validate_attendee_number(self, attendee_number):
        if attendee_number <= 0:
            raise serializers.ValidationError('The attendee_number must be greater than cero')
        return attendee_number

    def create(self, data, user_pk):
        data['user_id'] = user_pk
        try:
            reservation = Reservation.objects.create(**data)
        except IntegrityError:
            raise ParseError(detail='Failed to create Reservation')
        return reservation

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
        self.fields['status'] = serializers.CharField(source='get_status_display')
        return super().to_representation(obj)


class RateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user_name = serializers.ReadOnlyField()
    date = serializers.DateTimeField(source='modified', read_only=True)

    class Meta:
        model = Rate
        fields = ('id', 'user_id', 'user_name', 'date', 'rate', 'comment')

    def create(self, data, event_pk, user_pk):
        data['event_id'] = event_pk
        data['user_id'] = user_pk
        try:
            rate = Rate.objects.create(**data)
        except IntegrityError:
            raise ParseError(detail='invalid event.')
        return rate

from datetime import datetime
from winecompanion import settings

from django.db.models import Avg
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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
    Mail,
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
                start = datetime.combine(date, start_time)
                end = datetime.combine(date, end_time)
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

    def update(self, instance, validated_data):
        """Event update method"""
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)

        vacancies = validated_data.get('vacancies')
        if vacancies:
            for elem in validated_data.get('schedule'):
                start_time = elem['start_time']
                end_time = elem['end_time']
                dates = Event.calculate_dates_in_threshold(
                        elem['from_date'],
                        elem['to_date'],
                        elem['weekdays'])

                for date in dates:
                    start = datetime.combine(date, start_time)
                    end = datetime.combine(date, end_time)
                    EventOccurrence.objects.create(
                        start=start,
                        end=end,
                        vacancies=vacancies,
                        event=instance
                    )

        categories = validated_data.get('categories', instance.categories.all())
        instance.categories.clear()
        for category in categories:
            instance.categories.add(get_object_or_404(EventCategory, name=category['name']))

        tags = validated_data.get('tags', instance.tags.all())
        instance.tags.clear()
        for tag in tags:
            instance.tags.add(get_object_or_404(Tag, name=tag['name']))

        instance.save()
        return instance

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

    def validate_schedule(self, schedules):
        for schedule in schedules:
            end_date = schedule.get('to_date')
            start_date = schedule.get('from_date')
            if not start_date or datetime.now() > datetime.combine(start_date, schedule.get('start_time')):
                raise serializers.ValidationError({'from_date': 'Invalid start date'})
            if end_date and start_date > end_date:
                raise serializers.ValidationError({'to_date': 'End date must be greater than start date'})
        return schedules

    def validate(self, data):
        if data.get('schedule') and not data.get('vacancies'):
            raise serializers.ValidationError({'vacancies': 'Vacancies must be specified'})
        return data

    def get_occurrences(self, event):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        occurrences = EventOccurrence.objects.filter(event=event)
        if not (request and getattr(user, 'winery', None) and user.winery == event.winery):
            occurrences = occurrences.filter(start__gt=datetime.now())
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
    images = ImageUrlField(read_only=True, many=True)

    class Meta:
        model = Wine
        fields = ('id', 'name', 'description', 'varietal', 'images')

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
    cancelled = serializers.ReadOnlyField()
    event = EventBriefSerializer(read_only=True)

    class Meta:
        model = EventOccurrence
        fields = ('id', 'start', 'end', 'cancelled', 'vacancies', 'event')

    def create(self, data, event_pk):
        event = Event.objects.filter(pk=event_pk).first()
        if not event:
            raise ParseError(detail='Invalid event.')
        if event.cancelled:
            raise serializers.ValidationError('This event is cancelled.')

        data['event_id'] = event_pk
        occurrence = EventOccurrence.objects.create(**data)
        return occurrence

    def update(self, instance, validated_data):
        start = validated_data.get('start')
        end = validated_data.get('end')
        instance.start = start or instance.start
        instance.end = end or instance.end
        instance.vacancies = validated_data.get('vacancies', instance.vacancies)
        instance.save()
        if start or end:
            for reservation in instance.reservation_set.all():
                # send email
                subject = 'Winecompanion Reservation Date Modified'
                html_message = render_to_string(
                    'reservation_edited_template.html',
                    {
                        'first_name': reservation.user.first_name,
                        'winery': instance.event.winery.name,
                        'id': instance.id,
                        'date': instance.start.strftime("%d/%m/%Y"),
                        'start': instance.start.time,
                        'end': instance.end.time,
                    }
                )
                plain_message = strip_tags(html_message)
                Mail.send_mail(subject, plain_message, [reservation.user.email], html_message=html_message)
        return instance

    def validate(self, data):
        start = data.get('start') or getattr(self.instance, 'start', None)
        if start and start < datetime.now():
            raise serializers.ValidationError({'start': ['Start datetime cannot be in the past']})
        end = data.get('end') or getattr(self.instance, 'end', None)
        if start and end and start >= end:
            raise serializers.ValidationError({'end': ['End date must be greater than start date']})
        return data


class ReservationSerializer(serializers.ModelSerializer):
    """Seriazlizer for Reservation"""
    id = serializers.ReadOnlyField()
    created_on = serializers.ReadOnlyField()
    user = serializers.SlugRelatedField(read_only=True, slug_field='email')
    user_first_name = serializers.SlugRelatedField(source='user', read_only=True, slug_field='first_name')
    user_last_name = serializers.SlugRelatedField(source='user', read_only=True, slug_field='last_name')

    class Meta:
        model = Reservation
        fields = (
            'id',
            'attendee_number',
            'observations',
            'created_on',
            'paid_amount',
            'user',
            'user_first_name',
            'user_last_name',
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
        if data['event_occurrence'].cancelled:
            raise serializers.ValidationError('This venue is no longer available')

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

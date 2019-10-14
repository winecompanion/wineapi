from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import DateTimeFromToRangeFilter, FilterSet, ModelMultipleChoiceFilter
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from . import VARIETALS
from .models import (
    Country,
    Event,
    EventCategory,
    EventOccurrence,
    Rate,
    Reservation,
    Tag,
    Wine,
    WineLine,
    Winery,
    ImagesWinery,
    ImagesEvent,
)
from .serializers import (
    CountrySerializer,
    EventCategorySerializer,
    EventOccurrenceSerializer,
    EventSerializer,
    RateSerializer,
    ReservationSerializer,
    TagSerializer,
    WinerySerializer,
    WineLineSerializer,
    WineSerializer,
    FileSerializer,
)


class EventFilter(FilterSet):
    # https://django-filter.readthedocs.io/en/latest/guide/usage.html#declaring-filters

    start = DateTimeFromToRangeFilter(field_name='occurrences__start')
    category = ModelMultipleChoiceFilter(
        field_name='categories__name',
        to_field_name='name',
        queryset=EventCategory.objects.all()
    )
    tag = ModelMultipleChoiceFilter(
        field_name='tags__name',
        to_field_name='name',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Event
        fields = ['occurrences__start', 'category', 'tag']


class EventsView(viewsets.ModelViewSet):
    queryset = Event.objects.filter(
        occurrences__start__gt=datetime.now()
    ).exclude(categories__name__icontains='restaurant').distinct()

    serializer_class = EventSerializer

    # search elements (must use search= as query params)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']

    # filter elements (must use field= as query params )
    filterset_class = EventFilter

    def create(self, request):
        serializer = EventSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        event = serializer.create(serializer.validated_data)
        return Response({'url': reverse('event-detail', args=[event.id])}, status=status.HTTP_201_CREATED)


class WineryView(viewsets.ModelViewSet):
    queryset = Winery.objects.all()
    serializer_class = WinerySerializer

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    http_method_names = ['get', 'head', 'put', 'patch']

    @action(detail=True, methods=['get'], name='get-winery-events')
    def events(self, request, pk=None):
        query = Event.objects.filter(
            occurrences__start__gt=datetime.now(), winery=pk
        ).distinct()
        events = EventSerializer(query, many=True)
        return Response(events.data, status=status.HTTP_200_OK)


class WineView(viewsets.ModelViewSet):
    serializer_class = WineSerializer

    def create(self, request, winery_pk, wineline_pk):
        serializer = WineSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        wine = serializer.create(serializer.validated_data, winery_pk, wineline_pk)
        return Response({
            'url': reverse(
                    'wines-detail',
                    kwargs={'winery_pk': winery_pk, 'wineline_pk': wineline_pk, 'pk': wine.id}
                    )
            },
            status=status.HTTP_201_CREATED
        )

    def get_queryset(self):
        wine_line = get_object_or_404(WineLine, id=self.kwargs['wineline_pk'])
        winery = get_object_or_404(Winery, id=self.kwargs['winery_pk'])
        if wine_line.winery.id != winery.id:
            raise PermissionDenied(detail="winery and wine line don't match")
        return Wine.objects.filter(wine_line=wine_line.id)


class WineLineView(viewsets.ModelViewSet):
    serializer_class = WineLineSerializer

    def create(self, request, winery_pk):
        serializer = WineLineSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        wine_line = serializer.create(serializer.validated_data, winery_pk)
        return Response(
            {'url': reverse('winelines-detail', kwargs={'winery_pk': winery_pk, 'pk': wine_line.id})},
            status=status.HTTP_201_CREATED)

    def get_queryset(self):
        winery = get_object_or_404(Winery, id=self.kwargs['winery_pk'])
        return WineLine.objects.filter(winery=winery.id)


class MapsView(APIView):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q')
        r = request.GET.get('r')
        if r is None:
            r = 100
        try:
            q = 'POINT({})'.format(q.replace(',', ' '))
            queryset = Winery.get_nearly_wineries(q, r)
            serializer = WinerySerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return Response({'errors': 'Invalid Request.'}, status=status.HTTP_400_BAD_REQUEST)


class TagView(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    model_class = Tag

    def create(self, request):
        serializer = TagSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        tag = serializer.create(serializer.validated_data)
        return Response(
            {'url': reverse('tags-detail', args=[tag.id])},
            status=status.HTTP_201_CREATED)


class CountryView(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    model_class = Country

    # TODO: permission_classes

    def create(self, request):
        serializer = CountrySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        country = serializer.create(serializer.validated_data)
        return Response(
            {'url': reverse('countries-detail', args=[country.id])},
            status=status.HTTP_201_CREATED)


class EventCategoryView(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    model_class = EventCategory

    def create(self, request):
        serializer = EventCategorySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        event_category = serializer.create(serializer.validated_data)
        return Response(
            {'url': reverse('event-categories-detail', args=[event_category.id])},
            status=status.HTTP_201_CREATED)


class ReservationView(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    model_class = Reservation

    # Todo: use logged user
    def create(self, request):
        serializer = ReservationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        reservation = serializer.create(serializer.validated_data)

        # get event occurrency and decrement vacancies
        event_occurrence = get_object_or_404(EventOccurrence, pk=request.data['event_occurrence'])
        event_occurrence.vacancies -= int(request.data['attendee_number'])
        event_occurrence.save()
        return Response(
            {'url': reverse('reservations-detail', args=[reservation.id])},
            status=status.HTTP_201_CREATED)


class VarietalsView(APIView):
    def get(self, request):
        varietals = [{'id': k, 'value': v} for k, v in VARIETALS]
        return Response(varietals)


class RatingView(viewsets.ModelViewSet):
    serializer_class = RateSerializer
    model_class = Rate

    @permission_classes([IsAuthenticated])
    def create(self, request, event_pk):
        serializer = RateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        rate = serializer.create(serializer.validated_data, event_pk, user.id)
        return Response(
            {'url': reverse('event-ratings-detail', kwargs={'event_pk': event_pk, 'pk': rate.id})},
            status=status.HTTP_201_CREATED)

    def get_queryset(self):
        event = get_object_or_404(Event, id=self.kwargs['event_pk'])
        return Rate.objects.filter(event=event.id)


class FileUploadView(APIView):
    def post(self, request):
        serializer = FileSerializer(data=request.data)
        model = None
        kwargs = {}

        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data['type'] == 'winery':
            model = ImagesWinery
            kwargs['winery'] = get_object_or_404(Winery, pk=serializer.validated_data['id'])
        elif serializer.validated_data['type'] == 'event':
            model = ImagesEvent
            kwargs['event'] = get_object_or_404(Event, pk=serializer.validated_data['id'])
        else:
            return Response({'errors': 'Type not found'}, status=status.HTTP_400_BAD_REQUEST)

        for onefile in serializer.validated_data['filefield']:
            model.objects.create(filefield=onefile, **kwargs)
        return Response(status=status.HTTP_201_CREATED)


class RestaurantsView(APIView):
    def get(self, request):
        query = Event.objects.filter(
            occurrences__start__gt=datetime.now(), categories__name__icontains='restaurant'
        ).distinct()
        restaurants = EventSerializer(query, many=True)
        return Response(restaurants.data, status=status.HTTP_200_OK)


class EventOccurrencesView(viewsets.ModelViewSet):
    serializer_class = EventOccurrenceSerializer
    model_class = EventOccurrence

    def create(self, request, event_pk):
        serializer = EventOccurrenceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        occurrence = serializer.create(serializer.validated_data, event_pk)
        return Response(
            {'url': reverse('event-occurrences-detail', kwargs={'event_pk': event_pk, 'pk': occurrence.id})},
            status=status.HTTP_201_CREATED)

    def get_queryset(self):
        event = get_object_or_404(Event, id=self.kwargs['event_pk'])
        return EventOccurrence.objects.filter(event=event.id)

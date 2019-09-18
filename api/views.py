from datetime import datetime

from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import DateTimeFromToRangeFilter, FilterSet, ModelMultipleChoiceFilter

from .models import (
    Event,
    EventCategory,
    EventOccurrence,
    Reservation,
    Tag,
    Wine,
    WineLine,
    Winery,
)
from .serializers import (
    EventCategorySerializer,
    EventSerializer,
    ReservationSerializer,
    TagSerializer,
    WinerySerializer,
    WineLineSerializer,
    WineSerializer,
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
    queryset = Event.objects.filter(occurrences__start__gt=datetime.now()).distinct()
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

    # to do: filterset_class

    def create(self, request):
        serializer = WinerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        winery = serializer.create(serializer.validated_data)
        return Response({'url': reverse('winery-detail', args=[winery.id])}, status=status.HTTP_201_CREATED)


class WineView(viewsets.ModelViewSet):
    queryset = Wine.objects.all()
    serializer_class = WineSerializer

    def create(self, request):
        serializer = WineSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        wine = serializer.create(serializer.validated_data)
        return Response({'url': reverse('wine-detail', args=[wine.id])}, status=status.HTTP_201_CREATED)


class WineLineView(viewsets.ModelViewSet):
    queryset = WineLine.objects.all()
    serializer_class = WineLineSerializer

    def create(self, request):
        serializer = WineLineSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        wine_line = serializer.create(serializer.validated_data)
        return Response(
            {'url': reverse('wine-line-detail', args=[wine_line.id])},
            status=status.HTTP_201_CREATED)


class MapsView(APIView):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q')
        try:
            q = 'POINT({})'.format(q.replace(',', ' '))
            queryset = Winery.get_nearly_wineries(q)
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
        event_occurrence = EventOccurrence.objects.get(pk=request.data['event_occurrence'])
        event_occurrence.vacancies -= int(request.data['attendee_number'])
        event_occurrence.save()
        return Response(
            {'url': reverse('reservations-detail', args=[reservation.id])},
            status=status.HTTP_201_CREATED)

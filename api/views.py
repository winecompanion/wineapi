import datetime

from rest_framework import viewsets, status
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, DateTimeFromToRangeFilter, ModelMultipleChoiceFilter

from .models import Event, Winery, WineLine, Wine, EventCategory, Tag
from .serializers import (
    EventSerializer,
    EventCategorySerializer,
    WinerySerializer,
    WineLineSerializer,
    WineSerializer,
    MapsSerializer,
    TagSerializer,
)


class EventFilter(FilterSet):
    # https://django-filter.readthedocs.io/en/latest/guide/usage.html#declaring-filters

    start = DateTimeFromToRangeFilter(field_name='occurrences__start')
    category = ModelMultipleChoiceFilter(
        field_name='categories__name',
        to_field_name='name',
        queryset=EventCategory.objects.all()
    )

    class Meta:
        model = Event
        fields = ['occurrences__start', 'category']


class EventsView(viewsets.ModelViewSet):
    queryset = Event.objects.filter(occurrences__start__gt=datetime.datetime.now())
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


class MapsView(viewsets.ViewSet):
    def create(self, request):
        serializer = MapsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.data['location']:
            location = serializer.data['location']
            queryset = Winery.get_nearly_wineries(location)
            serializer = WinerySerializer(queryset, many=True)
            return Response(serializer.data)


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

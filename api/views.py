import datetime

from rest_framework import viewsets, status
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, DateFilter

from .models import Event
from .serializers import EventSerializer


class EventFilter(FilterSet):
    # https://django-filter.readthedocs.io/en/latest/guide/usage.html#declaring-filters

    to_date = DateFilter(field_name='occurrences__start', lookup_expr='lt')

    class Meta:
        model = Event
        fields = ['occurrences__start']


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

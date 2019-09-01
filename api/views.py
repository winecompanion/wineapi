import datetime

from rest_framework import viewsets, status
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework import filters

from .models import Event
from .serializers import EventSerializer


class EventsView(viewsets.ModelViewSet):
    queryset = Event.objects.filter(occurrences__start__gt=datetime.datetime.now())
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def create(self, request):
        serializer = EventSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        event = serializer.create(serializer.validated_data)
        return Response({'url': reverse('event-detail', args=[event.id])}, status=status.HTTP_201_CREATED)

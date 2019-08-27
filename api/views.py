from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Event
from .serializers import EventSerializer, CreateRecurrentEventsSerializer


class EventsView(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('name')
    serializer_class = EventSerializer

    @action(detail=True, methods=['post'])
    def CreateRecurrentEvents(self, request, pk=None):
        event = self.get_object()
        serializer = CreateRecurrentEventsSerializer(data=request.data)
        if serializer.is_valid():
            # evento.calculate_dates_in_threshold(serializer.data['fechaInicio'], serializer.data['fechaFin'],serializer.data['diadelasemana'])
            # user.save()
            return Response(
                    event.calculate_dates_in_threshold(
                        serializer.data['start'],
                        serializer.data['end'],
                        serializer.data['weekdays']
                    )
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

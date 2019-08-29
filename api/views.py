from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Event, EventOccurrence
from .serializers import EventSerializer, ScheduleSerializer


class EventsView(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('name')
    serializer_class = EventSerializer
    
    def create(self, request):
        serializer = RecurrentEventSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.calculate(request.data), status=status.HTTP_200_OK)                
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

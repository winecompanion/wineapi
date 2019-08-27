from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Event, EventOccurrence
from .serializers import EventSerializer, RecurrentEventSerializer, ScheduleSerializer


class EventsView(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('name')
    serializer_class = EventSerializer
    
    #@action(detail=True, methods=['post'])
    def create(self, request):
        serializerRecurrent = RecurrentEventSerializer(data=request.data)
        if serializerRecurrent.is_valid():
            return Response(serializerRecurrent.Calculate(request.data))                
            #return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializerRecurrent.errors, status=status.HTTP_400_BAD_REQUEST)

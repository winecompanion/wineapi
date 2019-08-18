from rest_framework.views import APIView
from rest_framework.response import Response


class EventListView(APIView):
    """Event List View for home page"""

    def get(self, request, format=None):
        """Returns a list of Events available"""
        example_event = {'name': 'Hello Event', 'description': 'Example Event'}

        return Response(example_event)


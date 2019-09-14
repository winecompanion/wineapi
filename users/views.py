from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.reverse import reverse


from .models import WineUser, UserSerializer


class WineUserView(viewsets.ModelViewSet):
    queryset = WineUser.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        wine_user = serializer.create(serializer.validated_data)
        return Response({'url': reverse('users-detail', args=[wine_user.id])}, status=status.HTTP_201_CREATED)

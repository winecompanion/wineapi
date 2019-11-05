from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import get_object_or_404

from . import LANGUAGES, GENDERS
from .models import WineUser, UserSerializer
from api.models import Reservation, Mail
from api.serializers import ReservationSerializer

from .permissions import (
    AllowCreateUserButUpdateOwnerOnly,
    ListAdminOnly,
)


class WineUserView(viewsets.ModelViewSet):
    queryset = WineUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = [ListAdminOnly, AllowCreateUserButUpdateOwnerOnly]

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        wine_user = serializer.create(serializer.validated_data)

        # send email
        subject = 'Bienvenido a Winecompanion'
        html_message = render_to_string(
            'user_registration_template.html',
        )
        plain_message = strip_tags(html_message)
        Mail.send_mail(subject, plain_message, [wine_user.email], html_message=html_message)

        return Response({'url': reverse('users-detail', args=[wine_user.id])}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], name='get-user-reservations')
    def reservations(self, request):
        if request.user.is_anonymous:
            return Response([], status=status.HTTP_200_OK)
        res = Reservation.objects.filter(user=request.user.id).order_by('-id')
        reservations = ReservationSerializer(res, many=True)
        return Response(reservations.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], name='set-password')
    def set_password(self, request, pk):
        user = get_object_or_404(WineUser, id=pk)
        if user != request.user:
            return Response({'detail': 'Permission Denied'}, status=status.HTTP_403_FORBIDDEN)
        password = request.data.get('password')
        if password:
            user.set_password(password)
            user.save()
            return Response({'detail': 'Password updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': 'Password not provided'}, status=status.HTTP_400_BAD_REQUEST)


class LanguagesView(APIView):
    def get(self, request):
        languages = [{'id': k, 'value': v} for k, v in LANGUAGES]
        return Response(languages)


class GendersView(APIView):
    def get(self, request):
        genders = [{'id': k, 'value': v} for k, v in GENDERS]
        return Response(genders)

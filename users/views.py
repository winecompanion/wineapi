from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings

from . import LANGUAGES, GENDERS
from .models import WineUser, UserSerializer
from api.models import Reservation, Mail
from api.serializers import ReservationSerializer

from .permissions import (
    AllowCreateUserButUpdateOwnerOnly,
    ListAdminOnly,
)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # send email
    token = reset_password_token.key
    url = settings.URL_FRONT_END
    subject = 'Winecompanion - Password Assistance'
    html_message = render_to_string(
            'reset_password_template.html',
            {
                'user': reset_password_token.user.first_name,
                'url': "{}{}confirm/{}".format(url, reverse('password_reset:reset-password-request'), token),
            }
        )
    plain_message = strip_tags(html_message)
    Mail.send_mail(subject, plain_message, [reset_password_token.user.email], html_message=html_message)


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


class LanguagesView(APIView):
    def get(self, request):
        languages = [{'id': k, 'value': v} for k, v in LANGUAGES]
        return Response(languages)


class GendersView(APIView):
    def get(self, request):
        genders = [{'id': k, 'value': v} for k, v in GENDERS]
        return Response(genders)

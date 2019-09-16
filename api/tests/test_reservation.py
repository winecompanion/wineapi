from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from rest_framework import status

from api.models import Reservation, Event, EventOccurrence, Winery
from api.serializers import ReservationSerializer, EventBriefSerializer, EventOccurrenceSerializer

from users.models import WineUser


class TestReservation(TestCase):
    def setUp(self):
        self.user = WineUser.objects.create_user(
            email='user@user.com',
            password='12345678',
        )
        self.winery = Winery.objects.create(
                name='My Winery',
                description='Test Winery',
                website='website.com',
        )
        self.event = Event.objects.create(
            name='Wanted Event',
            description='Should be showed',
            winery=self.winery,
            price=500.0
        )
        self.event_occ = EventOccurrence.objects.create(
            start='2020-10-31T20:00:00',
            end='2020-10-31T23:00:00',
            vacancies=50,
            event=self.event
        )

        self.valid_creation_data = {
                'attendee_number': 2,
                'observations': 'No kids',
                'ammount_payed': 1000.0,
                'user': self.user,
                'event_occurrence': self.event_occ,
        }
        self.valid_reservation_json_data = {
                'attendee_number': 2,
                'observations': 'No kids',
                'ammount_payed': 1000.0,
                'user': self.user.id,
                'event_occurrence': self.event_occ.id,
        }
        self.invalid_reservation_data = {
                'observations': 'observations',
        }
        self.required_fields = set(['attendee_number', 'ammount_payed', 'user', 'event_occurrence'])
        self.client = Client()

    def test_reservation_creation(self):
        reservation = Reservation(**self.valid_creation_data)
        reservation.full_clean()
        reservation.save()

    def test_invalid_reservation_creation(self):
        reservation = Reservation(**self.invalid_reservation_data)
        with self.assertRaises(Exception):
            reservation.full_clean()

    def test_reservation_serializer(self):
        serializer = ReservationSerializer(data=self.valid_reservation_json_data)
        self.assertTrue(serializer.is_valid())
        reservation_fields = ['attendee_number', 'observations', 'ammount_payed', 'user', 'event_occurrence']
        self.assertEqual(set(serializer.data.keys()), set(reservation_fields))

    def test_invalid_reservation_serializer(self):
        serializer = ReservationSerializer(data=self.invalid_reservation_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), self.required_fields)

    def test_reservation_endpoint_get(self):
        response = self.client.get(
            reverse('reservations-list')
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_reservation_endpoint_create(self):
        response = self.client.post(
            reverse('reservations-list'),
            self.valid_reservation_json_data
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_reservation_endpoint_create_with_invalid_data(self):
        response = self.client.post(
            reverse('reservations-list'),
            self.invalid_reservation_data
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['errors'].keys(), self.required_fields)

    def test_reservation_detail_get(self):
        reservation = Reservation.objects.create(**self.valid_creation_data)
        response = self.client.get(
            reverse('reservations-detail', kwargs={'pk': reservation.id})
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        serializer = ReservationSerializer(reservation)
        self.assertEqual(response.data, serializer.data)

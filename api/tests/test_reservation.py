from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from api.models import Reservation, Event, EventOccurrence, Winery
from api.serializers import ReservationSerializer

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
                'paid_ammount': 1000.0,
                'user': self.user,
                'event_occurrence': self.event_occ,
        }
        self.valid_reservation_json_data = {
                'attendee_number': 2,
                'observations': 'No kids',
                'paid_ammount': 1000.0,
                'user': self.user.id,
                'event_occurrence': self.event_occ.id,
        }
        self.invalid_reservation_data = {
                'observations': 'observations',
        }
        self.required_fields = set(['attendee_number', 'paid_ammount', 'user', 'event_occurrence'])
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
        reservation_fields = ['attendee_number', 'observations', 'paid_ammount', 'user', 'event_occurrence']
        self.assertEqual(set(serializer.data.keys()), set(reservation_fields))

    def test_invalid_reservation_serializer(self):
        serializer = ReservationSerializer(data=self.invalid_reservation_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), self.required_fields)

    def test_invalid_reservation_paid_ammount_serializer(self):
        test_data = self.valid_reservation_json_data
        test_data['paid_ammount'] = 1234.0  # not valid since it should be 2*500=1000
        serializer = ReservationSerializer(data=test_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors['non_field_errors']), set(['The paid ammount is not valid']))

    def test_invalid_reservation_not_enough_vacancies(self):
        test_data = self.valid_reservation_json_data
        test_data['paid_ammount'] = 25500.0
        test_data['attendee_number'] = 51
        serializer = ReservationSerializer(data=test_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors['non_field_errors']), set(['Not enough vacancies for the reservation']))

    def test_invalid_reservation_old_occurrence(self):
        occurrence = EventOccurrence.objects.create(
            start='2018-10-31T20:00:00',
            end='2018-10-31T23:00:00',
            vacancies=50,
            event=self.event
        )
        test_data = self.valid_reservation_json_data
        test_data['event_occurrence'] = occurrence.id
        serializer = ReservationSerializer(data=test_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors['non_field_errors']), set(['The date is no longer available']))

    def test_invalid_reservation_event_cancelled(self):
        cancelled_event = Event.objects.create(
            name='Event Cancelled',
            description='Shouldnt be able to make a reservation',
            cancelled='2019-9-15T20:00:00',
            winery=self.winery,
            price=500.0,
        )
        occurrence = EventOccurrence.objects.create(
            start='2030-10-31T20:00:00',
            end='2030-10-31T23:00:00',
            vacancies=50,
            event=cancelled_event
        )
        test_data = self.valid_reservation_json_data
        test_data['event_occurrence'] = occurrence.id
        serializer = ReservationSerializer(data=test_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors['non_field_errors']), set(['The event is cancelled']))

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

    def test_reservation_creation_vacancies_decrement(self):
        previous_vacancies = self.event_occ.vacancies
        self.client.post(
            reverse('reservations-list'),
            self.valid_reservation_json_data
        )
        self.event_occ.refresh_from_db()
        new_vacancies = self.event_occ.vacancies
        self.assertEqual(new_vacancies, previous_vacancies - self.valid_reservation_json_data['attendee_number'])

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

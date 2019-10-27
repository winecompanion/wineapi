from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from api import RESERVATION_CONFIRMED, RESERVATION_CANCELLED
from api.models import Country, Event, EventOccurrence, Reservation, Winery
from api.serializers import ReservationSerializer

from users import GENDER_OTHER, LANGUAGE_ENGLISH
from users.models import WineUser


class TestReservation(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='Argentina')
        self.winery = Winery.objects.create(
                name='My Winery',
                description='Test Winery',
                website='website.com',
                available_since=datetime.now()
        )
        self.user = WineUser.objects.create_user(
            email='user@user.com',
            password='12345678',
            first_name='User',
            last_name='Test',
            gender=GENDER_OTHER,
            language=LANGUAGE_ENGLISH,
            country=self.country,
            winery=self.winery,
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
                'paid_amount': 1000.0,
                'user': self.user,
                'event_occurrence': self.event_occ,
        }
        self.valid_reservation_json_data = {
                'attendee_number': 2,
                'observations': 'No kids',
                'paid_amount': 1000.0,
                'event_occurrence': self.event_occ.id,
        }
        self.invalid_reservation_data = {
                'observations': 'observations',
        }
        self.required_fields = set(['attendee_number', 'paid_amount', 'event_occurrence'])
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
        reservation_fields = ['attendee_number', 'observations', 'paid_amount', 'event_occurrence']
        self.assertEqual(set(serializer.validated_data.keys()), set(reservation_fields))

    def test_invalid_reservation_serializer(self):
        serializer = ReservationSerializer(data=self.invalid_reservation_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), self.required_fields)

    def test_invalid_reservation_paid_amount_serializer(self):
        test_data = self.valid_reservation_json_data
        test_data['paid_amount'] = 1234.0  # not valid since it should be 2*500=1000
        serializer = ReservationSerializer(data=test_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors['non_field_errors']), set(['The paid amount is not valid']))

    def test_invalid_reservation_not_enough_vacancies(self):
        test_data = self.valid_reservation_json_data
        test_data['paid_amount'] = 25500.0
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
        self.country = Country.objects.create(name='Argentina')
        admin_user = WineUser.objects.create_user(
            email='user@admin.com',
            password='12345678',
            is_staff=True,
            gender=GENDER_OTHER,
            language=LANGUAGE_ENGLISH,
            country=self.country,
        )
        self.client.force_login(admin_user)
        response = self.client.get(
            reverse('reservations-list')
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_reservation_endpoint_create(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('reservations-list'),
            self.valid_reservation_json_data
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_reservation_creation_vacancies_decrement(self):
        self.client.force_login(self.user)
        previous_vacancies = self.event_occ.vacancies
        self.client.post(
            reverse('reservations-list'),
            self.valid_reservation_json_data
        )
        self.event_occ.refresh_from_db()
        new_vacancies = self.event_occ.vacancies
        self.assertEqual(new_vacancies, previous_vacancies - self.valid_reservation_json_data['attendee_number'])

    def test_reservation_endpoint_create_with_invalid_data(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('reservations-list'),
            self.invalid_reservation_data
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['errors'].keys(), self.required_fields)

    def test_reservation_detail_get(self):
        self.client.force_login(self.user)
        reservation = Reservation.objects.create(**self.valid_creation_data)
        response = self.client.get(
            reverse('reservations-detail', kwargs={'pk': reservation.id})
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        serializer = ReservationSerializer(reservation)
        self.assertEqual(response.data, serializer.data)

    def test_get_user_reservations(self):
        self.client.force_login(self.user)
        reservation = Reservation.objects.create(**self.valid_creation_data)
        response = self.client.get(
            reverse('users-reservations')
        )
        self.assertDictContainsSubset({'id': reservation.id}, response.data[0])

    def test_get_user_reservations_not_logged_in(self):
        Reservation.objects.create(**self.valid_creation_data)
        response = self.client.get(
            reverse('users-reservations')
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cancel_reservation(self):
        self.client.force_login(self.user)
        reservation = Reservation.objects.create(**self.valid_creation_data)
        self.assertEqual(reservation.status, RESERVATION_CONFIRMED)
        old_vacancies = self.event_occ.vacancies

        # cancel the reservation
        response = self.client.post(
            reverse('reservations-cancel-reservation', kwargs={'pk': reservation.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, RESERVATION_CANCELLED)

        self.event_occ.refresh_from_db()
        self.assertEqual(self.event_occ.vacancies, old_vacancies + reservation.attendee_number)

    def test_cancel_event_cancels_reservations(self):
        self.client.force_login(self.user)
        reservation = Reservation.objects.create(**self.valid_creation_data)

        old_occurrence = EventOccurrence.objects.create(
            start='2018-10-31T20:00:00',
            end='2018-10-31T23:00:00',
            vacancies=50,
            event=self.event
        )
        self.valid_creation_data['event_occurrence'] = old_occurrence
        old_reservation = Reservation.objects.create(**self.valid_creation_data)

        self.client.post(
            reverse('event-cancel-event', kwargs={'pk': self.event.id})
        )
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, RESERVATION_CANCELLED)
        self.assertEqual(old_reservation.status, RESERVATION_CONFIRMED)

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from api.models import (
    Country,
    Event,
    EventCategory,
    EventOccurrence,
    Reservation,
    Winery,
)
from users import (
    GENDER_MALE,
    GENDER_FEMALE,
    GENDER_OTHER,
    LANGUAGE_SPANISH,
    LANGUAGE_ENGLISH,
    LANGUAGE_FRENCH,
)
from users.models import WineUser


class TestReports(TestCase):
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(name='Argentina')

        self.winery = Winery.objects.create(
            name='My Winery',
            description='Test Winery',
            website='website.com',
        )
        self.user = WineUser.objects.create_user(
            email='example@winecompanion.com',
            password='testuserpass',
            first_name='First Name',
            last_name='Last Name',
            gender=GENDER_OTHER,
            language=LANGUAGE_ENGLISH,
            phone='2616489178',
            country=self.country,
            winery=self.winery,
        )
        self.tourist_1 = WineUser.objects.create_user(
            email='example2@winecompanion.com',
            password='testuserpass',
            first_name='First Name',
            last_name='Last Name',
            gender=GENDER_MALE,
            language=LANGUAGE_SPANISH,
            phone='2616489178',
            country=self.country,
        )
        self.tourist_2 = WineUser.objects.create_user(
            email='example3@winecompanion.com',
            password='testuserpass',
            first_name='First Name',
            last_name='Last Name',
            gender=GENDER_FEMALE,
            language=LANGUAGE_FRENCH,
            phone='2616489178',
            country=self.country,
        )
        self.event_category = EventCategory.objects.create(name="Test category")
        self.event_1 = Event.objects.create(
            name='Experiencia Malbec',
            description='a test event',
            winery=self.winery,
            price=500.0
        )
        self.event_2 = Event.objects.create(
            name='Gran cabalgata',
            description='a test event',
            winery=self.winery,
            price=500.0
        )
        self.event_1.categories.add(self.event_category)
        self.event_2.categories.add(self.event_category)
        self.event_occ_october = EventOccurrence.objects.create(
            start='2020-10-31T20:00:00',
            end='2020-10-31T23:00:00',
            vacancies=50,
            event=self.event_1
        )
        self.event_occ_december = EventOccurrence.objects.create(
            start='2020-12-11T20:00:00',
            end='2020-12-11T23:00:00',
            vacancies=50,
            event=self.event_1
        )
        self.reservation_1 = Reservation.objects.create(
            attendee_number=2,
            observations='No kids',
            paid_amount=1000.0,
            user=self.tourist_1,
            event_occurrence=self.event_occ_october,
        )
        self.reservation_2 = Reservation.objects.create(
            attendee_number=2,
            observations='No kids',
            paid_amount=1000.0,
            user=self.tourist_2,
            event_occurrence=self.event_occ_october,
        )
        self.reservation_3 = Reservation.objects.create(
            attendee_number=2,
            observations='No kids',
            paid_amount=1000.0,
            user=self.tourist_2,
            event_occurrence=self.event_occ_december,
        )

    def test_reservations_report(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('reservation-count-reports'),
        )
        expected_reservations_by_event = [
            {
                "name": self.event_1.name,
                "count": 3,
            }
        ]
        expected_reservations_by_month = [
            {
                "month": 1,
                "count": 0,
            },
            {
                "month": 2,
                "count": 0,
            },
            {
                "month": 3,
                "count": 0,
            },
            {
                "month": 4,
                "count": 0,
            },
            {
                "month": 5,
                "count": 0,
            },
            {
                "month": 6,
                "count": 0,
            },
            {
                "month": 7,
                "count": 0,
            },
            {
                "month": 8,
                "count": 0,
            },
            {
                "month": 9,
                "count": 0,
            },
            {
                "month": 10,
                "count": 2,
            },
            {
                "month": 11,
                "count": 0,
            },
            {
                "month": 12,
                "count": 1,
            },
        ]
        expected_attendees_languages = [
            {
                'language': 'French',
                'count': 2,
            },
            {
                'language': 'Spanish',
                'count': 1,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data['reservations_by_event']), expected_reservations_by_event)
        self.assertEqual(list(response.data['reservations_by_month']), expected_reservations_by_month)
        self.assertEqual(list(response.data['attendees_languages']), expected_attendees_languages)

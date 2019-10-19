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
from users import GENDER_OTHER, LANGUAGE_ENGLISH
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
        self.event_occ = EventOccurrence.objects.create(
            start='2020-10-31T20:00:00',
            end='2020-10-31T23:00:00',
            vacancies=50,
            event=self.event_1
        )
        self.reservation = Reservation.objects.create(
            attendee_number=2,
            observations='No kids',
            paid_amount=1000.0,
            user=self.user,
            event_occurrence=self.event_occ,
        )

    def test_reservations_report(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('reservation-count-reports'),
        )
        expected_reservations_by_event = [
            {
                "name": self.event_1.name,
                "count": 1,
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
                "count": 1,
            },
            {
                "month": 11,
                "count": 0,
            },
            {
                "month": 12,
                "count": 0,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data['reservations_by_event']), expected_reservations_by_event)
        self.assertEqual(list(response.data['reservations_by_month']), expected_reservations_by_month)

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from users import GENDER_OTHER, LANGUAGE_ENGLISH
from api.models import Country, Event, EventOccurrence, Rate, Winery
from api.serializers import RateSerializer
from users.models import WineUser


class TestRatings(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='Argentina')
        self.user = WineUser.objects.create_user(
            email='user@test.com',
            password='abcd',
            first_name='Test',
            last_name='User',
            gender=GENDER_OTHER,
            language=LANGUAGE_ENGLISH,
            country=self.country
        )
        self.winery = Winery.objects.create(
            name='Winery',
            description='Test Winery',
        )
        self.event = Event.objects.create(
            name='Event 1',
            description='Desc 1',
            winery=self.winery,
            price=0.0
        )
        self.valid_rate_json_data = {
                'rate': 3,
                'comment': 'Test Rating',
                'event': self.event.id,
                'user': self.user.id,
        }
        self.valid_rate_creation_data = {
                'rate': 3,
                'comment': 'Test Rating',
                'event': self.event,
                'user': self.user,
        }
        self.invalid_rate_data = {
                'comment': 'description',
        }
        self.required_fields = set(['rate', ])
        self.client = Client()

    def test_event_rate_creation(self):
        rate = Rate(**self.valid_rate_creation_data)
        rate.full_clean()
        rate.save()

    def test_invalid_rate_creation(self):
        rate = Rate(**self.invalid_rate_data)
        with self.assertRaises(Exception):
            rate.full_clean()

    def test_rate_serializer(self):
        serializer = RateSerializer(data=self.valid_rate_json_data)
        self.assertTrue(serializer.is_valid())
        rate_fields = ['rate', 'comment']
        self.assertEqual(set(serializer.validated_data.keys()), set(rate_fields))

    def test_invalid_rate_serializer(self):
        serializer = RateSerializer(data=self.invalid_rate_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), self.required_fields)

    def test_rate_endpoint_get(self):
        response = self.client.get(
            reverse('event-ratings-list', kwargs={'event_pk': self.event.id})
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_rate_endpoint_create(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('event-ratings-list', kwargs={'event_pk': self.event.id}),
            self.valid_rate_json_data
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_rate_endpoint_create_with_invalid_data(self):
        response = self.client.post(
            reverse('event-ratings-list', kwargs={'event_pk': self.event.id}),
            self.invalid_rate_data
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['errors'].keys(), self.required_fields)

    def test_rate_detail_get(self):
        rate = Rate.objects.create(**self.valid_rate_creation_data)
        response = self.client.get(
            reverse('event-ratings-detail', kwargs={'event_pk': self.event.id, 'pk': rate.id})
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        serializer = RateSerializer(rate)
        self.assertEqual(response.data, serializer.data)

    def test_get_event_user_calification(self):
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=self.event
        )
        self.client.force_login(self.user)
        rate = Rate.objects.create(**self.valid_rate_creation_data)
        response = self.client.get(
            reverse('event-detail', kwargs={'pk': self.event.id}),
        )
        self.assertEqual(response.data.get('current_user_rating'), RateSerializer(rate).data)

    def test_get_event_user_calification_not_logged_in(self):
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=self.event
        )
        Rate.objects.create(**self.valid_rate_creation_data)
        response = self.client.get(
            reverse('event-detail', kwargs={'pk': self.event.id}),
        )
        self.assertEqual(response.data.get('current_user_rating'), None)

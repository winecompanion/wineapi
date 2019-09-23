from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from api.models import Event, Rate, Winery
from api.serializers import RateSerializer
from users.models import WineUser


class TestRatings(TestCase):
    def setUp(self):
        self.user = WineUser.objects.create_user(
            email='user@test.com',
            password='abcd',
            first_name='Test',
            last_name='User',
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
        self.required_fields = set(['rate', 'event', 'user'])
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
        rate_fields = ['rate', 'comment', 'event', 'user']
        self.assertEqual(set(serializer.data.keys()), set(rate_fields))

    def test_invalid_rate_serializer(self):
        serializer = RateSerializer(data=self.invalid_rate_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), self.required_fields)

    def test_rate_endpoint_get(self):
        response = self.client.get(
            reverse('rates-list')
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_rate_endpoint_create(self):
        response = self.client.post(
            reverse('rates-list'),
            self.valid_rate_json_data
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_rate_endpoint_create_with_invalid_data(self):
        response = self.client.post(
            reverse('rates-list'),
            self.invalid_rate_data
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['errors'].keys(), self.required_fields)

    def test_rate_detail_get(self):
        rate = Rate.objects.create(**self.valid_rate_creation_data)
        response = self.client.get(
            reverse('rates-detail', kwargs={'pk': rate.id})
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        serializer = RateSerializer(rate)
        self.assertEqual(response.data, serializer.data)

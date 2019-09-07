from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from api.models import Winery
from api.serializers import WinerySerializer


class TestWinery(TestCase):
    def setUp(self):
        self.valid_winery_data = {
                'name': 'Bodega1',
                'description': 'Hola',
                'website': 'hola.com',
        }
        self.invalid_winery_data = {
                'description': 'description',
        }
        self.required_fields = set(['name', 'website'])

    def test_winery_creation(self):
        winery = Winery(**self.valid_winery_data)
        winery.full_clean()
        winery.save()

    def test_invalid_winery_creation(self):
        winery = Winery(**self.invalid_winery_data)
        with self.assertRaises(Exception):
            winery.full_clean()

    def test_winery_serializer(self):
        winery = WinerySerializer(self.valid_winery_data)
        self.assertEqual(set(winery.data.keys()), set(['name', 'description', 'website', 'available_since']))

    def test_invalid_winery_serializer(self):
        serializer = WinerySerializer(data=self.invalid_winery_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), self.required_fields)

    def test_winery_endpoint_get(self):
        c = Client()
        response = c.get("/api/wineries/")
        result = response.status_code
        self.assertEqual(200, result)

    def test_winery_endpoint_create(self):
        c = Client()
        response = c.post(
            "/api/wineries/",
            self.valid_winery_data
        )
        result = response.status_code
        self.assertEqual(status.HTTP_201_CREATED, result)

    def test_winery_endpoint_create_with_invalid_data(self):
        c = Client()
        response = c.post(
            "/api/wineries/",
            self.invalid_winery_data
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['errors'].keys(), self.required_fields)

    def test_winery_detail_get(self):
        c = Client()
        winery = Winery.objects.create(**self.valid_winery_data)
        response = c.get(
            reverse('winery-detail', kwargs={'pk': winery.id})
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        serializer = WinerySerializer(winery)
        self.assertEqual(response.data, serializer.data)

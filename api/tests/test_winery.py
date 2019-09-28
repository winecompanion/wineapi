from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from rest_framework import status

from api import VARIETALS
from api.models import Winery, WineLine, Wine
from api.serializers import WinerySerializer, WineLineSerializer, WineSerializer


class TestWinery(TestCase):
    def setUp(self):
        self.valid_winery_data = {
                'name': 'Bodega1',
                'description': 'Hola',
                'website': 'hola.com',
                'location': 'POINT (106.84341430665 -6.1832427978516)',
        }
        self.invalid_winery_data = {
                'description': 'description',
        }
        self.required_fields = set(['name', ])
        self.client = Client()

    def test_winery_creation(self):
        winery = Winery(**self.valid_winery_data)
        winery.full_clean()
        winery.save()

    def test_invalid_winery_creation(self):
        winery = Winery(**self.invalid_winery_data)
        with self.assertRaises(Exception):
            winery.full_clean()

    def test_winery_serializer(self):
        serializer = WinerySerializer(data=self.valid_winery_data)
        self.assertTrue(serializer.is_valid())
        winery_fields = ['name', 'description', 'website', 'location', 'available_since']
        #print (serializer.errors)
        print (serializer.data)
        #self.assertEqual(set(serializer.data.keys()), set(winery_fields))

    def test_invalid_winery_serializer(self):
        serializer = WinerySerializer(data=self.invalid_winery_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), self.required_fields)

    def test_winery_endpoint_get(self):
        response = self.client.get(
            reverse('winery-list')
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_winery_endpoint_create_should_not_be_allowed(self):
        data = self.valid_winery_data
        response = self.client.post(
            reverse('winery-list'),
            data
        )
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)


class TestWines(TestCase):
    def setUp(self):
        self.winery = Winery.objects.create(
                name='Bodega1',
                description='Test Bodega',
                website='webpage.com',
        )
        self.wine_line = WineLine.objects.create(
            name='Example Wine Line',
            winery=self.winery
        )
        self.valid_wine_data = {
                'name': 'Example wine',
                'description': 'Amazing wine',
                'winery': self.winery.id,
                'varietal': '1',
                'wine_line': self.wine_line.id,
        }
        self.invalid_wine_data = {
                'description': 'description',
        }
        self.wine_creation_data = {
            'name': 'Example wine',
            'description': 'Amazing wine',
            'winery': self.winery,
            'varietal': '1',
            'wine_line': self.wine_line,
        }
        self.wine_required_fields = set(['name', 'winery', 'wine_line'])

    def test_wine_creation(self):
        wine = Wine(**self.wine_creation_data)
        wine.full_clean()
        wine.save()

    def test_invalid_wine_creation(self):
        wine = Wine(**self.invalid_wine_data)
        with self.assertRaises(ValidationError) as context:
            wine.full_clean()
        self.assertEqual(set(context.exception.error_dict), self.wine_required_fields)

    def test_wine_serializer(self):
        serializer = WineSerializer(data=self.valid_wine_data)
        self.assertTrue(serializer.is_valid())
        wine_fields = ['name', 'description', 'winery', 'varietal', 'wine_line']
        self.assertEqual(set(serializer.data.keys()), set(wine_fields))

    def test_invalid_wine_serializer(self):
        serializer = WineSerializer(data=self.invalid_wine_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), self.wine_required_fields)

    def test_invalid_wine_creation_serializer(self):
        """Test that when creating a wine the wine line is from the same winery"""
        data = self.valid_wine_data
        winery = Winery.objects.create(
                name='Other winery',
                description='Other',
        )
        wineline = WineLine.objects.create(
            name='From other winery',
            winery=winery,
        )
        data['wine_line'] = wineline.id
        serializer = WineSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            set(serializer.errors['non_field_errors']),
            set(['The wine line specified does not match the same winery'])
        )

    def test_wine_endpoint_get(self):
        response = self.client.get(
            reverse('wine-list')
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_wine_endpoint_create(self):
        response = self.client.post(
            reverse('wine-list'),
            self.valid_wine_data
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_wine_endpoint_create_with_invalid_data(self):
        response = self.client.post(
            reverse('wine-list'),
            self.invalid_wine_data
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['errors'].keys(), self.wine_required_fields)

    def test_wine_detail_get(self):
        wine = Wine.objects.create(**self.wine_creation_data)
        response = self.client.get(
            reverse('wine-detail', kwargs={'pk': wine.id})
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        serializer = WineSerializer(wine)
        self.assertEqual(response.data, serializer.data)

    def test_varietal_get(self):
        response = self.client.get(
            reverse('varietals')
        )
        expected = [{'id': k, 'value': v} for k, v in VARIETALS]
        self.assertEqual(response.data, expected)


class TestWineLines(TestCase):
    def setUp(self):
        self.winery = Winery.objects.create(
                name='Bodega1',
                description='Test Bodega',
                website='webpage.com',
        )
        self.wine_line_creation_data = {
                'name': 'Wine Line',
                'description': 'Testing wine line',
                'winery': self.winery,
        }
        self.valid_wineline_data = {
                'name': 'Wine Line',
                'description': 'Testing wine line',
                'winery': self.winery.id,
        }
        self.invalid_wineline_data = {
                'description': 'description',
        }
        self.wineline_required_fields = set(['name', 'winery'])
        self.client = Client()

    def test_wineline_creation(self):
        wineline = WineLine(**self.wine_line_creation_data)
        wineline.full_clean()
        wineline.save()

    def test_invalid_wineline_creation(self):
        wineline = WineLine(**self.invalid_wineline_data)
        with self.assertRaises(ValidationError) as context:
            wineline.full_clean()
        self.assertEqual(set(context.exception.error_dict), self.wineline_required_fields)

    def test_wineline_serializer(self):
        serializer = WineLineSerializer(data=self.valid_wineline_data)
        self.assertTrue(serializer.is_valid())
        wine_line_fields = ['name', 'description', 'winery']
        self.assertEqual(set(serializer.data.keys()), set(wine_line_fields))

    def test_invalid_wineline_serializer(self):
        serializer = WineLineSerializer(data=self.invalid_wineline_data)  # dezerialize
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), self.wineline_required_fields)

    def test_wineline_endpoint_get(self):
        response = self.client.get(
            reverse('wine-line-list'),
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_wineline_endpoint_create(self):
        response = self.client.post(
            reverse('wine-line-list'),
            self.valid_wineline_data
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_wineline_endpoint_create_with_invalid_data(self):
        response = self.client.post(
            reverse('wine-line-list'),
            self.invalid_wineline_data
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['errors'].keys(), self.wineline_required_fields)

    def test_wineline_detail_get(self):
        wine_line = WineLine.objects.create(**self.wine_line_creation_data)
        response = self.client.get(
            reverse('wine-line-detail', kwargs={'pk': wine_line.id})
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        serializer = WineLineSerializer(wine_line)
        self.assertEqual(response.data, serializer.data)

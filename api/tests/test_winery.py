from django.test import TestCase
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
        self.assertEqual(set(serializer.errors), set(['name', 'website']))
 
 

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.base import ContentFile
from rest_framework import status

from api.models import Winery, ImagesWinery
from api.serializers import FileSerializer, ImageUrlField 

from users.models import WineUser


class TestImagesWinary(TestCase):
    
    def setUp(self):
        self.winery = Winery.objects.create(
                name='My Winery',
                description='Test Winery',
                website='website.com'
        )
        
        file_test = ContentFile(b"Some file content")
        file_test.name = 'myfile.xml'
        self.valid_file =  file_test

        self.valid_images_upload_data = {
                'id': 1,
                'filefield': [self.valid_file],
                'winery': self.winery
                }

        self.invalid_images_upload_data = {
                'id': 1,
                'filefield': self.valid_file,
                'winery': self.winery
                }


    def test_file_serializer(self):
        serializer = FileSerializer(data=self.valid_images_upload_data)
        self.assertTrue(serializer.is_valid())
        #reservation_fields = ['attendee_number', 'observations', 'paid_amount', 'user', 'event_occurrence']
        #self.assertEqual(set(serializer.data.keys()), set(reservation_fields))

    def test_invalid_file_serializer(self):
        serializer = FileSerializer(data=self.invalid_images_upload_data)
        self.assertFalse(serializer.is_valid())
        #reservation_fields = ['attendee_number', 'observations', 'paid_amount', 'user', 'event_occurrence']
        #self.assertEqual(set(serializer.data.keys()), set(reservation_fields))

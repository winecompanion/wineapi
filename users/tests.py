from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from rest_framework import status

from api.models import Country
from . import TOURIST, WINERY, GENDER_OTHER, LANGUAGE_ENGLISH
from .models import WineUser, UserSerializer


class TestUser(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='Argentina')
        self.valid_user_creation_data = {
            'email': 'example@winecompanion.com',
            'password': 'testuserpass',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'gender': GENDER_OTHER,
            'language': LANGUAGE_ENGLISH,
            'phone': '2616489178',
            'country': self.country
        }
        self.valid_user_post_data = {
            'email': 'example@winecompanion.com',
            'password': 'testuserpass',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'gender': GENDER_OTHER,
            'language': LANGUAGE_ENGLISH,
            'phone': '2616489178',
            'country': self.country.id
        }
        self.valid_winery_data = {
            'name': 'Test winery name',
            'description': 'Test winery description',
            'website': 'test.com',
            'location': 'POINT(-32.8974226 -68.8704887)'
        }
        self.invalid_user_data = {
            'email': '',
        }
        self.users_required_fields = set([
            'email',
            'password',
            'first_name',
            'last_name',
            'gender',
            'language',
            'country',
            'phone',
            ])
        self.serializer_fields = set([
            'email',
            'first_name',
            'last_name',
            'birth_date',
            'gender',
            'language',
            'country',
            'phone',
            ])

    def test_user_creation(self):
        """Test valid attributes"""
        user = WineUser(**self.valid_user_creation_data)
        user.full_clean()
        user.save()

    def test_invalid_user_creation(self):
        """Test required fields"""
        user = WineUser(**self.invalid_user_data)
        with self.assertRaises(ValidationError) as cm:
            user.full_clean()
        self.assertEqual(
            set(cm.exception.error_dict.keys()),
            self.users_required_fields
        )

    def test_user_serializer(self):
        """Test serializer fields"""
        serializer = UserSerializer(data=self.valid_user_post_data)
        serializer.is_valid()
        # In this case, we don't want the serializer to return the password since it's read only.
        self.assertEqual(set(serializer.data.keys()), self.serializer_fields)

    def test_invalid_user_serializer(self):
        """Test required fields"""
        serializer = UserSerializer(data=self.invalid_user_data)
        self.assertFalse(serializer.is_valid())
        # The password is read only, but required
        self.assertEqual(set(serializer.errors), self.users_required_fields)

    def test_users_endpoint_get(self):
        response = self.client.get(
            reverse('users-list'),
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_users_endpoint_create(self):
        response = self.client.post(
            reverse('users-list'),
            self.valid_user_post_data
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_users_endpoint_create_with_invalid_data(self):
        response = self.client.post(
            reverse('users-list'),
            self.invalid_user_data
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['errors'].keys(), self.users_required_fields)

    def test_users_detail_get(self):
        user = WineUser.objects.create(**self.valid_user_creation_data)
        response = self.client.get(
            reverse('users-detail', kwargs={'pk': user.id})
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        serializer = UserSerializer(user)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(user.user_type, TOURIST)

    def test_create_user_with_winery_endpoint(self):
        data = self.valid_user_post_data
        data['winery'] = self.valid_winery_data
        response = self.client.post(
            reverse('users-list'),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        db_user = WineUser.objects.first()
        self.assertEqual(db_user.winery.name, data['winery']['name'])
        self.assertEqual(db_user.user_type, WINERY)

    def test_user_login(self):
        user = WineUser.objects.create_user(**self.valid_user_creation_data)
        res = self.client.post(
            reverse('token_obtain_pair'),
            {'email': user.email, 'password': self.valid_user_post_data['password']},
        )
        self.assertEqual(set(['access', 'refresh']), set(res.data.keys()))

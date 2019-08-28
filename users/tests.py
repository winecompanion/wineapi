from django.test import TestCase
from .models import WineUser, UserSerializer
from django.core.exceptions import ValidationError


class TestUser(TestCase):
    def setUp(self):
        self.valid_user_data = {
                'email': 'example@winecompanion.com',
                'password': '1234',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                }
        self.invalid_user_data = {
                'email': '',
                }

    def test_user_creation(self):
        """Test valid attributes"""
        user = WineUser(**self.valid_user_data)
        user.full_clean()
        user.save()

    def test_invalid_user_creation(self):
        """Test required fields"""
        user = WineUser(**self.invalid_user_data)
        with self.assertRaises(ValidationError) as cm:
            user.full_clean()
        self.assertEqual(
            set(cm.exception.error_dict.keys()),
            set(['email', 'password', 'first_name', 'last_name'])
        )

    def test_user_serializer(self):
        """Test serializer fields"""
        user = UserSerializer(self.valid_user_data)
        self.assertEqual(set(user.data.keys()), set(['email', 'first_name', 'last_name', 'birth_date']))

    def test_invalid_user_serializer(self):
        """Test required fields"""
        serializer = UserSerializer(data=self.invalid_user_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), set(['email', 'password', 'first_name', 'last_name']))

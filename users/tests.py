from django.test import TestCase
from .models import WineUser
from django.core.exceptions import ValidationError


class TestUser(TestCase):
    def setUp(self):
        self.valid_user_data = {
                'email': 'example@winecompanion.com',
                'password': '1234',
                'name': 'First Name',
                }
        self.invalid_user_data = {
                'email': '',
                }

    def test_user_creation(self):
        user = WineUser(**self.valid_user_data)
        user.full_clean()
        user.save()

    def test_invalid_user_creation(self):
        user = WineUser(**self.invalid_user_data)
        with self.assertRaises(ValidationError) as cm:
            user.full_clean()
        self.assertEqual(
            set(cm.exception.error_dict.keys()),
            set(['email', 'password', 'name'])
        )

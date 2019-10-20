from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from rest_framework import serializers
from django.utils import timezone
from django.db import models

from api.models import Winery, Country
from api.serializers import WinerySerializer

from . import ADMIN, GENDERS, LANGUAGES, TOURIST, WINERY


USER_TYPE_CHOICES = [
    (TOURIST, 'TOURIST'),
    (WINERY, 'WINERY'),
    (ADMIN, 'ADMIN')
]


class WineUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not getattr(extra_fields, 'country', None):
            extra_fields['country'] = Country.objects.all().first()

        extra_fields['user_type'] = ADMIN

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class WineUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField('email address', unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # Custom fields
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    user_type = models.CharField(max_length=20, blank=True, choices=USER_TYPE_CHOICES, default=TOURIST)

    winery = models.ForeignKey('api.winery', null=True, blank=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    gender = models.IntegerField(choices=GENDERS)
    language = models.IntegerField(choices=LANGUAGES)
    phone = models.CharField(max_length=15)

    objects = WineUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'country', 'language', 'gender', 'phone']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)


class UserSerializer(serializers.ModelSerializer):
    """Serializes a user for the api endpoint"""
    id = serializers.ReadOnlyField()
    winery = WinerySerializer(required=False)

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'birth_date',
            'gender',
            'country',
            'language',
            'phone',
            'winery',
            'user_type',
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
        }

    def create(self, validated_data):
        """Create and return a new user"""
        winery_data = validated_data.pop('winery', None)
        user = WineUser.objects.create_user(**validated_data)
        if winery_data:
            winery = Winery.objects.create(**winery_data)
            user.winery = winery
            user.user_type = WINERY
        user.save()
        return user

    def to_representation(self, obj):
        self.fields['gender'] = serializers.CharField(source='get_gender_display')
        self.fields['language'] = serializers.CharField(source='get_language_display')
        self.fields['country'] = serializers.CharField(source='country.name')
        return super().to_representation(obj)

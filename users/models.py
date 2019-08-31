from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from rest_framework import serializers
from django.utils import timezone
from django.db import models
from api.models import Winery


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

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class WineUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # Custom fields
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    winery = models.ForeignKey(Winery, null=True, blank=True, on_delete=models.PROTECT)

    objects = WineUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class UserSerializer(serializers.ModelSerializer):
    """Serializes a user for the api endpoint"""
    class Meta:
        model = WineUser
        fields = ('email', 'password', 'first_name', 'last_name', 'birth_date')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """Create and return a new user"""
        user = WineUser.objects.create_user(**validated_data)
        return user

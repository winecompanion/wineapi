from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import WineUser

admin.site.register(WineUser)
admin.site.register(Permission)

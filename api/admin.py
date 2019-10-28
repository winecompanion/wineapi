from django.contrib import admin

from api.models import (
    Country,
    EventCategory,
    Tag,
)

admin.site.register(Country)
admin.site.register(EventCategory)
admin.site.register(Tag)

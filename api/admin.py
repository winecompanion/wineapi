from django.contrib import admin

from api.models import (
    Country,
    EventCategory,
    Tag,
    Language,
    Gender,
    Varietal,
)

admin.site.register(Country)
admin.site.register(Language)
admin.site.register(Gender)
admin.site.register(Varietal)
admin.site.register(EventCategory)
admin.site.register(Tag)

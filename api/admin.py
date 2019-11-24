from django.contrib import admin

from api.models import (
    Country,
    Event,
    EventOccurrence,
    EventCategory,
    Tag,
    Language,
    Gender,
    Rate,
    Reservation,
    Varietal,
    Wine,
    WineLine,
    Winery,
)


class WineryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class EventAdmin(admin.ModelAdmin):
    search_fields = ('name', 'winery__name')


class EventOccurrenceAdmin(admin.ModelAdmin):
    search_fields = ('event__name', 'start')


class ReservationAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'event_occurrence__event__name', 'user__last_name', 'user__first_name')


class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class RateAdmin(admin.ModelAdmin):
    search_fields = ('created', 'user__email', 'user__last_name', 'user__first_name')


admin.site.register(Country, CountryAdmin)
admin.site.register(Language)
admin.site.register(Gender)
admin.site.register(Varietal)
admin.site.register(EventCategory)
admin.site.register(Tag)
admin.site.register(Winery, WineryAdmin)
admin.site.register(WineLine)
admin.site.register(Wine)
admin.site.register(Event, EventAdmin)
admin.site.register(EventOccurrence, EventOccurrenceAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(Reservation, ReservationAdmin)

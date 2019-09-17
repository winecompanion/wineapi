import datetime
from decimal import Decimal
from django.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.gis import geos
from django.contrib.gis.measure import Distance
from django.core.validators import MinValueValidator


from . import VARIETALS
from users.models import WineUser


class Tag(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Winery(models.Model):
    """Model for winery"""

    name = models.CharField(max_length=30)
    description = models.TextField()
    website = models.CharField(max_length=40)
    available_since = models.DateTimeField(null=True, blank=True)
    location = PointField(u"longitude/latitude", geography=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Winery'
        verbose_name_plural = 'Wineries'

    def __str__(self):
        return self.name

    @staticmethod
    def get_nearly_wineries(location):
        current_point = geos.fromstr(location)
        distance_from_point = {'km': 10}
        wineries = Winery.objects.filter(location__distance_lt=(current_point, Distance(**distance_from_point)))
        return wineries


class WineLine(models.Model):
    """Model for winery wine lines"""
    name = models.CharField(max_length=20)
    description = models.TextField()
    winery = models.ForeignKey(Winery, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Wine-line'
        verbose_name_plural = 'Wine-lines'

    def __str__(self):
        return self.name


class Wine(models.Model):
    """Model for winery wines"""
    name = models.CharField(max_length=20)
    description = models.TextField()
    winery = models.ForeignKey(Winery, on_delete=models.CASCADE)
    # to discuss: choices vs foreign key
    varietal = models.CharField(
        max_length=20,
        choices=VARIETALS,
        default='4',
    )
    wine_line = models.ForeignKey(WineLine, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class EventCategory(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Event(models.Model):
    """"Model for Events"""

    name = models.CharField(max_length=80)
    description = models.TextField()
    cancelled = models.DateTimeField(null=True, blank=True)
    winery = models.ForeignKey(Winery, on_delete=models.PROTECT)
    categories = models.ManyToManyField(EventCategory)
    tags = models.ManyToManyField(Tag, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    @staticmethod
    def calculate_dates_in_threshold(start, end, weekdays):
        """Returns a list of dates for certain weekdays
        between start and end."""
        if not end:
            return [start]
        dates = []
        days_between = (end - start).days + 1
        for i in range(days_between):
            day = start + datetime.timedelta(days=i)
            if day.weekday() in weekdays:
                dates.append(day)
        return dates


class EventOccurrence(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    vacancies = models.IntegerField()
    event = models.ForeignKey(
        Event,
        related_name='occurrences',
        on_delete=models.CASCADE
    )


class Reservation(models.Model):
    attendee_number = models.PositiveIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    observations = models.TextField()
    paid_ammount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    user = models.ForeignKey(WineUser, on_delete=models.PROTECT)
    event_occurrence = models.ForeignKey(EventOccurrence, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.id) + ": " + self.user.name + ", " + str(self.ammount_payed)

from datetime import date, datetime, timedelta
from decimal import Decimal
from django.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.gis import geos
from django.contrib.gis.measure import Distance
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.mail import send_mail

from . import RESERVATION_STATUS, RESERVATION_CANCELLED, RESERVATION_CONFIRMED, VARIETALS


class Mail():
    def send_mail(subject, message, mailfrom, mailto):
        send_mail(subject, message, mailfrom, mailto, fail_silently=False)


class Country(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Winery(models.Model):
    """Model for winery"""

    name = models.CharField(max_length=30)
    description = models.TextField()
    website = models.CharField(max_length=40, blank=True)
    available_since = models.DateTimeField(null=True, blank=True)
    location = PointField(u"longitude/latitude", geography=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Winery'
        verbose_name_plural = 'Wineries'

    def __str__(self):
        return self.name

    @staticmethod
    def get_nearly_wineries(location, ratio):
        current_point = geos.fromstr(location)
        distance_from_point = {'km': ratio}
        distance = Distance(**distance_from_point)
        wineries = Winery.objects.filter(location__distance_lt=(current_point, distance), location__isnull=False)
        return wineries


class WineLine(models.Model):
    """Model for winery wine lines"""
    name = models.CharField(max_length=20)
    description = models.TextField()
    winery = models.ForeignKey(
        Winery,
        related_name='wine_lines',
        on_delete=models.CASCADE,
    )

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
    wine_line = models.ForeignKey(
        WineLine,
        related_name='wines',
        on_delete=models.CASCADE,
    )

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
            day = start + timedelta(days=i)
            if day.weekday() in weekdays:
                dates.append(day)
        return dates

    def cancel(self):
        self.cancelled = datetime.now()
        occurrences = self.occurrences.filter(start__gt=date.today())
        for occurrence in occurrences:
            reservations = occurrence.reservation_set.all()
            for reservation in reservations:
                reservation.cancel()
        self.save()
        success_message = 'The event has been cancelled'
        return success_message

    def __str__(self):
        return self.name


class EventOccurrence(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    vacancies = models.PositiveIntegerField()
    event = models.ForeignKey(
        Event,
        related_name='occurrences',
        on_delete=models.CASCADE
    )


class Rate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    event = models.ForeignKey(
        Event,
        related_name='rating',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey('users.wineuser', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('event', 'user'), )

    @property
    def user_name(self):
        return self.user.full_name


class Reservation(models.Model):
    attendee_number = models.PositiveIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    observations = models.TextField(blank=True)
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    user = models.ForeignKey('users.wineuser', on_delete=models.PROTECT)
    event_occurrence = models.ForeignKey(EventOccurrence, on_delete=models.PROTECT)
    status = models.IntegerField(
        choices=RESERVATION_STATUS,
        default=RESERVATION_CONFIRMED,
    )

    def __str__(self):
        return '{}: {}, {}'.format(str(self.id), self.user.first_name, str(self.paid_amount))

    def cancel(self):
        self.status = RESERVATION_CANCELLED
        self.save()
        info = 'Your reservation in {} with number {} for the day {} has been cancelled'
        mailfrom = 'winecompanion19@gmail.com',
        subject = 'Winecompanion'
        body = info.format(self.event_occurrence.event.winery.name, self.id, self.event_occurrence.start)
        Mail.send_mail(subject, body, mailfrom, [self.user.email])
        success_message = 'The reservation has been cancelled'
        return success_message


class ImagesWinery(models.Model):
    filefield = models.FileField(blank=False, null=False)
    winery = models.ForeignKey(
        Winery,
        related_name='images',
        on_delete=models.CASCADE
    )


class ImagesEvent(models.Model):
    filefield = models.FileField(blank=False, null=False)
    event = models.ForeignKey(
        Event,
        related_name='images',
        on_delete=models.CASCADE
    )

import datetime
from django.db import models


class Winery(models.Model):
    """Model for winery"""

    name = models.CharField(max_length=30)
    description = models.TextField()
    website = models.CharField(max_length=40)
    available_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    """"Model for Events"""

    name = models.CharField(max_length=80)
    description = models.TextField()
    cancelled = models.DateTimeField(null=True, blank=True)
    winery = models.ForeignKey(Winery, on_delete=models.PROTECT)

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
        on_delete=models.CASCADE)

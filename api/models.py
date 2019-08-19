import datetime
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=80)
    description = models.TextField()


class EventOccurrence(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    vacancies = models.IntegerField()
    event = models.ForeignKey('Event', on_delete=models.CASCADE)

    @staticmethod
    def calculate_dates_in_threshold(start, end, weekdays):
        """Returns a list of dates for certain weekdays between start and end."""
        dates = []
        days_between = (end - start).days
        for i in range(days_between):
            day = start + datetime.timedelta(days=i)
            if day.weekday() in weekdays:
                dates.append(day)
        return dates

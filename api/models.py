import datetime
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=80)
    description = models.TextField()

    @staticmethod
    def calculate_dates_in_threshold(start, end, weekdays):
        """Returns a list of dates for certain weekdays
        between start and end."""
        dates = []
        days_between = (end - start).days
        for i in range(days_between):
            day = start + datetime.timedelta(days=i)
            if day.weekday() in weekdays:
                dates.append(day)
            return dates

    @classmethod
    def create_with_schedules(cls, data):
        # TODO: finish docstring
        """Creates and saves an Event associated to
        instances of EventOcurrence.

        Params:
        """
        schedule = data.pop('schedule')
        event = cls.objects.create(**data)

        for elem in schedule:
            start_time = elem['start_time']
            end_time = elem['end_time']
            dates = cls.calculate_dates_in_threshold(
                    elem['from_date'],
                    elem['to_date'],
                    elem['weekdays'])

            for date in dates:
                start = datetime.datetime(
                    date.year,
                    date.month,
                    date.day,
                    start_time.hour,
                    start_time.minute,
                )
                end = datetime.datetime(
                    date.year,
                    date.month,
                    date.day,
                    end_time.hour,
                    end_time.minute,
                )

                # TODO: don't hardcode vacancies
                EventOccurrence.objects.create(
                    start=start,
                    end=end,
                    vacancies=50,
                    event=event
                )

        return event


class EventOccurrence(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    vacancies = models.IntegerField()
    event = models.ForeignKey(
        Event, 
        related_name='ocurrences', 
        on_delete=models.CASCADE)


class Winery(models.Model):
    """Model for winery"""

    name = models.CharField(max_length=30)
    description = models.TextField()
    website = models.CharField(max_length=40)
    available_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

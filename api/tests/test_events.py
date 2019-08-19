import datetime
from django.test import TestCase
from api.models import EventOccurrence


class TestEvents(TestCase):
    def test_dates_between_threshold(self):
        MONDAY, WEDNESDAY, FRIDAY = 0, 2, 4
        start = datetime.date(2019, 8, 18)
        end = datetime.date(2019, 8, 31)
        weekdays = [MONDAY, WEDNESDAY, FRIDAY]
        expected = [
            datetime.date(2019, 8, 19),
            datetime.date(2019, 8, 21),
            datetime.date(2019, 8, 23),
            datetime.date(2019, 8, 26),
            datetime.date(2019, 8, 28),
            datetime.date(2019, 8, 30),
        ]
        result = EventOccurrence.calculate_dates_in_threshold(
                start, end, weekdays)

        self.assertEqual(expected, result)


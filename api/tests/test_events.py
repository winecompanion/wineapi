import datetime
from django.test import Client
from django.test import TestCase
from api.models import Event

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
        result = Event.calculate_dates_in_threshold(
                start, end, weekdays)

        self.assertEqual(expected, result)

    def test_event_endpoint_get(self):    
        c = Client()
        response = c.get('/api/events/')
        result = response.status_code
        self.assertEqual(200, result)

    def test_event_endpoint_post(self):
        c = Client()
        response = c.post('/api/events/', {'name': 'exampleName', 'description': 'exampleDescription'})
        response = c.get('/api/events/')
        self.assertEqual(response.json(), [{'name': 'exampleName', 'description': 'exampleDescription'}])  

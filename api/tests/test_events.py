import datetime
from parameterized import parameterized
from django.test import Client, TestCase
from django.urls import reverse
from api.models import Event, EventOccurrence, Winery
from api.serializers import EventSerializer


MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = list(range(7))


class TestEvents(TestCase):
    def setUp(self):
        self.winery = Winery.objects.create(
                name='Bodega1',
                description='Hola',
                website='hola.com',
        )
        self.valid_data = {
            "one_schedule_no_to_date": {
                "name": "TEST_EVENT_NAME",
                "description": "TEST_EVENT_DESCRIPTION",
                "vacancies": 50,
                "winery": self.winery.id,
                "schedule": [
                    {
                        "from_date": "2019-08-28",
                        "to_date": None,
                        "start_time": "15:30:00",
                        "end_time": "16:30:00",
                        "weekdays": None,
                    }
                ],
            },
            "one_schedule_with_weekdays": {
                "name": "TEST_EVENT_NAME",
                "description": "TEST_EVENT_DESCRIPTION",
                "vacancies": 50,
                "winery": self.winery.id,
                "schedule": [
                    {
                        "from_date": "2019-08-28",
                        "to_date": "2019-09-11",
                        "start_time": "15:30:00",
                        "end_time": "16:30:00",
                        "weekdays": [TUESDAY, WEDNESDAY, THURSDAY],
                    }
                ],
            },
            "multiple_schedules_with_weekdays": {
                "name": "TEST_EVENT_NAME",
                "description": "TEST_EVENT_DESCRIPTION",
                "vacancies": 50,
                "winery": self.winery.id,
                "schedule": [
                    {
                        "from_date": "2019-08-28",
                        "to_date": "2019-09-11",
                        "start_time": "8:30:00",
                        "end_time": "10:30:00",
                        "weekdays": [TUESDAY, THURSDAY, SATURDAY],
                    },
                    {
                        "from_date": "2019-08-28",
                        "to_date": "2019-09-11",
                        "start_time": "15:30:00",
                        "end_time": "16:30:00",
                        "weekdays": [TUESDAY, THURSDAY, SATURDAY],
                    },
                ],
            },
        }

        self.client = Client()

    def test_dates_between_threshold(self):
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
        result = Event.calculate_dates_in_threshold(start, end, weekdays)
        self.assertEqual(result, expected)

    @parameterized.expand([
       ('one_schedule_no_to_date', 1),
       ('one_schedule_with_weekdays', 7),
       ('multiple_schedules_with_weekdays', 12),
    ])
    def test_event_creation_endpoint_with_different_schedules(self, data_key, expected_occurrences_count):
        data = self.valid_data[data_key]
        serializer = EventSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        response = self.client.post(
            reverse("event-list"), data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.json().keys()), set(["url"]))

        db_event = Event.objects.first()
        self.assertEqual(db_event.name, data["name"])
        self.assertEqual(expected_occurrences_count, len(db_event.occurrences.all()))

    def test_invalid_event_creation(self):
        data = {}
        response = self.client.post(reverse('event-list'), data=data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            set(response.data['errors'].keys()),
            set(['name', 'description', 'winery', 'schedule', 'vacancies'])
        )

    def test_event_endpoint_get(self):
        c = Client()
        response = c.get("/api/events/")
        result = response.status_code
        self.assertEqual(200, result)

    def test_filter_event_by_date(self):
        """Test returning events with future occurrencies"""
        event1 = Event.objects.create(name='Evento 1', description='Desc 1', winery=self.winery)
        event2 = Event.objects.create(name='Evento 2', description='Desc 2', winery=self.winery)
        EventOccurrence.objects.create(
            start='2036-10-31T20:00:00',
            end='2036-10-31T23:00:00',
            vacancies=50,
            event=event1
        )
        EventOccurrence.objects.create(
            start='2019-05-31T20:00:00',
            end='2019-05-31T23:00:00',
            vacancies=50,
            event=event2
        )
        res = self.client.get(
            reverse("event-list")
        )
        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_search_event_by_name(self):
        """Test returning events that match a name"""
        event1 = Event.objects.create(name='Event buscado', description='Desc 1', winery=self.winery)
        event2 = Event.objects.create(name='Evento 2', description='Desc 2', winery=self.winery)
        EventOccurrence.objects.create(
            start='2036-10-31T20:00:00',
            end='2036-10-31T23:00:00',
            vacancies=50,
            event=event1
        )
        EventOccurrence.objects.create(
            start='2036-05-31T20:00:00',
            end='2036-05-31T23:00:00',
            vacancies=50,
            event=event2
        )
        res = self.client.get(
            reverse("event-list"),
            {'search': 'buscado'}
        )

        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_events_until_date(self):
        """Test returning events with a date no superior than the specified"""

        event1 = Event.objects.create(name='Event buscado', description='Desc 1', winery=self.winery)
        event2 = Event.objects.create(name='Evento 2', description='Desc 2', winery=self.winery)
        EventOccurrence.objects.create(
            start='2036-10-31T20:00:00',
            end='2036-10-31T23:00:00',
            vacancies=50,
            event=event1
        )
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=event2
        )
        res = self.client.get(
            reverse("event-list"),
            {'to_date': '2031-05-31'}
        )
        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)
        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

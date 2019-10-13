from datetime import date, datetime

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from parameterized import parameterized

from users.models import WineUser
from api.models import Event, EventCategory, EventOccurrence, Tag, Winery
from api.serializers import EventSerializer, EventOccurrenceSerializer


MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = list(range(7))


class TestEvents(TestCase):
    def setUp(self):
        self.winery = Winery.objects.create(
                name='Bodega1',
                description='Hola',
                website='hola.com',
        )
        self.winery_user = WineUser.objects.create(
            email='testuser@winecompanion.com',
            winery=self.winery,
        )
        self.category1 = EventCategory.objects.create(name="Tour")
        self.category2 = EventCategory.objects.create(name="Food")
        self.category3 = EventCategory.objects.create(name="Wine tasting")
        self.category_restaurant = EventCategory.objects.create(name="Restaurant")
        self.valid_data = {
            "one_schedule_no_to_date": {
                "name": "TEST_EVENT_NAME",
                "description": "TEST_EVENT_DESCRIPTION",
                "vacancies": 50,
                "price": 500.0,
                "categories": [
                    {
                        "name": self.category1.name
                    },
                ],
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
                "price": 500.0,
                "categories": [
                    {
                        "name": self.category1.name
                    },
                ],
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
                "price": 0.0,
                "categories": [
                    {
                        "name": self.category1.name
                    },
                    {
                        "name": self.category2.name
                    },
                    {
                        "name": self.category3.name
                    },
                ],
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

        self.invalid_data = {
            "empty_schedule": {
                "name": "TEST_EVENT_NAME",
                "description": "TEST_EVENT_DESCRIPTION",
                "vacancies": 50,
                "schedule": [],
            },
        }

        self.event_required_fields = ['name', 'description', 'price', 'categories', 'schedule', 'vacancies']
        self.client = Client()
        self.client.force_login(self.winery_user)

    def test_dates_between_threshold(self):
        start = date(2019, 8, 18)
        end = date(2019, 8, 31)
        weekdays = [MONDAY, WEDNESDAY, FRIDAY]
        expected = [
            date(2019, 8, 19),
            date(2019, 8, 21),
            date(2019, 8, 23),
            date(2019, 8, 26),
            date(2019, 8, 28),
            date(2019, 8, 30),
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.json().keys()), set(["url"]))

        db_event = Event.objects.first()
        self.assertEqual(db_event.name, data["name"])
        self.assertEqual(expected_occurrences_count, len(db_event.occurrences.all()))

    def test_invalid_event_creation(self):
        data = {}
        response = self.client.post(reverse('event-list'), data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            set(response.data['errors'].keys()),
            set(self.event_required_fields)
        )

    def test_event_endpoint_get(self):
        c = Client()
        response = c.get("/api/events/")
        result = response.status_code
        self.assertEqual(200, result)

    def test_filter_event_by_date(self):
        """Test returning events with future occurrencies"""
        event1 = Event.objects.create(name='Evento 1', description='Desc 1', winery=self.winery, price=0.0)
        event2 = Event.objects.create(name='Evento 2', description='Desc 2', winery=self.winery, price=0.0)
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
        event1 = Event.objects.create(name='Event buscado', description='Desc 1', winery=self.winery, price=0.0)
        event2 = Event.objects.create(name='Evento 2', description='Desc 2', winery=self.winery, price=0.0)
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

    def test_filter_events_before_date(self):
        """Test returning events with a date no superior than the specified"""

        event1 = Event.objects.create(name='Event buscado', description='Desc 1', winery=self.winery, price=0.0)
        event2 = Event.objects.create(name='Evento 2', description='Desc 2', winery=self.winery, price=0.0)
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
            {'start_before': '2031-05-31'}
        )
        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)
        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    def test_filter_events_in_date_range(self):
        """Test returning events with a date no superior than the specified"""

        event1 = Event.objects.create(name='First Event', description='Desc 1', winery=self.winery, price=0.0)
        event2 = Event.objects.create(name='Second Event', description='Desc 2', winery=self.winery, price=0.0)
        event3 = Event.objects.create(name='Third Event', description='Desc 3', winery=self.winery, price=0.0)
        EventOccurrence.objects.create(
            start='2034-10-31T20:00:00',
            end='2034-10-31T23:00:00',
            vacancies=50,
            event=event1
        )
        EventOccurrence.objects.create(
            start='2035-05-31T20:00:00',
            end='2035-05-31T23:00:00',
            vacancies=50,
            event=event2
        )
        EventOccurrence.objects.create(
            start='2036-05-31T20:00:00',
            end='2036-05-31T23:00:00',
            vacancies=50,
            event=event3
        )
        res = self.client.get(
            reverse("event-list"),
            {'start_after': '2034-12-15', 'start_before': '2036-01-15'}
        )
        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)
        serializer3 = EventSerializer(event3)
        # Test that only the event between the dates is in the response
        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_events_categories(self):
        """Test returning events with category specified"""

        event1 = Event.objects.create(
            name='Event buscado',
            description='Desc 1',
            winery=self.winery,
            price=0.0
        )
        event2 = Event.objects.create(
            name='Evento 2',
            description='Desc 2',
            winery=self.winery,
            price=0.0
        )
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
        event1.categories.add(self.category1)
        res = self.client.get(
            reverse("event-list"),
            {'category': 'Tour'}  # Exact match
        )
        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_events_multiple_categories(self):
        """Test returning events with category specified"""

        event1 = Event.objects.create(
            name='Wanted Event',
            description='Should be shown',
            winery=self.winery,
            price=0.0
        )
        event2 = Event.objects.create(
            name='Also Wanted',
            description='Should be shown',
            winery=self.winery,
            price=0.0
        )
        event3 = Event.objects.create(
            name='Unwanted',
            description='Shouldnt be shown',
            winery=self.winery,
            price=0.0
        )
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
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=event3
        )
        # Wanted Event categories
        event1.categories.add(self.category1)
        event1.categories.add(self.category3)
        event2.categories.add(self.category2)
        # Unwanted Event categories
        event3.categories.add(self.category3)

        res = self.client.get(
            '/api/events/?category=Tour&category=Food'  # looks for events with any of this categories
        )
        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)
        serializer3 = EventSerializer(event3)
        # Check that wanted events are in the response
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        # Check that unwanted event is not in response data
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_events_multiple_tags(self):
        """Test returning events with tags specified"""

        event1 = Event.objects.create(
            name='Wanted Event',
            description='Should be shown',
            winery=self.winery,
            price=0.0
        )
        event2 = Event.objects.create(
            name='Also Wanted',
            description='Should be shown',
            winery=self.winery,
            price=0.0
        )
        event3 = Event.objects.create(
            name='Unwanted',
            description='Shouldnt be shown',
            winery=self.winery,
            price=0.0
        )
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
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=event3
        )
        # Wanted Event tags
        event1.tags.add(Tag.objects.create(name='tag1'))
        event1.tags.add(Tag.objects.create(name='tag3'))
        event2.tags.add(Tag.objects.create(name='tag2'))
        # Unwanted Event tag)
        event3.tags.add(Tag.objects.create(name='tag3'))

        res = self.client.get(
            '/api/events/?tag=tag1&tag=tag2'  # looks for events with any of this tags
        )
        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)
        serializer3 = EventSerializer(event3)
        # Check that wanted events are in the response
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        # Check that unwanted event is not in response data
        self.assertNotIn(serializer3.data, res.data)

    def test_invalid_schedule(self):
        data = self.invalid_data['empty_schedule']
        serializer = EventSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        response = self.client.post(
            reverse("event-list"), data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_creation_with_tags(self):
        data = self.valid_data['one_schedule_no_to_date']
        tag1 = Tag.objects.create(name='test tag')
        tag2 = Tag.objects.create(name='other tag')
        data['tags'] = [
            {
                "name": tag1.name
            },
            {
                "name": tag2.name
            }
        ]
        serializer = EventSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        response = self.client.post(
            reverse("event-list"), data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.json().keys()), set(["url"]))

        db_event = Event.objects.first()
        self.assertEqual(db_event.name, data["name"])
        tag_list = [tag.name for tag in db_event.tags.all()]
        self.assertEqual(set(tag_list), set(['test tag', 'other tag']))

    def test_event_creation_with_invalid_tag(self):
        data = self.valid_data['one_schedule_no_to_date']
        tag1 = Tag.objects.create(name='test tag')
        data['tags'] = [
            {
                "name": tag1.name
            },
            {
                "name": "bad_tag_name"
            }
        ]
        serializer = EventSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['tags']))

    def test_event_creation_with_invalid_category(self):
        data = self.valid_data['one_schedule_no_to_date']
        data['categories'] = [
            {
                "name": "bad_category_name"
            }
        ]
        serializer = EventSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['categories']))

    def test_only_show_future_occurrences_of_event(self):
        """Test returning events with only future occurrencies"""
        event = Event.objects.create(name='Evento 1', description='Desc 1', winery=self.winery, price=0.0)
        EventOccurrence.objects.create(
            start='2018-10-31T20:00:00',
            end='2018-10-31T23:00:00',
            vacancies=50,
            event=event
        )
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=event
        )
        res = self.client.get(
            reverse("event-detail", kwargs={'pk': event.id})
        )

        self.assertTrue(
            all(
                [datetime.strptime(occurrence['start'], "%Y-%m-%dT%H:%M:%S") > datetime.now()
                    for occurrence in res.data['occurrences']]
            )
        )

    def test_get_winery_events(self):
        event = Event.objects.create(
            name='Event from winery',
            description='Should be shown',
            winery=self.winery,
            price=0.0
        )
        other_winery = Winery.objects.create(
                name='Other Winery',
                description='test',
                website='test.com',
        )
        event_from_other_winery = Event.objects.create(
            name='Other Winery Event',
            description='Should not be shown',
            winery=other_winery,
            price=0.0
        )
        EventOccurrence.objects.create(
            start='2036-10-31T20:00:00',
            end='2036-10-31T23:00:00',
            vacancies=50,
            event=event
        )
        EventOccurrence.objects.create(
            start='2036-10-31T20:00:00',
            end='2036-10-31T23:00:00',
            vacancies=50,
            event=event_from_other_winery
        )

        res = self.client.get(
            reverse('winery-events', kwargs={'pk': self.winery.id}),
        )
        serializer_event = EventSerializer(event)
        serializer_event_from_other_winery = EventSerializer(event_from_other_winery)

        self.assertIn(serializer_event.data, res.data)
        self.assertNotIn(serializer_event_from_other_winery.data, res.data)

    def test_get_winery_restaurants(self):
        event = Event.objects.create(
            name='Event from winery',
            description='Should be shown',
            winery=self.winery,
            price=0.0
        )
        event.categories.add(self.category_restaurant)
        event.save()

        other_winery = Winery.objects.create(
                name='Other Winery',
                description='test',
                website='test.com',
        )
        event_from_other_winery = Event.objects.create(
            name='Other Winery Event',
            description='Should not be shown',
            winery=other_winery,
            price=0.0
        )
        event_from_other_winery.categories.add(self.category_restaurant)
        event_from_other_winery.save()

        EventOccurrence.objects.create(
            start='2036-10-31T20:00:00',
            end='2036-10-31T23:00:00',
            vacancies=50,
            event=event
        )
        EventOccurrence.objects.create(
            start='2036-10-31T20:00:00',
            end='2036-10-31T23:00:00',
            vacancies=50,
            event=event_from_other_winery
        )

        res = self.client.get(
            reverse('winery-restaurants', kwargs={'pk': self.winery.id}),
        )
        serializer_event = EventSerializer(event)
        serializer_event_from_other_winery = EventSerializer(event_from_other_winery)

        self.assertIn(serializer_event.data, res.data)
        self.assertNotIn(serializer_event_from_other_winery.data, res.data)

    def test_events_endpoints_exclude_restaurants(self):
        """Test returning events without restaurant category"""
        event1 = Event.objects.create(name='Evento 1', description='Desc 1', winery=self.winery, price=0.0)
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=event1
        )
        event2 = Event.objects.create(name='Restaurante', description='Desc 1', winery=self.winery, price=0.0)
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=event2
        )
        event1.categories.add(self.category1)
        event1.categories.add(self.category2)
        event2.categories.add(self.category_restaurant)
        res = self.client.get(
            '/api/events/'
        )
        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_restaurants_endpoint(self):
        """Test that the endpoint only returns events with restaurant categories"""
        event1 = Event.objects.create(name='Restaurante', description='Desc 1', winery=self.winery, price=0.0)
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=event1
        )
        event2 = Event.objects.create(name='Evento 1', description='Desc 1', winery=self.winery, price=0.0)
        EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=event2
        )
        event1.categories.add(self.category_restaurant)
        event2.categories.add(self.category1)
        event2.categories.add(self.category2)
        res = self.client.get(
            reverse('restaurant-list'),
        )
        serializer1 = EventSerializer(event1)
        serializer2 = EventSerializer(event2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_event_get_occurrences(self):
        event = Event.objects.create(name='Test Event', description='Desc 1', winery=self.winery, price=0.0)
        occurrence = EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=event
        )
        res = self.client.get(
            reverse('event-occurrences-list', kwargs={'event_pk': event.id}),
        )
        serializer = EventOccurrenceSerializer(occurrence)
        self.assertIn(serializer.data, res.data)

    def test_event_occurrences_post(self):
        event = Event.objects.create(name='Test Event', description='Desc 1', winery=self.winery, price=0.0)
        res = self.client.post(
            reverse('event-occurrences-list', kwargs={'event_pk': event.id}),
            {
                'start': '2030-05-31T20:00:00',
                'end': '2030-05-31T23:00:00',
                'vacancies': 50,
                'event': event,
            }
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            res.data.get('url'),
            reverse('event-occurrences-detail', kwargs={'event_pk': event.id, 'pk': 1})
        )

    def test_restaurant_get_occurrences(self):
        restaurant = Event.objects.create(name='Test restaurant', description='Desc 1', winery=self.winery, price=0.0)
        restaurant.categories.add(self.category_restaurant)
        restaurant.save()

        occurrence = EventOccurrence.objects.create(
            start='2030-05-31T20:00:00',
            end='2030-05-31T23:00:00',
            vacancies=50,
            event=restaurant
        )
        res = self.client.get(
            reverse('restaurant-occurrences-list', kwargs={'restaurant_pk': restaurant.id}),
        )
        serializer = EventOccurrenceSerializer(occurrence)
        self.assertIn(serializer.data, res.data)

    def test_restaurant_occurrences_post(self):
        restaurant = Event.objects.create(name='Test Restaurant', description='Desc 1', winery=self.winery, price=0.0)
        restaurant.categories.add(self.category_restaurant)
        restaurant.save()

        res = self.client.post(
            reverse('restaurant-occurrences-list', kwargs={'restaurant_pk': restaurant.id}),
            {
                'start': '2030-05-31T20:00:00',
                'end': '2030-05-31T23:00:00',
                'vacancies': 50,
                'event': restaurant,
            }
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            res.data.get('url'),
            reverse('restaurant-occurrences-detail', kwargs={'restaurant_pk': restaurant.id, 'pk': 1})
        )

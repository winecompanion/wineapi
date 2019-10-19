from django_filters import DateTimeFromToRangeFilter, FilterSet, ModelMultipleChoiceFilter

from .models import Event, EventCategory, Tag


class EventFilter(FilterSet):
    # https://django-filter.readthedocs.io/en/latest/guide/usage.html#declaring-filters

    start = DateTimeFromToRangeFilter(field_name='occurrences__start')
    category = ModelMultipleChoiceFilter(
        field_name='categories__name',
        to_field_name='name',
        queryset=EventCategory.objects.all()
    )
    tag = ModelMultipleChoiceFilter(
        field_name='tags__name',
        to_field_name='name',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Event
        fields = ['occurrences__start', 'category', 'tag']

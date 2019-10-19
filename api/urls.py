from django.urls import include, path

from rest_framework_nested import routers

from api.views import (
    CountryView,
    EventsView,
    EventCategoryView,
    EventOccurrencesView,
    FileUploadView,
    MapsView,
    RatingView,
    ReportsView,
    ReservationView,
    RestaurantsView,
    RestaurantOccurrencesView,
    TagView,
    VarietalsView,
    WineryView,
    WineLineView,
    WineView,
)

router = routers.DefaultRouter()

router.register(r'wineries', WineryView, basename='winery')

wine_lines_router = routers.NestedDefaultRouter(router, r'wineries', lookup='winery')
wine_lines_router.register(r'wine-lines', WineLineView, basename='winelines')
# router.register(r'wine-lines', WineLineView, basename='wine-line')

wines_router = routers.NestedDefaultRouter(wine_lines_router, r'wine-lines', lookup='wineline')
wines_router.register(r'wines', WineView, basename='wines')
# router.register(r'wines', WineView, basename='wine')

router.register(r'events', EventsView, basename='event')
router.register(r'restaurants', RestaurantsView, basename='restaurant')

ratings_router = routers.NestedDefaultRouter(router, r'events', lookup='event')
ratings_router.register(r'ratings', RatingView, basename='event-ratings')
# router.register(r'rates', RatingView, basename='rates')

event_occurrences_router = routers.NestedDefaultRouter(router, r'events', lookup='event')
event_occurrences_router.register(r'occurrences', EventOccurrencesView, basename='event-occurrences')

restaurant_occurrences_router = routers.NestedDefaultRouter(router, r'restaurants', lookup='restaurant')
restaurant_occurrences_router.register(r'occurrences', RestaurantOccurrencesView, basename='restaurant-occurrences')
restaurant_ratings_router = routers.NestedDefaultRouter(router, r'restaurants', lookup='restaurant')
restaurant_ratings_router.register(r'ratings', RatingView, basename='restaurant-ratings')


router.register(r'tags', TagView, basename='tags')
router.register(r'countries', CountryView, basename='countries')
router.register(r'event-categories', EventCategoryView, basename='event-categories')
router.register(r'reservations', ReservationView, basename='reservations')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(wine_lines_router.urls)),
    path('', include(wines_router.urls)),
    path('', include(ratings_router.urls)),
    path('', include(event_occurrences_router.urls)),
    path('', include(restaurant_occurrences_router.urls)),
    path('', include(restaurant_ratings_router.urls)),
    path('maps/', MapsView.as_view()),
    path('reports/reservations/', ReportsView.as_view(), name='reservation-count-reports'),
    path('varietals/', VarietalsView.as_view(), name='varietals'),
    path('upload/', FileUploadView.as_view()),
]

from django.urls import include, path

from rest_framework_nested import routers

from api.views import (
    WineryApprovalView,
    CountryView,
    EventsView,
    EventCategoryView,
    EventReservationsView,
    EventOccurrencesView,
    FileUploadView,
    MapsView,
    RatingView,
    ReportsView,
    ReservationView,
    RestaurantsView,
    RestaurantOccurrencesView,
    TagView,
    VarietalView,
    WineryView,
    WineLineView,
    WineView,
    GenderView,
    LanguageView,
)

router = routers.DefaultRouter()

# Winery, Wine-Lines and Wines
router.register(r'wineries', WineryView, basename='winery')

wine_lines_router = routers.NestedDefaultRouter(router, r'wineries', lookup='winery')
wine_lines_router.register(r'wine-lines', WineLineView, basename='winelines')

wines_router = routers.NestedDefaultRouter(wine_lines_router, r'wine-lines', lookup='wineline')
wines_router.register(r'wines', WineView, basename='wines')

# Reservations
router.register(r'reservations', ReservationView, basename='reservations')

# Events
router.register(r'events', EventsView, basename='event')

# Event-Ratings
ratings_router = routers.NestedDefaultRouter(router, r'events', lookup='event')
ratings_router.register(r'ratings', RatingView, basename='event-ratings')

# Event-occurrences
event_occurrences_router = routers.NestedDefaultRouter(router, r'events', lookup='event')
event_occurrences_router.register(r'occurrences', EventOccurrencesView, basename='event-occurrences')

# Event-reservations
event_reservations_router = routers.NestedDefaultRouter(
    event_occurrences_router,
    r'occurrences',
    lookup='occurrence'
)
event_reservations_router.register(r'reservations', EventReservationsView, basename='event-reservations')

# Restaurants
router.register(r'restaurants', RestaurantsView, basename='restaurant')

# Restaurant-occurrences
restaurant_occurrences_router = routers.NestedDefaultRouter(router, r'restaurants', lookup='restaurant')
restaurant_occurrences_router.register(
    r'occurrences',
    RestaurantOccurrencesView,
    basename='restaurant-occurrences'
)

# Restaurant-ratings
restaurant_ratings_router = routers.NestedDefaultRouter(router, r'restaurants', lookup='restaurant')
restaurant_ratings_router.register(r'ratings', RatingView, basename='restaurant-ratings')

# Restaurant-reservations
restaurant_reservations_router = routers.NestedDefaultRouter(
    restaurant_occurrences_router,
    r'occurrences',
    lookup='occurrence'
)
restaurant_reservations_router.register(r'reservations', EventReservationsView, basename='restaurant-reservations')


# Admin
router.register(r'tags', TagView, basename='tags')
router.register(r'countries', CountryView, basename='countries')
router.register(r'varietals', VarietalView, basename='varietals')
router.register(r'languages', LanguageView, basename='languages')
router.register(r'genders', GenderView, basename='genders')
router.register(r'event-categories', EventCategoryView, basename='event-categories')
router.register(r'approve-wineries', WineryApprovalView, basename='approve-wineries')

# Patterns
urlpatterns = [
    path('', include(router.urls)),
    path('', include(wine_lines_router.urls)),
    path('', include(wines_router.urls)),
    path('', include(ratings_router.urls)),
    path('', include(event_occurrences_router.urls)),
    path('', include(restaurant_occurrences_router.urls)),
    path('', include(event_reservations_router.urls)),
    path('', include(restaurant_reservations_router.urls)),
    path('', include(restaurant_ratings_router.urls)),
    path('maps/', MapsView.as_view()),
    path('reports/reservations/', ReportsView.as_view(), name='reservation-count-reports'),
    path('upload/', FileUploadView.as_view()),
]

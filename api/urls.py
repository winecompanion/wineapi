from django.urls import include, path

from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register(r'wineries', views.WineryView, basename='winery')

wine_lines_router = routers.NestedDefaultRouter(router, r'wineries', lookup='winery')
wine_lines_router.register(r'wine-lines', views.WineLineView, basename='winelines')
# router.register(r'wine-lines', views.WineLineView, basename='wine-line')

wines_router = routers.NestedDefaultRouter(wine_lines_router, r'wine-lines', lookup='wineline')
wines_router.register(r'wines', views.WineView, basename='wines')
# router.register(r'wines', views.WineView, basename='wine')

router.register(r'events', views.EventsView)

ratings_router = routers.NestedDefaultRouter(router, r'events', lookup='event')
ratings_router.register(r'ratings', views.RatingView, basename='event-ratings')
# router.register(r'rates', views.RatingView, basename='rates')

router.register(r'tags', views.TagView, basename='tags')
router.register(r'event-categories', views.EventCategoryView, basename='event-categories')
router.register(r'reservations', views.ReservationView, basename='reservations')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(wine_lines_router.urls)),
    path('', include(wines_router.urls)),
    path('', include(ratings_router.urls)),
    path('maps/', views.MapsView.as_view()),
    path('varietals/', views.VarietalsView.as_view(), name='varietals'),
    path('upload/', views.FileUploadView.as_view()),
]

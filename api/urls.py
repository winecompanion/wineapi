from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'events', views.EventsView)
router.register(r'wineries', views.WineryView, basename='winery')
router.register(r'wine-lines', views.WineLineView, basename='wine-line')
router.register(r'wines', views.WineView, basename='wine')
router.register(r'tags', views.TagView, basename='tags')
router.register(r'event-categories', views.EventCategoryView, basename='event-categories')
router.register(r'reservations', views.ReservationView, basename='reservations')

urlpatterns = [
    path('', include(router.urls)),
    path('maps/', views.MapsView.as_view()),
    path('varietals/', views.VarietalsView.as_view(), name='varietals'),
]

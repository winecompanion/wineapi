from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'events', views.EventsView)
router.register(r'wineries', views.WineryView, basename='winery')
router.register(r'wine-lines', views.WineLineView, basename='wine-line')
router.register(r'wines', views.WineView, basename='wine')
router.register(r'maps', views.MapsView, basename='maps')
router.register(r'tags', views.TagView, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]

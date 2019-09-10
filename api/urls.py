from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'events', views.EventsView)
router.register(r'wineries', views.WineryView)

urlpatterns = [
    path('', include(router.urls)),
]

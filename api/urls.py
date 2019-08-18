from django.urls import path
from api import views

urlpatterns = [
        path('event-list', views.EventListView.as_view()),
        ]

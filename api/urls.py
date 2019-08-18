from django.urls import path
from api import views

urlpatterns = [
        path('event_list', views.EventListView.as_view()),
        ]

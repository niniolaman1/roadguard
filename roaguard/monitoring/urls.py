from django.urls import path
from . import views

urlpatterns = [
    path('trip/latest/', views.latest_trip, name='latest_trip'),
    path('trips/', views.all_trips, name='all_trips'),
]
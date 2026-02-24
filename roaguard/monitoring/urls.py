from django.urls import path
from . import views

urlpatterns = [
    path('trip/latest/', views.latest_trip, name='latest_trip'),
]
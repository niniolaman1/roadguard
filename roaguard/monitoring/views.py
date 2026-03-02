from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Trip
from .serializers import TripSerializer

@api_view(['GET'])
def latest_trip(request):
    try:
        trip = Trip.objects.prefetch_related('events').latest('start_time')
        serializer = TripSerializer(trip)
        return Response(serializer.data)
    except Trip.DoesNotExist:
        return Response(
            {'message': 'No trips recorded yet'},
            status=status.HTTP_404_NOT_FOUND
        )
@api_view(['GET'])
def all_trips(request):
    trips = Trip.objects.prefetch_related('events').order_by('-start_time')
    serializer = TripSerializer(trips, many=True)
    return Response(serializer.data)
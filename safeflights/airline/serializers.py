from rest_framework import serializers
from .models import FlightInfo

class FlightInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightInfo
        fields = (
            'id',
            'flight_number',
            'flight_price',
            'seat_list',
            'departure_airport',
            'destination_airport',
            'arrival_date',
            'departure_date'
        )
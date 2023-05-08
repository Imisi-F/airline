from django.contrib import admin

from .models import Bookings, PassengerSeatInfo, FlightInfo, Airports

admin.site.register(Bookings)
admin.site.register(PassengerSeatInfo)
admin.site.register(FlightInfo)
admin.site.register(Airports)
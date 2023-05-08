from django.urls import path
from . import views

urlpatterns = [
    path('flights/', views.getFlightsInfo, name='flights'),
    path('flights/<int:flight_id>/seats/<str:seat_codes>/', views.selectFlightSeat, name='select_flight_seat'),
    path('flights/<int:flight_id>/bookings/', views.confirmFlightSeat, name='confirm_booking'),
    path('', views.add_flights, name='add_flights'),
]
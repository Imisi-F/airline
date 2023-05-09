from django.urls import path
from . import views

urlpatterns = [
    path('', views.allFlights, name='all_flights'),
    path('flights/departure/<str:departure>/destination/<str:destination>/departure_date/<str:departure_date>/seat_class/<str:seat_class>/ticket_adult/<int:ticket_adult>/ticket_child/<int:ticket_child>/', views.getFlightsInfo, name='flights'),
    path('flights/<int:flight_id>/seats/<str:seat_codes>/', views.selectFlightSeat, name='select_flight_seat'),
    path('flights/<int:flight_id>/bookings/', views.confirmFlightSeat, name='confirm_booking')
]
# flights/departure/JFK/destination/LAX/departure_date/2023-05-10/seat_class/first/ticket_adult/2/ticket_child/1/
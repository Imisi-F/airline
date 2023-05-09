from django.urls import path
from . import views

urlpatterns = [
    path('', views.allFlights, name='all_flights'),
    
    path('flights/departure/<str:departure>/destination/<str:destination>/departure_date/<str:departure_date>/seat_class/<str:seat_class>/ticket_adult/<int:ticket_adult>/ticket_child/<int:ticket_child>/', views.getFlightsInfo, name='flights'),
    
    path('flights/<int:flight_id>/seats/<str:seat_codes>/', views.selectFlightSeat, name='select_flight_seat'),
    
    path('flights/<int:flight_id>/booking_id/<int:booking_id>/transaction_id/<int:transaction_id>/seats/<str:seat_codes>/email/<str:email>/number_tickets/<int:number_tickets>/total_price/<str:total_price>/cancelled/<str:cancelled>/', views.confirmFlightSeat, name='confirm_booking')
]
# To test getFlightsInfo:
# http://127.0.0.1:8000/airline/flights/departure/JFK/destination/LAX/departure_date/2023-05-10/seat_class/first/ticket_adult/2/ticket_child/1/

# To test selectFlightSeat:
# http://127.0.0.1:8000/airline/flights/11/seats/sy,sw,sx

# To test confirmFlightSeat:
# http://127.0.0.1:8000/airline/flights/11/booking_id/200/transaction_id/200/seats/sw,sx/email/example@example.com/number_tickets/2/total_price/1000/cancelled/False/
# http://127.0.0.1:8000/airline/flights/11/booking_id/200/transaction_id/200/seats/sw,sx/email/example@example.com/number_tickets/2/total_price/1000/cancelled/True/
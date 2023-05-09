from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .models import FlightInfo, Bookings
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@api_view(['GET'])
def allFlights(request):
  all_flights = [flight.flight_number for flight in FlightInfo.objects.all()]
  return Response(all_flights, status=status.HTTP_200_OK)

# retrieve the user's search parameters from the query string
@api_view(['GET'])
def getFlightsInfo (request, departure, destination, departure_date, seat_class, ticket_adult, ticket_child):
  if request.method == 'GET':
    # Setting user params for flight
    departure_airport = str(departure).upper()
    destination_airport = str(destination).upper()
    departure_date = departure_date
    class_multiplier = 1.0
    if 'first' in str(seat_class).lower():
      class_multiplier = 5.0
    if 'business' in str(seat_class).lower():
      class_multiplier = 2.5
    no_of_tickets = ticket_adult + ticket_child
    # Filter based on user input  
    flight_info_list = FlightInfo.objects.all().filter(departure_airport=departure_airport, destination_airport=destination_airport, departure_date__contains=departure_date)
    # Make flights info a JSON obj, include calculated flight duration and flight price
    flights_info_json = []
    for flight in flight_info_list:
      # if there's enough available seats on the flight
      if flight.seat_list.count('0') >= no_of_tickets:
        # calculate the total duration of the flight in minute
        d_time = flight.departure_date
        a_time  = flight.arrival_date
        duration = a_time - d_time
        s_duration = duration.total_seconds()
        flight_time = divmod(s_duration, 60)[0]
        # Child price is 50% of adults
        flight_price =( (float(flight.flight_price) * 
        float(ticket_adult)) + (float(flight.flight_price) * 0.5 * float(ticket_child))) * class_multiplier
        # Adding to the json-style list 
        flights_info_json.append("id:{},flight_number:{},seats_available:{},departure_airport:{},destination_airport:{},departure_date:{},arrival_date:{},flight_time_mins:{},flight_price:{}".format(flight.id, flight.flight_number, flight.seat_list, flight.departure_airport, flight.destination_airport, flight.departure_date, flight.arrival_date, flight_time, flight_price))
    return Response({'flights': flights_info_json}, status=status.HTTP_201_CREATED)
  else:
    return Response(status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET','POST'])
def selectFlightSeat (request, flight_id, seat_codes):
  if request.method == 'GET' or request.method == 'POST':
    try:
      seats = FlightInfo.objects.all().get(id=flight_id)
    except FlightInfo.objects.all().get(id=flight_id).DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # checks if there are some seats
    if str(seats.seat_list).count('0') < 1:
      return Response('No seats available')
    # seat format setcode:takenno, setcode2:takenno2,
    seats_status = {}
    taken_flag = 0
    list_seats = str(seats.seat_list).split(',')
    # seeing if all the seats are taken or not
    for code in seat_codes.split(','):
      for word in list_seats:
        if code == word.split(':')[0]:
          if word.split(':')[1] == '1':
            seats_status[code] = 'Taken'
          elif word.split(':')[1] == '0':
            seats_status[code] = 'Not Taken'
    for x in seats_status.values():
      if x == 'Taken':
        taken_flag += 1
    if taken_flag > 0:
      # if any seats are taken:
      return Response(seats_status.items(),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
      return Response({'seats': seats_status.items()}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET','POST'])
def confirmFlightSeat (request, flight_id, booking_id,transaction_id, seat_codes, email, number_tickets, total_price, cancelled):
  if request.method == 'POST' or request.method == 'GET':
    try:
      flight_info = FlightInfo.objects.all().get(id=flight_id)
    except FlightInfo.objects.all().get(id=flight_id).DoesNotExist:
      return Response(status=status.HTTP_404_NOT_FOUND)
    # if booking has not been cancelled
    if cancelled.lower() == 'false':
      # creating a new booking
      booking = Bookings.objects.create(
      id=booking_id, 
      transaction_id=float(transaction_id), 
      seat_codes=seat_codes,
      email=email,
      number_tickets=number_tickets,
      total_price=total_price,
      cancelled=cancelled)
      booking.save()
      # updating the seat_list in the flight's info
      seats_update = flight_info.seat_list.split(',')
      i = 0
      for seat in seats_update:
        for code in seat_codes.split(','):
          if code == seat.split(':')[0]:
            temp = seat.split(':')[1].replace('0', '1')
            update_seat = "{}:{}".format(code,temp)
            seats_update[i] = update_seat
        i += 1
      flight_info.seat_list = ','.join(seats_update)
      flight_info.save()
      return Response(flight_info.seat_list, status=status.HTTP_200_OK)
    # if booking has not been cancelled
    elif cancelled.lower() == 'true':
      # setting cancelled flag to true
      booking = Bookings.objects.all().get(id=booking_id)
      booking.cancelled = cancelled
      booking.save()
      # updating the seat_list in the flight's info
      seats_update = flight_info.seat_list.split(',')
      i = 0
      for seat in seats_update:
        for code in seat_codes.split(','):
          if code == seat.split(':')[0]:
            temp = seat.split(':')[1].replace('1', '0')
            update_seat = "{}:{}".format(code,temp)
            seats_update[i] = update_seat
        i += 1
      flight_info.seat_list = ','.join(seats_update)
      flight_info.save()
      return Response(flight_info.seat_list, status=status.HTTP_200_OK)

    else:
      return Response(flight_info.seat_list, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
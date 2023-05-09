from django.shortcuts import render
from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .models import FlightInfo, PassengerSeatInfo, Bookings,Airports
from datetime import datetime, timedelta
from django.http import JsonResponse

@api_view(['GET'])
def allFlights(request):
  all_flights = [flight.flight_number for flight in FlightInfo.objects.all()]
  # return JsonResponse({'all_flights': all_flights}, status=status.HTTP_202_ACCEPTED))
  return Response(all_flights, status=status.HTTP_202_ACCEPTED)


# use @csrf_exempt if you wanna use post requests
  # Assuming info comes as a string in format (NO SPACES):
  # [departure/<str:departure>/destination/<str:destination>/departure_date/<str:departure_date in dd-mm-yyyy>/seat_class/<str:seat_class>/ticket_adult/<int:ticket_adult>/ticket_child/<int:ticket_child>/]
  # retrieve the user's search parameters from the query string
@api_view(['GET'])
def getFlightsInfo (request, departure, destination, departure_date, seat_class, ticket_adult, ticket_child):
  if request.method == 'GET':
    print("{}, {}, {}, {}, {}".format, destination, departure,seat_class,ticket_adult, ticket_child)
    departure_airport = str(departure).upper()
    destination_airport = str(destination).upper()
    departure_date = departure_date
    class_multiplier = 1.0
    if 'first' in str(seat_class).lower():
      class_multiplier = 2.0
    if 'business' in str(seat_class).lower():
      class_multiplier = 1.5
    print("{}".format, class_multiplier)
    no_of_tickets = ticket_adult + ticket_child
    # Filter based on user input  
    flight_info_list = FlightInfo.objects.all().filter(departure_airport=departure_airport, destination_airport=destination_airport, departure_date__contains=departure_date)
    # Make flights info a JSON obj, include calculated flight duration and flight price
    flights_info_json = []
    
    print("okay")
    for flight in flight_info_list:
      # len(flight.seat_list.split(','))
      # if there's enough available seats on the flight
      if flight.seat_list.count('0') >= no_of_tickets:
        # calculate the total duration of the flight
        hour = abs(flight.arrival_date.time().hour - flight.departure_date.time().hour) * 60
        minute = abs(flight.arrival_date.time().minute  - flight.departure_date.time().minute)
        second = abs(flight.arrival_date.time().second - flight.departure_date.time().second) / 60
        flight_time = hour + minute + second
        # Child price is 50% of adults
        flight_price =( (float(flight.flight_price) * 
        float(ticket_adult)) + (float(flight.flight_price) * 0.5 * float(ticket_child))) * class_multiplier
        # Adding to the json-style list 
        flights_info_json.append("id:{},flight_number:{},seats_available:{},departure_airport:{},destination_airport:{},departure_date:{},arrival_date:{},flight_time_mins:{},flight_price:{}".format(flight.id, flight.flight_number, flight.seat_list, flight.departure_airport, flight.destination_airport, flight.departure_date, flight.arrival_date, flight_time, flight_price))
    return Response({'flights': flights_info_json}, status=status.HTTP_201_CREATED)
  else:
    return Response(status=status.HTTP_400_BAD_REQUEST)

# @csrf_exempt
@api_view(['POST'])
def selectFlightSeat (request, flight_id, seat_codes):
  if request.method == 'POST':
    try:
      seats = FlightInfo.objects.all().get(id=flight_id)
    except FlightInfo.DoesNotExist:
        return HttpResponse('404_NOT_FOUND')
    #shows there are some seats
    if str(seats.seat_list).count('0') < 1:
      return HttpResponse('No seats available')
    # seat format setcode:takenno, setcode2:takenno2,
    seats_status = {}
    taken_flag = 0
    list_seats = str(seats.seat_list).split(',')
    # seeing if the seats are taken or not
    for word in list_seats:
      for code in seat_codes:
        if code.lower() in word.lower() and "0" in word:
          seats_status[code] = 'Taken'
        else:
          seats_status[code] = 'Not Taken'
    for x in seats_status.values():
      if x == 'Taken':
        taken_flag += 1
    if taken_flag > 0:
      # if seats are taken:
      return seats_status.items(),HttpResponse("\n{} seat(s) are taken\nStatus Code: 500".format(taken_flag))
    else:
      # reserving specified empty seats depending on user input
      reserved = str(seats.seat_list).split(',')
      for i in range(len(reserved)):
        for code in seat_codes:
          if code in reserved[i]:
            reserved[i] = "{}:{}".format(code,'1')
      new_seats = ','.join(reserved)
      seats.seat_list = new_seats
      seats.save()
      return JsonResponse({'seats': seats_status.values()}), HttpResponse("All seat(s) have been reserved.\nStatus Code: 200")

# @csrf_exempt
@api_view(['POST'])
def confirmFlightSeat (request, flight_id, booking_info):
  if request.method == 'POST':
    try:
      flight_info = FlightInfo.objects.all().get(id=flight_id)
    except FlightInfo.DoesNotExist:
      return HttpResponse('404_NOT_FOUND')
    # creating a new booking
    booking = Bookings.objects.create(
    id=booking_info['booking_id'], 
    transaction_id=booking_info['transaction_id'], 
    seat_codes=booking_info['seat_codes'],
    email=booking_info['email'],
    number_tickets=booking_info['number_tickets'],
    total_price=booking_info['total_price'],
    cancelled=booking_info['cancelled'])
    return HttpResponse('Added new booking. Status: 200'), flight_info.seat_list



'''flight_info_isolated = [] 
    flight_info = list(request.body).split(',')
    ticket_adult = int(flight_info[4])
    ticket_child = int(flight_info[5])
    no_of_tickets = ticket_adult + ticket_child
    for info in flight_info:
      info_isolated = info.split('=')
      flight_info_isolated.append(str(info_isolated[1]))
    # Filter based on user input  
    flight_info_list = FlightInfo.objects.all().filter(departure_airport=flight_info_isolated[0], destination_airport=flight_info_isolated[1], departure_date=flight_info_isolated[2], seat_class__contains=flight_info_isolated[3])
    # Make flights info a JSON obj, include calculated flight duration and flight price
    flights_info_json = []
    if len(flight_info_list) > no_of_tickets:
      for flight in flight_info_list:
        hour = abs(flight(name='arrival_date').time().hour - flight(name='departure_date').time().hour) *60
        minute = abs(flight(name='arrival_date').time().minute - flight(name='departure_date').time().minute)
        second = abs(flight(name='arrival_date').time().second - flight(name='departure_date').time().second) /60
        flight_time_mins = hour + minute + second
        # Child price is 50% of adults
        flight_price = (flight(name='flight_price') * 
        ticket_adult) + (flight(name='flight_price') * 0.5 * ticket_child)
        # Adding to the json-style list 
        flights_info_json.append("id:{},flight_number:{},seats_available:{},departure_airport:{},destination_airport:{},departure_date:{},arrival_date:{},flight_time_mins:{},flight_price:{}".format(flight(name='id'), flight(name='flight_number'), flight(name='seat_list'), flight(name='departure_airport'), flight(name='destination_airport'), flight(name='departure_date'), flight(name='arrival_date'), flight_time_mins, flight_price))
      return flights_info_json, HttpResponse.status_code
    else:
      return HttpResponse('No flights available')'''
from django.shortcuts import render
from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from .models import FlightInfo, PassengerSeatInfo, Bookings,Airports
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.response import Response


# use @csrf_exempt if you wanna use post requests
@api_view(['GET'])
def getFlightsInfo (request):
  # Assuming info comes as a string in format (NO SPACES):
  # [departure=...,destination=...,departure_date=...,class=...,ticket_adult=...,ticket_child=...]
  # retrieve the user's search parameters from the query string
  if request.method == 'GET':
    departure_airport = request.GET.get('departure')
    destination_airport = request.GET.get('destination')
    departure_datetime = request.GET.get('datetime')
    seat_class = request.GET.get('seat_class')
    class_multiplier = 1
    if 'first' in str(seat_class).lower:
      class_multiplier = 2
    if 'business' in str(seat_class).lower:
      class_multiplier = 1.5

    no_of_tickets_a = int(request.GET.get('Ticket_adult'))
    no_of_tickets_c = int(request.GET.get('Ticket_child'))
    no_of_tickets = no_of_tickets_a + no_of_tickets_c
    # Filter based on user input  
    flight_info_list = FlightInfo.objects.all().filter(departure_airport=departure_airport, destination_airport=destination_airport, departure_date=departure_datetime, seat_class__contains=seat_class)
    # Make flights info a JSON obj, include calculated flight duration and flight price
    flights_info_json = []
    if len(flight_info_list) > no_of_tickets:
      for flight in flight_info_list:
        # calculate the total duration of the flight
        hour = abs(flight.arrival_date.time().hour - flight.departure_date.time().hour) * 60
        minute = abs(flight.arrival_date.time().minute  - flight.departure_date.time().minute)
        second = abs(flight.arrival_date.time().second - flight.departure_date.time().second) / 60
        flight_time = hour + minute + second
        # Child price is 50% of adults
        flight_price =( (flight.flight_price * 
        no_of_tickets_a) + (flight.flight_price * 0.5 * no_of_tickets_c)) * class_multiplier
        # Adding to the json-style list 
        flights_info_json.append("id:{},flight_number:{},seats_available:{},departure_airport:{},destination_airport:{},departure_date:{},arrival_date:{},flight_time_mins:{},flight_price:{}".format(flight.id, flight.flight_number, flight.seat_list, flight.departure_airport, flight.destination_airport, flight.departure_date, flight.arrival_date, flight_time, flight_price))
      return JsonResponse({'flights': flights_info_json}), HttpResponse.status_code
    else:
      return HttpResponse('No flights available')

  else:
    return HttpResponse('Wrong request, should send GET')


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
  
@api_view(['POST'])
def add_flights(flight_data_list):
    for data in flight_data_list:
        departure_airport = Airports.objects.get(code=data['departure_airport_code'])
        arrival_airport = Airports.objects.get(code=data['arrival_airport_code'])
        departure_time = datetime.strptime(data['departure_time'], '%Y-%m-%d %H:%M:%S')
        arrival_time = datetime.strptime(data['arrival_time'], '%Y-%m-%d %H:%M:%S')
        duration = arrival_time - departure_time
        flight = FlightInfo.objects.create(
            number=data['flight_number'],
            departure_airport=departure_airport,
            departure_time=departure_time,
            arrival_airport=arrival_airport,
            arrival_time=arrival_time,
            duration=duration,
            price=data['price']
        )

flight_data_list = [
    {
        'flight_number': 'AA101',
        'origin': 'JFK',
        'destination': 'LAX',
        'departure_time': datetime.now() + timedelta(days=1),
        'arrival_time': datetime.now() + timedelta(days=1, hours=6),
        'price': 250.00,
    },
    {
        'flight_number': 'UA203',
        'origin': 'LAX',
        'destination': 'ORD',
        'departure_time': datetime.now() + timedelta(days=2),
        'arrival_time': datetime.now() + timedelta(days=2, hours=4),
        'price': 350.00,
    },
    {
        'flight_number': 'DL311',
        'origin': 'JFK',
        'destination': 'ATL',
        'departure_time': datetime.now() + timedelta(days=1),
        'arrival_time': datetime.now() + timedelta(days=1, hours=3),
        'price': 150.00,
    },
    {
        'flight_number': 'AA444',
        'origin': 'LAX',
        'destination': 'SFO',
        'departure_time': datetime.now() + timedelta(days=1, hours=12),
        'arrival_time': datetime.now() + timedelta(days=1, hours=13, minutes=30),
        'price': 100.00,
    },
    {
        'flight_number': 'UA555',
        'origin': 'ORD',
        'destination': 'LAX',
        'departure_time': datetime.now() + timedelta(days=2, hours=10),
        'arrival_time': datetime.now() + timedelta(days=2, hours=14),
        'price': 375.00,
    },
    {
        'flight_number': 'DL666',
        'origin': 'ATL',
        'destination': 'JFK',
        'departure_time': datetime.now() + timedelta(days=1, hours=20),
        'arrival_time': datetime.now() + timedelta(days=1, hours=23),
        'price': 175.00,
    },
    {
        'flight_number': 'AA777',
        'origin': 'LAX',
        'destination': 'ORD',
        'departure_time': datetime.now() + timedelta(days=3),
        'arrival_time': datetime.now() + timedelta(days=3, hours=6),
        'price': 300.00,
    },
    {
        'flight_number': 'UA888',
        'origin': 'ORD',
        'destination': 'SFO',
        'departure_time': datetime.now() + timedelta(days=2, hours=8),
        'arrival_time': datetime.now() + timedelta(days=2, hours=11, minutes=30),
        'price': 400.00,
    },
    {
        'flight_number': 'DL999',
        'origin': 'JFK',
        'destination': 'LAX',
        'departure_time': datetime.now() + timedelta(days=2, hours=16),
        'arrival_time': datetime.now() + timedelta(days=2, hours=22),
        'price': 275.00,
    },
    {
        'flight_number': 'AA1111',
        'origin': 'SFO',
        'destination': 'ORD',
        'departure_time': datetime.now() + timedelta(days=4),
        'arrival_time': datetime.now() + timedelta(days=4, hours=7),
        'price': 350.00,
    }
]



'''flight_info_isolated = [] 
    flight_info = list(request.body).split(',')
    no_of_tickets_a = int(flight_info[4])
    no_of_tickets_c = int(flight_info[5])
    no_of_tickets = no_of_tickets_a + no_of_tickets_c
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
        no_of_tickets_a) + (flight(name='flight_price') * 0.5 * no_of_tickets_c)
        # Adding to the json-style list 
        flights_info_json.append("id:{},flight_number:{},seats_available:{},departure_airport:{},destination_airport:{},departure_date:{},arrival_date:{},flight_time_mins:{},flight_price:{}".format(flight(name='id'), flight(name='flight_number'), flight(name='seat_list'), flight(name='departure_airport'), flight(name='destination_airport'), flight(name='departure_date'), flight(name='arrival_date'), flight_time_mins, flight_price))
      return flights_info_json, HttpResponse.status_code
    else:
      return HttpResponse('No flights available')'''
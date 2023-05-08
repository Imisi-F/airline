from datetime import datetime
from airline import models
from datetime import datetime, timedelta

def add_flights(flight_data_list):
    for data in flight_data_list:
        departure_airport = models.Airports.objects.get(code=data['departure_airport_code'])
        arrival_airport = models.Airports.objects.get(code=data['arrival_airport_code'])
        departure_time = datetime.strptime(data['departure_time'], '%Y-%m-%d %H:%M:%S')
        arrival_time = datetime.strptime(data['arrival_time'], '%Y-%m-%d %H:%M:%S')
        duration = arrival_time - departure_time
        flight = models.FlightInfo.objects.create(
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
add_flights(flight_data_list)
from django.db import models


class Bookings (models.Model):
  id = models.IntegerField(primary_key=True)
  # list of passenger types/ ids, make string
  passenger_ids = models.CharField(max_length=1000) 
  email = models.EmailField()
  transaction_id = models.CharField(unique=True, max_length=30)
  number_tickets = models.IntegerField()
  # list of seat codes, make string
  seat_codes = models.CharField(max_length=1000)
  total_price = models.DecimalField(decimal_places=2, max_digits=100)
  cancelled = models.BooleanField()
  # added by me: (consider)
  # passengers = models.ManyToManyField(PassengerSeatInfo)

class PassengerSeatInfo(models.Model):
  id = models.CharField(primary_key=True, max_length=30)
  first_name = models.CharField(max_length=50)
  surname = models.CharField(max_length=50)
  seat_classes = [('first', 'First Class'), ('business', 'Business Class'), ('economy', 'Economy Class')]
  seat_class = models.CharField(choices=seat_classes, max_length=30)
  price = models.DecimalField(decimal_places=2, max_digits=10)
  # Child or adult
  passenger_types = [('first', 'First Class'), ('business', 'Business Class')]
  passenger_type = models.CharField(max_length=30, choices=passenger_types)
  reserved = models.BooleanField()
  # added by me, used to be booking_id = models.IntegerField()
  booking_id = models.ForeignKey(Bookings, on_delete=models.CASCADE)
  def __str__(self):
    return '%s %s %s %s' % (self.first_name, self.surname, self.seat_class, self.passenger_type)

class FlightInfo(models.Model):
  id = models.CharField(primary_key=True, max_length=30)
  flight_number = models.CharField(max_length=30)
  flight_price = models.DecimalField(decimal_places=2, max_digits=10)
  # list of available seats, make JSON string seatname:taken?(0 = no, 1 = yes)
  seat_list = models.CharField(max_length=5000)
  departure_airport = models.CharField(max_length=100)
  destination_airport = models.CharField(max_length=100)
  arrival_date = models.DateTimeField()
  departure_date = models.DateTimeField()
  def __str__(self):
    return '%s %s %s %s %s' % (self.flight_number, str(self.departure_date), str(self.arrival_date),self.departure_airport, self.destination_airport)

class Airports(models.Model):
  id = models.CharField(primary_key=True, max_length=30)
  code = models.CharField(max_length=30)
  city = models.CharField(max_length=30)
  country = models.CharField(max_length=30)
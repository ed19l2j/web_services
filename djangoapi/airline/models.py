# To tell django this is the models class we must inherit from a class
from django.db import models


class Country(models.Model):
    country_name = models.CharField(max_length = 100)
    continent = models.CharField(max_length = 100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    def __str__(self):
        return self.country_name


class BookingInstance(models.Model):
    booked_at_time = models.DateTimeField()
    lead_passenger_contact_email = models.CharField(max_length = 50)
    lead_passenger_contact_number = models.CharField(max_length = 50)
    total_booking_cost = models.FloatField()
    payment_confirmed = models.BooleanField(default=False)
    transaction_id = models.IntegerField(blank=True)
    def __str__(self):
        return "Booking: " + str(self.id)


class Plane(models.Model):
    max_capacity = models.IntegerField()
    max_flight_distance = models.IntegerField()
    def __str__(self):
        return str(self.max_flight_distance)


class FlightInstance(models.Model):
    plane_id = models.ForeignKey(Plane, on_delete=models.PROTECT)
    flight_ticket_cost = models.FloatField()
    departure_country = models.ForeignKey(Country, on_delete=models.PROTECT)
    arrival_country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='%(class)s_requests_created')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    departure_day = models.DateField()
    num_available_seats = models.IntegerField()
    airline_name = "Lewis's Airline"
    def __str__(self):
        return self.departure_country.country_name + " to " + self.arrival_country.country_name


class SeatInstance(models.Model):
    seat_name = models.CharField(max_length = 50)
    available = models.BooleanField()
    flight_id = models.ForeignKey(FlightInstance, on_delete=models.PROTECT)
    def __str__(self):
        return self.flight_id.departure_country.country_name + " to " + self.flight_id.arrival_country.country_name + " " + str(self.flight_id.id) + " seat " + self.seat_name


class Passenger(models.Model):
    booking_id = models.ForeignKey(BookingInstance, on_delete=models.CASCADE)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    date_of_birth = models.DateField()
    nationality_country = models.ForeignKey(Country, on_delete=models.PROTECT)
    passport_number = models.CharField(max_length = 50)
    seat_id  = models.ForeignKey(SeatInstance, on_delete=models.PROTECT)
    def __str__(self):
        return self.first_name + " " + self.last_name

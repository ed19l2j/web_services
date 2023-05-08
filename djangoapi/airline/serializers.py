from rest_framework import serializers
from .models import Country, FlightInstance, SeatInstance, BookingInstance, Passenger


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "country_name", "continent", "latitude", "longitude"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightInstance
        fields = ["id", "plane_id", "flight_ticket_cost", "departure_country", "arrival_country", "departure_time", "arrival_time", "num_available_seats", "airline_name"]


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatInstance
        fields = ["id", "seat_name", "available", "flight_id"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingInstance
        fields = ["id", "booked_at_time", "lead_passenger_contact_email", "lead_passenger_contact_number", "total_booking_cost", "payment_confirmed", "transaction_id"]


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ["id", "booking_id", "first_name", "last_name", "date_of_birth", "nationality_country", "passport_number", "seat_id"]

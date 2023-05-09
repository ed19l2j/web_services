# Create the endpoints in here
from django.http import JsonResponse
from .models import Country, FlightInstance, SeatInstance, BookingInstance
from .serializers import CountrySerializer, FlightSerializer, SeatSerializer, BookingSerializer, PassengerSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import csv
import os
import datetime


locToId = {}
try:
	with open('countries.csv', mode='r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		i = 0
		for line in reader:
			if i != 0:
				country = {line[0] : i}
				locToId.update(country)
			i+=1
except:
	pass


try:
	with open('/home/iewiis/web_services/djangoapi/countries.csv', mode='r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		i = 0
		for line in reader:
			if i != 0:
				country = {line[0] : i}
				locToId.update(country)
			i+=1
except:
	pass

@api_view(["GET"])
def query_flights(request):
	if request.method == "GET":
		departure_country = request.GET.get("departure_country")
		arrival_country = request.GET.get("arrival_country")
		departure_date = request.GET.get("departure_date")
		max_price = request.GET.get("max_price")
		num_passengers = request.GET.get("num_passengers")
		if max_price != None:
			try:
				flights = FlightInstance.objects.filter(departure_country=locToId[departure_country], arrival_country=locToId[arrival_country], departure_day=departure_date, flight_ticket_cost__lte=max_price, num_available_seats__gte=num_passengers)
			except FlightInstance.DoesNotExist:
				return Response(status=status.HTTP_404_NOT_FOUND)
		else:
			try:
				flights = FlightInstance.objects.filter(departure_country=locToId[departure_country], arrival_country=locToId[arrival_country], departure_day=departure_date, num_available_seats__gte=num_passengers)
			except FlightInstance.DoesNotExist:
				return Response(status=status.HTTP_404_NOT_FOUND)

		serializer = FlightSerializer(flights, many=True)
		serialized_data = serializer.data
		serialized_data[0]['departure_country'] = departure_country
		serialized_data[0]['arrival_country'] = arrival_country
		# serialized_data.departure_country = departure_country
		return Response(serialized_data, status=status.HTTP_200_OK)
	return Response(status=status.HTTP_200_OK)


@api_view(["GET", "PUT"])
def query_seats(request, format=None):
	if request.method == "GET":
		flight_id = request.GET.get("flight_id")
		try:
			seats = SeatInstance.objects.filter(flight_id=flight_id)
		except SeatInstance.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)
		serializer = SeatSerializer(seats, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
	elif request.method == "PUT":
		flight_id = request.GET.get("flight_id")
		seat_name = request.GET.get("seat_name")
		try:
			seats = SeatInstance.objects.filter(flight_id=flight_id, available=True, seat_name=seat_name).first()
		except SeatInstance.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)
		serializer = SeatSerializer(seats, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# {
#     "flight_id": 1,
#     "lead_passenger_contact_email": "testingtesting@hello.com",
#     "lead_passenger_contact_number": "999",
#     "passengers": [{"passenger": "1"}]
# }
@api_view(["POST"])
def add_booking(request, format=None):
	if request.method == "POST":
		request.data["booked_at_time"] = datetime.datetime.now()
		flight_id = request.data["flight_id"]
		flight = FlightInstance.objects.get(pk=flight_id)
		request.data["total_booking_cost"] = flight.flight_ticket_cost
		request.data["payment_confirmed"] = False
		request.data["transaction_id"] = 0
		booking_serializer = BookingSerializer(data=request.data)
		if booking_serializer.is_valid():
		    booking = booking_serializer.save()
		    booking_id = booking.id
		passengers = request.data["passengers"]
		for passenger in passengers:
			request.data["booking_id"] = booking_id
			request.data["first_name"] = passenger["first_name"]
			request.data["last_name"] = passenger["last_name"]
			request.data["date_of_birth"] = passenger["date_of_birth"]
			country = Country.objects.get(country_name = passenger["nationality_country"])
			request.data["nationality_country"] = country.id
			request.data["passport_number"] = passenger["passport_number"]
			seat = SeatInstance.objects.get(flight_id = flight_id, seat_name=passenger["seat_name"])
			request.data["seat_id"] = seat.id
			passenger_serializer = PassengerSerializer(data=request.data)
			if passenger_serializer.is_valid():
				passenger_serializer.save()
				seat.available = False
				seat.save()
				flight.num_available_seats = flight.num_available_seats - 1
				flight.save()
		return Response(booking_serializer.data, status=status.HTTP_200_OK)
	return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_booking_details(request, format=None):
	if request.method == "GET":
		booking_id = request.GET.get("booking_id")
		lead_passenger_contact_email = request.GET.get("lead_passenger_contact_email")
		booking = BookingInstance.objects.get(id = booking_id, lead_passenger_contact_email = lead_passenger_contact_email)
		request.data["booked_at_time"] = booking.booked_at_time
		request.data["lead_passenger_contact_email"] = booking.lead_passenger_contact_email
		request.data["lead_passenger_contact_number"] = booking.lead_passenger_contact_number
		request.data["total_booking_cost"] = booking.total_booking_cost
		booking_serializer = BookingSerializer(booking, data=request.data)
		if booking_serializer.is_valid():
			return Response(booking_serializer.data, status=status.HTTP_200_OK)
		return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	return Response(status=status.HTTP_400_BAD_REQUEST)

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
		return Response(serializer.data, status=status.HTTP_200_OK)
	return Response(status=status.HTTP_200_OK)


@api_view(["GET", "PUT"])
def query_seats(request, format=None):
	if request.method == "GET":
		flight_ID = request.GET.get("flight_ID")
		try:
			seats = SeatInstance.objects.filter(flight_ID=flight_ID)
		except SeatInstance.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)
		serializer = SeatSerializer(seats, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
	elif request.method == "PUT":
		flight_ID = request.GET.get("flight_ID")
		seat_name = request.GET.get("seat_name")
		try:
			seats = SeatInstance.objects.filter(flight_ID=flight_ID, available=True, seat_name=seat_name).first()
		except SeatInstance.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)
		serializer = SeatSerializer(seats, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# {
#     "flight_ID": 1,
#     "lead_passenger_contact_email": "testingtesting@hello.com",
#     "lead_passenger_contact_number": "999",
#     "passengers": [{"passenger": "1"}]
# }
@api_view(["POST"])
def add_booking(request, format=None):
	if request.method == "POST":
		request.data["booked_at_time"] = datetime.datetime.now()
		flight_ID = request.data["flight_ID"]
		flight = FlightInstance.objects.get(pk=flight_ID)
		request.data["total_booking_cost"] = flight.flight_ticket_cost
		request.data["payment_confirmed"] = False
		request.data["transaction_ID"] = 0
		booking_serializer = BookingSerializer(data=request.data)
		if booking_serializer.is_valid():
		    booking = booking_serializer.save()
		    booking_ID = booking.id
		passengers = request.data["passengers"]
		print("here1")
		for passenger in passengers:
			print("here2")
			request.data["booking_ID"] = booking_ID
			request.data["first_name"] = passenger["first_name"]
			request.data["last_name"] = passenger["last_name"]
			request.data["date_of_birth"] = passenger["date_of_birth"]
			country = Country.objects.get(country_name = passenger["nationality_country"])
			request.data["nationality_country"] = country.id
			request.data["passport_number"] = passenger["passport_number"]
			seat = SeatInstance.objects.get(flight_ID = flight_ID, seat_name=passenger["seat_number"])
			request.data["seat_ID"] = seat.id
			passenger_serializer = PassengerSerializer(data=request.data)
			print(passenger_serializer)
			if passenger_serializer.is_valid():
				passenger_serializer.save()
				print("here3")
			else:
				print(passenger_serializer.errors)
		return Response(booking_serializer.data, status=status.HTTP_200_OK)
	return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_passenger(request, format=None):
	if request.method == "POST":
		# booking_ID = request.GET.get("booking_ID")
		# first_name = request.GET.get("first_name")
		# last_name = request.GET.get("last_name")
		# date_of_birth = request.GET.get("date_of_birth")
		# nationality_country_ID = request.GET.get("nationality_country_ID")
		# passport_num = request.GET.get("passport_num")
		# seat_ID = request.GET.get("seat_ID")
		serializer = PassengerSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

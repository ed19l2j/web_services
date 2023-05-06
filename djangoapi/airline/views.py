# Create the endpoints in here
from django.http import JsonResponse
from .models import Country, FlightInstance, SeatInstance, BookingInstance
from .serializers import CountrySerializer, FlightSerializer, SeatSerializer, BookingSerializer, PassengerSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import csv
import os


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
	print("error")


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
	print("error")

@api_view(["GET"])
def query_flights(request):
	if request.method == "GET":
		departure_country = request.GET.get("departure_country")
		arrival_country = request.GET.get("arrival_country")
		arrival_date = request.GET.get("arrival_date")
		max_price = request.GET.get("max_price")
		num_passengers = request.GET.get("num_passengers")
		if max_price != "0":
			try:
				flights = FlightInstance.objects.filter(departure_location_ID=locToId[departure_country], arrival_location_ID=locToId[arrival_country], arrival_day=arrival_date, flight_ticket_cost__lte=max_price, num_available_seats__gte=num_passengers)
			except FlightInstance.DoesNotExist:
				return Response(status=status.HTTP_404_NOT_FOUND)
		else:
			try:
				flights = FlightInstance.objects.filter(departure_location_ID=locToId[departure_country], arrival_location_ID=locToId[arrival_country], arrival_day=arrival_date, num_available_seats__gte=num_passengers)
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
			seats = SeatInstance.objects.filter(flight_ID=flight_ID, available=True)
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


@api_view(["POST"])
def add_booking(request, format=None):
	if request.method == "POST":
		booked_at_time = request.GET.get("booked_at_time")
		lead_passenger_contact_email = request.GET.get("lead_passenger_contact_email")
		lead_passenger_contact_number = request.GET.get("lead_passenger_contact_number")
		total_booking_cost = request.GET.get("total_booking_cost")
		payment_confirmed = False
		transaction_ID = None
		serializer = BookingSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_passenger(request, format=None):
	if request.method == "POST":
		booking_ID = request.GET.get("booking_ID")
		first_name = request.GET.get("first_name")
		last_name = request.GET.get("last_name")
		date_of_birth = request.GET.get("date_of_birth")
		nationality_country_ID = request.GET.get("nationality_country_ID")
		passport_num = request.GET.get("passport_num")
		seat_ID = request.GET.get("seat_ID")

		serializer = PassengerSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

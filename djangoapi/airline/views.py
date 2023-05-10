# Create the endpoints in here
from django.http import JsonResponse
from .models import Country, FlightInstance, SeatInstance, BookingInstance, Passenger
from .serializers import CountrySerializer, FlightSerializer, SeatSerializer, BookingSerializer, PassengerSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import csv
import os
import datetime
import requests
import json

airline_account_number = "20202020"
airline_card_number_hash = "0a08c389d1e7ec3e1d13a74f46e1aae2b020d607316e4b818f378dc62d2c4d90477371fd034799c374ff8699b63a6f69"
airline_cvc_hash = "99e0a589f8889faee97a49bc43e3ec1faf735413c39fffd20d2f261fb019bbf8d3b3e07f203088aa50ee279fc24d7ce3"
airline_sortcode = "373891"
airline_expiry_date = "0724"
airline_cardholder_name = "Lewis Jackson"


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


@api_view(["GET"])
def query_seats(request, format=None):
	if request.method == "GET":
		flight_id = request.GET.get("flight_id")
		try:
			seats = SeatInstance.objects.filter(flight_id=flight_id)
		except SeatInstance.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)
		serializer = SeatSerializer(seats, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_seats(request, format=None):
	if request.method == "PUT":
		booking_id = request.data["booking_id"]
		new_seat_name = request.data["seat_name"]
		first_name = request.data["first_name"]
		last_name = request.data["last_name"]
		passenger = Passenger.objects.get(booking_id=booking_id, first_name=first_name, last_name=last_name)
		seat = SeatInstance.objects.get(id=passenger.seat_id.id)
		seat.available = True
		seat.save()
		new_seat = SeatInstance.objects.get(flight_id=seat.flight_id, seat_name=new_seat_name)
		print(new_seat)
		passenger.seat_id = new_seat
		passenger.save()
		new_seat.available = False
		new_seat.save()
		return Response(status=status.HTTP_200_OK)
	return Response(status=status.HTTP_400_BAD_REQUEST)


# {
#     "flight_id": 1,
#     "lead_passenger_contact_email": "testingtesting@hello.com",
#     "lead_passenger_contact_number": "999",
#     "passengers": [
#     {
#         "first_name": "Lewis",
#         "last_name": "Jackson",
#         "date_of_birth": "2002-05-22",
#         "nationality_country": "Poland",
#         "passport_number": "02910831083",
#         "seat_name": "A9"
#     }],
#     "payment_details":
#     {
#         "cardholder_name": "Mr Bean",
#         "card_number": "0b8c6e90f39582d09db07e483f8f1f44538003bbb95403d3e4037734c012e1cc069c1bbe9bfa746498d1fe712fd66766",
#         "cvc": "f100da566d3b762ff476ea194b7519b1bc5fc67cb3adf6837b91716c69dccc2c8dc490c9c04be39cc6f2fbe6a14b8903",
#         "sortcode": "373891",
#         "expiry_date": "2406"
#     }
# }
@api_view(["POST"])
def add_booking(request, format=None):
	if request.method == "POST":
		sender_cardholder_name = request.data["payment_details"]["cardholder_name"]
		sender_card_hash = request.data["payment_details"]["card_number"]
		sender_cvc_hash = request.data["payment_details"]["cvc"]
		sender_sortcode = request.data["payment_details"]["sortcode"]
		sender_expiry_date = request.data["payment_details"]["expiry_date"]

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

		card_details = {
			"sender_cardholder_name":sender_cardholder_name,
			"sender_card_hash":sender_card_hash,
			"sender_cvc_hash":sender_cvc_hash,
			"sender_sortcode":sender_sortcode,
			"sender_expiry_date":sender_expiry_date,
			"recipient_cardholder_name":airline_cardholder_name,
			"recipient_sortcode":airline_sortcode,
			"recipient_account_number":airline_account_number,
			"payment_amount":"100.00"
		}

		response = requests.post("https://sc20jzl.pythonanywhere.com/pay/", json=card_details)
		jsonresponse = json.loads(response.text)
		print(response.status_code)
		print(response.text)
		if response.status_code == 200:
			booking.transaction_id = jsonresponse["transaction_id"]
			booking.payment_confirmed = True
			booking.save()
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
		passenger = Passenger.objects.filter(booking_id=booking.id).first()
		seat = SeatInstance.objects.get(id=passenger.seat_id.id)
		# request.data["flight_id"] = seat.flight_id
		# request.data["num_passengers"] = len(Passenger.objects.filter(booking_id=booking.id))
		booking_serializer = BookingSerializer(booking, request.data)
		if booking_serializer.is_valid():
			serialized_data = booking_serializer.data
			print(serialized_data)
			serialized_data["num_passengers"] = len(Passenger.objects.filter(booking_id=booking.id))
			serialized_data["flight_id"] = seat.flight_id.id
			return Response(serialized_data, status=status.HTTP_200_OK)
	return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_booking(request, format=None):
	if request.method == "DELETE":
		#find booking
		#find passengers
		#make the seats available again
		#refund the booking account using transaction_id
		#delete the booking
		#make sure its also deleted the passengers
		booking_id = request.data["booking_id"]
		booking = BookingInstance.objects.get(id = booking_id)
		######
		passengers = Passenger.objects.filter(booking_id=booking_id)
		######
		for passenger in passengers:
			seat = SeatInstance.objects.get(id=passenger.seat_id.id)
			seat.available=True
			seat.save()
		######
		transaction_id = request.data["transaction_id"]
		get_data = {"transaction_id":transaction_id}
		response = requests.post("https://sc20jzl.pythonanywhere.com/get_transaction_details/", json=get_data)
		print(response.text)
		jsonresponse = json.loads(response.text)
		recipient_account_number = jsonresponse["sender_account_number"]
		recipient_sortcode = jsonresponse["sender_sortcode"]
		#recipient_cardholder_name = "John Smith" # ???????????
		payment_amount = jsonresponse["payment_amount"]
		card_details = {
			"sender_cardholder_name":airline_cardholder_name,
			"sender_card_hash":airline_card_number_hash,
			"sender_cvc_hash":airline_cvc_hash,
			"sender_sortcode":airline_sortcode,
			"sender_expiry_date":airline_expiry_date,
			#"recipient_cardholder_name":recipient_cardholder_name, #??????????? how do i get this
			"recipient_sortcode":recipient_sortcode,
			"recipient_account_number":recipient_account_number,
			"payment_amount":"100.00"
		}
		#response = requests.post("https://sc20jzl.pythonanywhere.com/pay/", json=card_details)
		######
		#booking.delete()

	return Response(status=status.HTTP_200_OK)

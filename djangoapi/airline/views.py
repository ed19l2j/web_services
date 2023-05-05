# Create the endpoints in here
from django.http import JsonResponse
from .models import Country, FlightInstance, SeatInstance, BookingInstance
from .serializers import CountrySerializer, FlightSerializer, SeatSerializer, BookingSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


locToId = {
    "England" : 1,
    "USA" : 3
}


#
# @api_view(["GET", "POST"])
# def country_list(request, format=None):
#     if request.method == "GET":
#         countries = Country.objects.all()
#         serializer = CountrySerializer(countries, many=True)
#         return Response(serializer.data)
#     # if request.method == "POST":
#     #     serializer = CountrySerializer(data=request.data)
#     #     if serializer.is_valid():
#     #         serializer.save()
#     #         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# @api_view(["GET", "PUT", "DELETE"])
# def country_detail(request, id, format=None):
#     try:
#         country = Country.objects.get(pk=id)
#     except Country.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == "GET":
#         serializer = CountrySerializer(country)
#         return Response(serializer.data)
#     elif request.method == "PUT":
#         serializer = CountrySerializer(country, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == "DELETE":
#         country.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# @api_view(["GET"])
# def flight_list(request, format=None):
#     if request.method == "GET":
#         flights = FlightInstance.objects.all()
#         serializer = FlightSerializer(flights, many=True)
#         return Response(serializer.data)
#     return Response(status=status.HTTP_404_NOT_FOUND)
#
#
# @api_view(["GET", "PUT"])
# def seat_detail(request, id, format=None):
#     try:
#         seats = SeatInstance.objects.filter(flight_ID=id)
#     except SeatInstance.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == "GET":
#         serializer = SeatSerializer(seats, many=True)
#         return Response(serializer.data)
#     elif request.method == "PUT":
#         serializer = SeatSerializer(seats, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def query_flights(request):
    if request.method == "GET":
        departure_country = request.GET.get("departure_country")
        arrival_country = request.GET.get("arrival_country")
        arrival_date = request.GET.get("arrival_date")
        max_price = request.GET.get("max_price")
        num_passengers = request.GET.get("num_passengers")

        if max_price != 0:
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
        return Response(serializer.data)
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
        return Response(serializer.data)
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
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
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
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "GET":
        try:
            bookings = BookingInstance.objects.all()
        except BookingInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

import csv
import os
import random
import time
import datetime
from .models import Country, FlightInstance, Plane, SeatInstance
import geopy.distance
import math


def PopulateCountries():
    i = 0
    for line in csv.reader(open('countries.csv'), delimiter=',', quotechar='"'):
        if i != 0:
            country = Country()
            country.country_name = line[0]
            country.continent = line[1]
            country.latitude = line[2]
            country.longitude = line[3]
            try:
                country.save()
            except Exception as e:
                print("Error saving country: " + country.country_name + " exception: " + str(e) + "\n")
        i+=1

def PopulatePlanes():
	max_capacity_list = [18,30,60,75,90,144]
	max_distance_list = [300,750,1500,3200,5000,11000]
	i = 0
	for plane in range(6):
		plane = Plane()
		plane.max_capacity = max_capacity_list[i]
		plane.max_flight_distance = max_distance_list[i]
		try:
			plane.save()
		except Exception as e:
			print("Error saving plane: " + str(Plane.max_flight_distance) + " exception: " + str(e) + "\n")
		i += 1

def str_time_prop(start, end, time_format, prop):
	"""Get a time at a proportion of a range of two formatted times.

	start and end should be strings specifying times formatted in the
	given format (strftime-style), giving an interval [start, end].
	prop specifies how a proportion of the interval to be taken after
	start.  The returned time will be in the specified format.
	"""

	stime = time.mktime(time.strptime(start, time_format))
	etime = time.mktime(time.strptime(end, time_format))
	ptime = stime + prop * (etime - stime)

	length_of_flight = random.randint(60,720)
	later_time = ptime + 60*length_of_flight
	return time.strftime(time_format, time.localtime(ptime)), time.strftime(time_format, time.localtime(later_time)), later_time


def random_date(start, end, prop):
	return str_time_prop(start, end, "%Y-%m-%d %H:%M:%S", prop)


def PopulateFlights():
	for flight in range(10):
		flight = FlightInstance()
		dep=random.randint(1,196)
		arr=random.randint(1,196)
		if dep != arr:
			flight.departure_country = Country.objects.get(id=dep)# randomint between 1-196
			flight.arrival_country = Country.objects.get(id=arr)# randomint between 1-196
			# make sure they arent the same
			flight.flight_ticket_cost = 200# random int between 50-500
			coords_1 = (flight.departure_country.latitude, flight.departure_country.longitude)
			coords_2 = (flight.arrival_country.latitude, flight.arrival_country.longitude)
			distance_between_countries = geopy.distance.geodesic(coords_1, coords_2).miles
			if distance_between_countries <= 300:
				flight.plane_id = Plane.objects.get(id=1)
			elif distance_between_countries <= 750:
				flight.plane_id = Plane.objects.get(id=2)
			elif distance_between_countries <= 1500:
				flight.plane_id = Plane.objects.get(id=3)
			elif distance_between_countries <= 3200:
				flight.plane_id = Plane.objects.get(id=4)
			elif distance_between_countries <= 5000:
				flight.plane_id = Plane.objects.get(id=5)
			else:
				flight.plane_id = Plane.objects.get(id=6)
			flight.num_available_seats = flight.plane_id.max_capacity
			flight.departure_time, flight.arrival_time, later_time = random_date("2023-07-05 01:01:01", "2023-12-31 01:01:01", random.random())
			utc_struct_time = time.gmtime(later_time)
			dt = datetime.datetime.fromtimestamp(time.mktime(utc_struct_time))
			flight.departure_day = dt
			flight.airline_name = "Lewis's Airline"
			try:
				flight.save()
			except Exception as e:
				print("Error saving flight: " + str(Country.country_name) + " exception: " + str(e) + "\n")

columns = ["A", "B", "C", "D", "E", "F"]
def PopulateSeats():
	all_flights = FlightInstance.objects.all()
	for flight in all_flights:
		column = 0
		row = 1
		for seat in range(flight.num_available_seats):
			new_seat = SeatInstance()
			new_seat.seat_name = columns[column] + str(math.floor((row-1)/6) + 1)
			new_seat.available = True
			new_seat.flight_id = flight
			column += 1
			row += 1
			if column > 5:
				column = 0
			try:
				new_seat.save()
			except Exception as e:
				print("Error saving seat: " + str(SeatInstance.seat_name) + " exception: " + str(e) + "\n")


if __name__ == '__main__':
	print("Populated the database with countries.")

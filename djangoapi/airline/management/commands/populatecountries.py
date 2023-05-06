from django.core.management.base import BaseCommand
from airline.populate_db import PopulateCountries, PopulateFlights, PopulatePlanes, PopulateSeats

class Command(BaseCommand):
	help = 'Populates the database'

	def handle(self, *args, **options):
		 PopulateCountries()
		 PopulatePlanes()
		 PopulateFlights()
		 PopulateSeats()

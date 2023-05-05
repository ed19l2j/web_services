# This admin site is not necessary but is useful in debugging etc
from django.contrib import admin
# Have to import each model so it shows up on the admin website
from .models import Country, BookingInstance, Plane, FlightInstance, SeatInstance, Passenger

admin.site.register(Country)
admin.site.register(BookingInstance)
admin.site.register(Plane)
admin.site.register(FlightInstance)
admin.site.register(SeatInstance)
admin.site.register(Passenger)

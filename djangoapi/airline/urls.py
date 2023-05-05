"""airline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from airline import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("countries/", views.country_list),
    # path("countries/<int:id>", views.country_detail),
    # path("seats/<int:id>", views.seat_detail),
    # path("flights/", views.flight_list),
    path("flights/", views.query_flights),
    path("seats/", views.query_seats),
    path("bookings/", views.add_booking),

]

urlpatterns = format_suffix_patterns(urlpatterns)

from django.shortcuts import render
from .models import City, TurnSystem
from citizen_engine.models import Citizen
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse


def main_view(request, city_id):
    city = City.objects.get(id=city_id)
    citizens_number = Citizen.objects.filter(city_id=city_id).count()
    turns = TurnSystem.objects.get(city_id=city_id)
    return render(request, 'main_view.html', {'city': city,
                                              'citizen_number': citizens_number,
                                              'turns': turns})


def turn_calculations(request, city_id):
    return HttpResponseRedirect(reverse('city_engine:main_view', args=(city_id,)))


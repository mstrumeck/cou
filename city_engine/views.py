from django.shortcuts import render
from .models import City, TurnSystem, Residential
from citizen_engine.models import Citizen
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Sum


def main_view(request, city_id):
    city = City.objects.get(id=city_id)
    population = Citizen.objects.filter(city_id=city_id).count()
    max_population = Residential.objects.filter(city_id=city_id).aggregate(Sum('max_population'))['max_population__sum']
    house_number = Residential.objects.filter(city_id=city_id).count()
    turns = TurnSystem.objects.get(city_id=city_id)
    income = Citizen.objects.filter(city_id=city_id).aggregate(Sum('income'))['income__sum']
    return render(request, 'main_view.html', {'city': city,
                                              'population': population,
                                              'max_population': max_population,
                                              'turns': turns,
                                              'house_number': house_number,
                                              'income': income})


def turn_calculations(request, city_id):
    turns = TurnSystem.objects.get(city_id=city_id)
    turns.current_turn += 1
    turns.save()
    return HttpResponseRedirect(reverse('city_engine:main_view', args=(city_id,)))


from django.shortcuts import render
from .models import City, Residential, ProductionBuilding, CityField, PowerPlant
from player.models import Profile
from django.contrib.auth.models import User
from citizen_engine.models import Citizen
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .board import hex_table, hex_detail_info_table, HEX_NUM, hex_with_builds
from django.utils.safestring import mark_safe


@login_required
def main_view(request):
    max_population = 0
    current_population = 0
    user = User.objects.get(id=request.user.id)
    city_id = City.objects.get(user_id=user.id).id
    city = City.objects.get(id=city_id)
    profile = Profile.objects.get(user_id=request.user.id)
    # population = Citizen.objects.filter(city_id=city_id).count()
    income = Citizen.objects.filter(city_id=city_id).aggregate(Sum('income'))['income__sum']
    # max_population = Residential.objects.filter(city_id=city_id).aggregate(Sum('max_population'))['max_population__sum']
    for city_field in CityField.objects.filter(city_id=city_id):
        if city_field.if_residential is True:
            max_population += Residential.objects.get(city_field=city_field).max_population
            current_population += Residential.objects.get(city_field=city_field).current_population
    # house_number = Residential.objects.filter(city_id=city_id).count()
    return render(request, 'main_view.html', {'city': city,
                                              'profile': profile,
                                              # 'population': population,
                                              'current_population': current_population,
                                              'max_population': max_population,
                                              # 'house_number': house_number,
                                              'income': income,
                                              'hex_table': mark_safe(hex_table),
                                              'hex_detail_info_table': mark_safe(hex_detail_info_table),
                                              'HEX_NUM': range(HEX_NUM)})


def turn_calculations(request):
    return HttpResponseRedirect(reverse('city_engine:main_view'))


def build(request, hex_id):
    city = City.objects.get(user_id=request.user.id)
    city_field = CityField.objects.get(field_id=hex_id, city_id=city.id)
    city_field.if_electricity = True
    city_field.save()
    city_field.refresh_from_db()
    power_plant = PowerPlant()
    power_plant.max_employees = 20
    power_plant.name = 'Elektrownia wiatrowa'
    power_plant.current_employees = 0
    power_plant.production_level = 0
    power_plant.trash = 0
    power_plant.health = 0
    power_plant.energy = 0
    power_plant.water = 0
    power_plant.crime = 0
    power_plant.pollution = 0
    power_plant.recycling = 0
    power_plant.city_communication = 0
    power_plant.build_time = 3
    power_plant.power_nodes = 1
    power_plant.energy_production = 20
    power_plant.city_field = CityField.objects.get(field_id=hex_id)
    power_plant.save()
    power_plant.refresh_from_db()

    return HttpResponseRedirect(reverse('city_engine:main_view'))


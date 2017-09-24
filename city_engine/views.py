from django.shortcuts import render
from .models import City, Residential, ProductionBuilding, CityField, PowerPlant
from player.models import Profile
from django.contrib.auth.models import User
from citizen_engine.models import Citizen
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .board import generate_board, generate_hex_detail
from django.utils.safestring import mark_safe


@login_required
def main_view(request):
    generate_board()
    generate_hex_detail(request)

    max_population = 0
    current_population = 0
    energy = 0

    building_name = []
    building_cur = []
    building_end = []

    buildings_under_construction = zip(building_name, building_cur, building_end)
    user = User.objects.get(id=request.user.id)
    city_id = City.objects.get(user_id=user.id).id
    city = City.objects.get(id=city_id)
    profile = Profile.objects.get(user_id=request.user.id)
    income = Citizen.objects.filter(city_id=city_id).aggregate(Sum('income'))['income__sum']

    for city_field in CityField.objects.filter(city_id=city_id):
        if city_field.if_residential is True:
            max_population += Residential.objects.get(city_field=city_field).max_population
            current_population += Residential.objects.get(city_field=city_field).current_population
        elif city_field.if_electricity is True:
            energy += PowerPlant.objects.get(city_field=city_field).total_energy_production()

    for buildings in Residential.objects.filter(city=city):
        if buildings.if_under_construction is True:
            building_name.append('Dom')
            building_cur.append(buildings.current_build_time)
            building_end.append(buildings.build_time)

    for buildings in ProductionBuilding.objects.filter(city=city):
        if buildings.if_under_construction is True:
            building_name.append('Fabryka')
            building_cur.append(buildings.current_build_time)
            building_end.append(buildings.build_time)

    for buildings in PowerPlant.objects.filter(city=city):
        if buildings.if_under_construction is True:
            building_name.append(buildings.name)
            building_cur.append(buildings.current_build_time)
            building_end.append(buildings.build_time)

    return render(request, 'main_view.html', {'city': city,
                                              'profile': profile,
                                              'income': income,
                                              'energy': energy,
                                              'hex_table': mark_safe(generate_board()),
                                              'hex_detail_info_table': mark_safe(generate_hex_detail(request)),
                                              'building_name': building_name,
                                              'buildings_under_construction': buildings_under_construction})


def turn_calculations(request):
    profile = Profile.objects.get(user_id=request.user.id)
    profile.current_turn += 1
    profile.save()

    city = City.objects.get(user_id=request.user.id)

    for buildings in Residential.objects.filter(city=city):
        buildings.build_status()

    for buildings in ProductionBuilding.objects.filter(city=city):
        buildings.build_status()

    for buildings in PowerPlant.objects.filter(city=city):
        buildings.build_status()

    return HttpResponseRedirect(reverse('city_engine:main_view'))


def build(request, hex_id):
    city = City.objects.get(user_id=request.user.id)
    city_field = CityField.objects.get(field_id=hex_id, city_id=city.id)
    city_field.if_electricity = True
    city_field.save()

    power_plant = PowerPlant()
    power_plant.name = 'Elektrownia wiatrowa'
    power_plant.city = city
    power_plant.build_time = 3
    power_plant.energy_production = 20
    power_plant.city_field = CityField.objects.get(field_id=hex_id, city=city)
    power_plant.save()

    generate_board()
    generate_hex_detail(request)

    return HttpResponseRedirect(reverse('city_engine:main_view'))


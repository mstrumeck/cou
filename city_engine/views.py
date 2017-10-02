from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
from .turn_data.main import \
    update_turn_status
from .main_view_data.main import \
    create_list_of_buildings_under_construction, \
    calculate_max_population, \
    calculate_energy_production, \
    calculate_current_population
from citizen_engine.models import Citizen
from city_engine.main_view_data.board import generate_board, generate_hex_detail
from player.models import Profile
from .models import City, Residential, ProductionBuilding, CityField, PowerPlant


@login_required
def main_view(request):
    user = User.objects.get(id=request.user.id)
    city_id = City.objects.get(user_id=user.id).id
    city = City.objects.get(id=city_id)
    profile = Profile.objects.get(user_id=request.user.id)
    income = Citizen.objects.filter(city_id=city_id).aggregate(Sum('income'))['income__sum']

    generate_board()
    generate_hex_detail(request)

    max_population = calculate_max_population(city=city)
    current_population = calculate_current_population(city=city)
    energy = calculate_energy_production(city=city)

    buildings_under_construction = create_list_of_buildings_under_construction(city)

    return render(request, 'main_view.html', {'city': city,
                                              'profile': profile,
                                              'income': income,
                                              'energy': energy,
                                              'hex_table': mark_safe(generate_board()),
                                              'hex_detail_info_table': mark_safe(generate_hex_detail(request)),
                                              'buildings_under_construction': buildings_under_construction})


def turn_calculations(request):
    profile = Profile.objects.get(user_id=request.user.id)
    profile.current_turn += 1
    profile.save()

    city = City.objects.get(user_id=request.user.id)
    update_turn_status(city)

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


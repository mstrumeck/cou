from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
from citizen_engine.models import Citizen
from city_engine.main_view_data.board import Board, HexDetail
from city_engine.models import City, list_of_models
from player.models import Profile
from .main_view_data.main import \
    create_list_of_buildings_under_construction, \
    calculate_max_population, \
    calculate_energy_production, calculate_water_production, calculate_energy_usage,\
    calculate_current_population, \
    create_list_of_buildings
from .turn_data.main import \
    update_build_status, \
    calculate_maintenance_cost
from .turn_data.build import build_building


@login_required
def main_view(request):
    user = User.objects.get(id=request.user.id)
    city = City.objects.get(user=user)
    profile = Profile.objects.get(user_id=request.user.id)
    income = Citizen.objects.filter(city=city).aggregate(Sum('income'))['income__sum']

    new_board = Board(request)
    new_hex_detail = HexDetail(request)

    max_population = calculate_max_population(city)
    current_population = calculate_current_population(city)
    City.energy_production = calculate_energy_production(city)
    City.energy_used = calculate_energy_usage(city)
    city_energy_bilans =  City.energy_production - City.energy_used

    City.water_production = calculate_water_production(city)

    buildings = create_list_of_buildings(city)
    buildings_under_construction = create_list_of_buildings_under_construction(city)

    total_cost_of_maintenance = calculate_maintenance_cost(list_of_models, city)

    return render(request, 'main_view.html', {'city': city,
                                              'profile': profile,
                                              'income': income,
                                              'energy': City.energy_production,
                                              'energy_bilans': city_energy_bilans,
                                              'water': City.water_production,
                                              'hex_table': mark_safe(new_board.hex_table),
                                              'hex_detail_info_table': mark_safe(new_hex_detail.hex_detail_info_table),
                                              'buildings': buildings,
                                              'buildings_under_construction': buildings_under_construction,
                                              'total_cost_of_maintenance': total_cost_of_maintenance})


@login_required
def turn_calculations(request):
    profile = Profile.objects.get(user_id=request.user.id)
    profile.current_turn += 1
    profile.save()

    city = City.objects.get(user_id=request.user.id)
    update_build_status(city)

    city.cash -= calculate_maintenance_cost(list_of_models, city)
    city.save()

    return HttpResponseRedirect(reverse('city_engine:main_view'))


@login_required
def build(request, hex_id, build_type):
    build_building(request, hex_id, build_type)
    return HttpResponseRedirect(reverse('city_engine:main_view'))


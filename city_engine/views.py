from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
from citizen_engine.models import Citizen
from city_engine.main_view_data.board import Board, HexDetail
from city_engine.models import City
from player.models import Profile
from .main_view_data.city_stats import \
    CityStatsCenter
from .turn_data.main import \
    TurnCalculation
from .turn_data.build import build_building
from django.db.models import F
from city_engine.abstract import RootClass


@login_required
def main_view(request):
    city = City.objects.get(user_id=request.user.id)
    data = RootClass(city)
    new_board = Board(city, data)
    new_hex_detail = HexDetail(city, data)
    city_stats = CityStatsCenter(city, data)
    city_resources_allocation_stats = zip(["Produkowana", "Ulokowana", "Bilans"],
                                          [city_stats.energy_production, city_stats.energy_allocation, city_stats.energy_bilans],
                                          [city_stats.water_production, city_stats.water_allocation, city_stats.water_bilans])

    profile = Profile.objects.get(user_id=request.user.id)
    income = Citizen.objects.filter(city=city).aggregate(Sum('income'))['income__sum']

    city.save()

    return render(request, 'main_view.html', {'city': city,
                                              'profile': profile,
                                              'income': income,
                                              'city_resources_stats': city_resources_allocation_stats,
                                              'hex_table': mark_safe(new_board.hex_table),
                                              'hex_detail_info_table': mark_safe(new_hex_detail.hex_detail_info_table),
                                              'buildings': city_stats.list_of_buildings,
                                              'buildings_under_construction': city_stats.building_under_construction,
                                              'total_cost_of_maintenance': TurnCalculation(city).calculate_maintenance_cost(),
                                              'current_population': city_stats.current_population,
                                              'max_population': city_stats.max_population})


@login_required
def turn_calculations(request):
    profile = Profile.objects.get(user_id=request.user.id)
    profile.current_turn = F('current_turn') + 1
    profile.save()

    city = City.objects.get(user_id=request.user.id)
    TurnCalculation(city).run()

    return HttpResponseRedirect(reverse('city_engine:main_view'))


@login_required
def build(request, row, col, build_type):
    build_building(request, row, col, build_type)
    return HttpResponseRedirect(reverse('city_engine:main_view'))

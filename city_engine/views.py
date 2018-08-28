from django.contrib.auth.decorators import login_required
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
from .turn_data.main import TurnCalculation
from .turn_data.build import build_building
from django.db.models import F
from cou.abstract import RootClass
from cou.abstract import ResourcesData


@login_required
def main_view(request):
    city = City.objects.get(user_id=request.user.id)
    data = RootClass(city, request.user)
    new_board = Board(city, data)
    new_hex_detail = HexDetail(city, data)
    city_stats = CityStatsCenter(city, data)
    city_resources_allocation_stats = zip(["Produkowana", "Ulokowana", "Bilans"],
                                          [city_stats.energy_production, city_stats.energy_allocation, city_stats.energy_bilans],
                                          [city_stats.clean_water_production, city_stats.clean_water_allocation, city_stats.clean_water_bilans],
                                          [city_stats.raw_water_production, city_stats.raw_water_allocation, city_stats.raw_water_bilans])

    profile = Profile.objects.get(user_id=request.user.id)
    total_cost_of_main = sum(b.maintenance_cost for b in data.list_of_buildings)

    city.save()

    return render(request, 'main_view.html', {'city': city,
                                              'profile': profile,
                                              'city_resources_stats': city_resources_allocation_stats,
                                              'hex_table': mark_safe(new_board.hex_table),
                                              'hex_detail_info_table': mark_safe(new_hex_detail.hex_detail_info_table),
                                              'buildings': city_stats.list_of_buildings,
                                              'buildings_under_construction': city_stats.building_under_construction,
                                              'total_cost_of_maintenance': total_cost_of_main,
                                              'current_population': city_stats.current_population,
                                              'max_population': city_stats.max_population,
                                              'home_demands': city_stats.building_stats.home_areas_demand(),
                                              'industial_demands': city_stats.building_stats.industrial_areas_demand(),
                                              'trade_demands': city_stats.building_stats.trade_areas_demand(),
                                              'citizen': Citizen.objects.all()})


@login_required
def resources_view(request):
    city = City.objects.get(user_id=request.user.id)
    rd = ResourcesData(city=city, user=request.user)
    resources = zip(rd.resources, rd.resources.values())
    return render(request, 'resources_view.html', {'city': city,
                                                   'resources': resources})


@login_required
def turn_calculations(request):

    city = City.objects.get(user_id=request.user.id)
    data = RootClass(city, request.user)
    profile = Profile.objects.get(user_id=request.user.id)
    TurnCalculation(city, data, profile).run()
    # return render(request, 'city_calculation_view.html')
    return HttpResponseRedirect(reverse('city_engine:main'))


@login_required
def build(request, row, col, build_type):
    build_building(request, row, col, build_type)
    return HttpResponseRedirect(reverse('city_engine:main'))

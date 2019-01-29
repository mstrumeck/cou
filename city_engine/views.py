from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from city_engine.main_view_data.board import Board, HexDetail
from city_engine.models import City, StandardLevelResidentialZone
from cou.abstract import AbstractAdapter
from cou.abstract import RootClass
from player.models import Message
from player.models import Profile
from .main_view_data.city_stats import CityStatsCenter
from .turn_data.build import build_building, build_resident_zone
from .turn_data.main import TurnCalculation


@login_required
def main_view(request):
    city = City.objects.get(user_id=request.user.id)
    rc = RootClass(city, request.user)
    new_board = Board(city, rc)
    new_hex_detail = HexDetail(city, rc)
    city_stats = CityStatsCenter(city, rc)
    city_resources_allocation_stats = zip(
        ["Produkowana", "Ulokowana", "Bilans"],
        [
            city_stats.energy_production,
            city_stats.energy_allocation,
            city_stats.energy_bilans,
        ],
        [
            city_stats.clean_water_production,
            city_stats.clean_water_allocation,
            city_stats.clean_water_bilans,
        ],
        [
            city_stats.raw_water_production,
            city_stats.raw_water_allocation,
            city_stats.raw_water_bilans,
        ],
    )

    profile = Profile.objects.get(user_id=request.user.id)
    total_cost_of_main = sum(b.maintenance_cost for b in rc.list_of_buildings)
    msg = Message.objects.filter(profile=profile, turn=profile.current_turn - 1).values(
        "text"
    )
    city.save()

    build_exception = [StandardLevelResidentialZone]
    list_of_buildings_class = [
        sub.__name__
        for sub in AbstractAdapter().get_subclasses_of_all_buildings()
        if sub not in build_exception
    ]

    return render(
        request,
        "main_view.html",
        {
            "city": city,
            "profile": profile,
            "city_resources_stats": city_resources_allocation_stats,
            "hex_table": mark_safe(new_board.hex_table),
            "hex_detail_info_table": mark_safe(new_hex_detail.hex_detail_info_table),
            "buildings": (
                rc.list_of_buildings[b]
                for b in rc.list_of_buildings
                if b.if_under_construction == False
            ),
            "buildings_under_construction": city_stats.building_under_construction,
            "total_cost_of_maintenance": total_cost_of_main,
            "current_population": city_stats.current_population,
            "max_population": city_stats.max_population,
            "home_demands": city_stats.building_stats.home_areas_demand(),
            "industial_demands": city_stats.building_stats.industrial_areas_demand(),
            "trade_demands": city_stats.building_stats.trade_areas_demand(),
            "citizen": (rc.citizens_in_city[c] for c in rc.citizens_in_city),
            "msg": msg,
            "list_of_buildings_class": list_of_buildings_class,
            "families": (rc.families[f] for f in rc.families),
        },
    )


@login_required
def resources_view(request):
    city = City.objects.get(user_id=request.user.id)
    rc = RootClass(city, request.user)
    market_resources = rc.market.resources.items()
    companies_goods = {c: rc.companies[c].goods.items() for c in rc.companies}.items()
    return render(
        request,
        "resources_view.html",
        {
            "city": city,
            "market_resources": market_resources,
            "companies_goods": companies_goods,
        },
    )


@login_required
def turn_calculations(request):
    city = City.objects.get(user_id=request.user.id)
    data = RootClass(city, request.user)
    profile = Profile.objects.get(user_id=request.user.id)
    TurnCalculation(city, data, profile).run()
    # return render(request, 'city_calculation_view.html')
    return HttpResponseRedirect(reverse("city_engine:main"))


@login_required
def build(request, row, col, build_type):
    build_building(request, row, col, build_type)
    return HttpResponseRedirect(reverse("city_engine:main"))


@login_required
def build_resident(request, row, col, max_population):
    build_resident_zone(request, row, col, max_population)
    return HttpResponseRedirect(reverse("city_engine:main"))

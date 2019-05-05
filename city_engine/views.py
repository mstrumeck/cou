from django.contrib.auth.decorators import login_required
# from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from city_engine.main_view_data.board import Board, HexDetail
from city_engine.models import City, StandardLevelResidentialZone
from cou.abstract import AbstractAdapter
from cou.abstract import RootClass
from player.models import Message
from player.models import Profile
from .turn_data.build import build_building, build_resident_zone
from .turn_data.main import TurnCalculation
from map_engine.map_viewer.main import HexTable
from map_engine.models import Field


@login_required
def main_view(request):
    profile = Profile.objects.get(user_id=request.user.id)
    city = City.objects.get(player=profile)
    rc = RootClass(city, request.user)
    new_board = HexTable(Field.objects.filter(player=profile), rc)
    new_hex_detail = HexDetail(city, rc)

    total_cost_of_main = sum(b.maintenance_cost for b in rc.list_of_buildings)
    building_under_construction = [b for b in rc.list_of_buildings if b.if_under_construction is True]

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
            "hex_table": mark_safe(new_board.hex_table),
            "hex_detail_info_table": mark_safe(new_hex_detail.hex_detail_info_table),
            "buildings": (
                rc.list_of_buildings[b]
                for b in rc.list_of_buildings
                if b.if_under_construction == False
            ),
            "buildings_under_construction": building_under_construction,
            "total_cost_of_maintenance": total_cost_of_main,
            "citizen": (rc.citizens_in_city[c] for c in rc.citizens_in_city),
            "list_of_buildings_class": list_of_buildings_class,
            "families": (rc.families[f] for f in rc.families),
        },
    )


@login_required
def resources(request):
    profile = Profile.objects.get(user_id=request.user.id)
    city = City.objects.get(player=profile)
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
    profile = Profile.objects.get(user_id=request.user.id)
    city = City.objects.get(player=profile)
    data = RootClass(city, request.user, is_turn_calculation=True)
    TurnCalculation(city, data, profile).run()
    # return render(request, 'city_calculation_view.html')
    return HttpResponseRedirect("/main")


@login_required
def build(request, row, col, build_type):
    build_building(request, row, col, build_type)
    return HttpResponseRedirect("/main")


@login_required
def build_resident(request, row, col, max_population):
    build_resident_zone(request, row, col, max_population)
    return HttpResponseRedirect("/main")

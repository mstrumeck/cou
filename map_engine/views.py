from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from .map_generator.generator import MapCreator
from .map_viewer.main import HexTable
from .models import Map, Field


def list_of_maps(request):
    return render(request, "maps_list.html", {'maps': Map.objects.all()})


def create_new_map(request):
    mc = MapCreator()
    mc.create_map()
    return HttpResponseRedirect("/main")


def show_map(request, map_id):
    fields = Field.objects.filter(map_id=map_id)
    hex_table = HexTable(fields).create()
    return render(request, "map.html", {
        'hex_table': mark_safe(hex_table),
        'map_id': map_id
    })


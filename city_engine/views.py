from django.shortcuts import render
from .models import City, Residential, ProductionBuilding, CityField
from player.models import Profile
from django.contrib.auth.models import User
from citizen_engine.models import Citizen
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .board import hex_table, hex_detail_info_table, HEX_NUM
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
        if city_field.if_residental is True:
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
                                              'hex_detail_info_table':mark_safe(hex_detail_info_table),
                                              'HEX_NUM': range(HEX_NUM)})


def turn_calculations(request):
    return HttpResponseRedirect(reverse('city_engine:main_view'))


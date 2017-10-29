from city_engine.models import list_of_models, electricity_buildings
from django.db.models import Sum
from city_engine.main_view_data.board import Board


def update_build_status(city):
    for model in list_of_models:
        for building in model.objects.filter(city=city):
            building.build_status()
    city.save()


def calculate_maintenance_cost(list_of_models, city):
    total_maintenance_cost = 0
    for model in list_of_models:
        total_cost_per_model = model.objects.filter(city=city).aggregate(Sum('maintenance_cost'))['maintenance_cost__sum']
        if total_cost_per_model is not None:
            total_maintenance_cost += total_cost_per_model
    return total_maintenance_cost

# def update_buildings_production(city):


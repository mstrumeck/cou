from city_engine.models import list_of_models, \
    electricity_buildings, Residential, ProductionBuilding, list_of_buildings_categories, \
    list_of_all_buildings, list_of_buildings_with_employees, WindPlant, WaterTower
from django.db.models import Sum
from citizen_engine.models import Citizen, WORK_CHOICES
from city_engine.main_view_data.city_stats import CityPopulationStats
from random import randint, choice, randrange
from city_engine.main_view_data.board import Board


class TurnCalculation(object):
    def __init__(self, city):
        self.city = city
        self.update_build_status()
        # self.update_population()
        # self.update_employee_allocation()

    def update_build_status(self):
        for model in list_of_models:
            for building in model.objects.filter(city=self.city):
                building.build_status()
        self.city.save()


def calculate_maintenance_cost(list_of_models, city):
    total_maintenance_cost = 0
    for model in list_of_models:
        total_cost_per_model = model.objects.filter(city=city).aggregate(Sum('maintenance_cost'))['maintenance_cost__sum']
        if total_cost_per_model is not None:
            total_maintenance_cost += total_cost_per_model
    return total_maintenance_cost

# def update_buildings_production(city):
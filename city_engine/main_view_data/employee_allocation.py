from city_engine.models import list_of_models, \
    electricity_buildings, Residential, ProductionBuilding, list_of_buildings_categories, \
    list_of_all_buildings, list_of_buildings_with_employees, WindPlant, WaterTower
from django.db.models import Sum
from citizen_engine.models import Citizen, WORK_CHOICES
from city_engine.main_view_data.city_stats import CityPopulationStats
from random import randint, choice, randrange
from citizen_engine.citizen_creation import CreateCitizen


class EmployeeAllocation(object):
    def __init__(self, city):
        self.city = city
        self.update_population()

    def update_population(self):
        city_population_stats = CityPopulationStats(city=self.city)
        if Citizen.objects.filter(city=self.city).count() < city_population_stats.calculate_max_population():
            if self.not_full_production_buildings() is not None:
                dif_population = city_population_stats.calculate_max_population() - Citizen.objects.filter(city=self.city).count()
                for citizen in range(randint(0, dif_population)):
                    target_production = self.not_full_production_buildings()
                    if target_production is not None:
                        CreateCitizen(self.city, target_production)
                        self.update_employee_allocation()
                    else:
                        break

    def clean_info_about_employees(self):
        for windplant in WindPlant.objects.filter(city=self.city):
            windplant.current_employees = 0
            windplant.save()
        for watertower in WaterTower.objects.filter(city=self.city):
            watertower.current_employees = 0
            watertower.save()
        for production_building in ProductionBuilding.objects.filter(city=self.city):
            production_building.current_employees = 0
            production_building.save()

    def not_full_production_buildings(self):
        data = []
        for categories in list_of_buildings_with_employees:
            for buildings in categories.objects.filter(city=self.city):
                if buildings.current_employees < buildings.max_employees:
                    data.append(buildings)
        if data:
            return choice(data).type_of_work_building()
        else:
            return None

    def update_employee_allocation(self):
        for windplant in WindPlant.objects.filter(city=self.city):
            windplant.current_employees = Citizen.objects.filter(city=self.city, work_in_windplant=windplant).count()
            windplant.save()
        for watertower in WaterTower.objects.filter(city=self.city):
            watertower.current_employees = Citizen.objects.filter(city=self.city, work_in_watertower=watertower).count()
            watertower.save()
        for production_building in ProductionBuilding.objects.filter(city=self.city):
            production_building.current_employees = Citizen.objects.filter(city=self.city, work_in_production=production_building).count()
            production_building.save()
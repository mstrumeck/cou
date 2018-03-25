from city_engine.models import ProductionBuilding, list_of_buildings_with_employees, WindPlant, WaterTower
from citizen_engine.models import Citizen
from city_engine.main_view_data.city_stats import CityPopulationStats
from random import randint, choice
from citizen_engine.citizen_creation import CreateCitizen
from cou.redis import r


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
        WindPlant.objects.filter(city=self.city).update(current_employees=0)
        WaterTower.objects.filter(city=self.city).update(current_employees=0)
        ProductionBuilding.objects.filter(city=self.city).update(current_employees=0)

    def not_full_production_buildings(self):
        data = []
        for categories in list_of_buildings_with_employees:
            for buildings in categories.objects.filter(city=self.city).values(
                    'type_of_working_building', 'current_employees', 'max_employees'):
                if buildings['current_employees'] < buildings['max_employees']:
                    data.append(buildings['type_of_working_building'])
        if data:
            return choice(data)
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
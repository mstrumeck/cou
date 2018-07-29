from citizen_engine.models import Citizen
from city_engine.main_view_data.city_stats import CityPopulationStats
from random import randint, choice
from citizen_engine.citizen_creation import CreateCitizen


class EmployeeAllocation(object):
    def __init__(self, city, data):
        self.city = city
        self.data = data

    def run(self):
        self.update_population()

    def update_population(self):
        city_population_stats = CityPopulationStats(city=self.city)
        max_population = city_population_stats.calculate_max_population()
        if Citizen.objects.filter(city=self.city).count() < max_population:
            if self.not_full_production_buildings() is not None:
                dif_population = max_population - Citizen.objects.filter(city=self.city).count()
                for citizen in range(randint(0, dif_population)):
                    target_production = self.not_full_production_buildings()
                    if target_production is not None:
                        CreateCitizen().create_with_workplace(self.city, target_production)
                    else:
                        break

    def not_full_production_buildings(self):
        data = []
        for buildings in self.data.list_of_workplaces():
            if buildings.employee.count() < buildings.max_employees:
                data.append(buildings)
        if data:
            return choice(data)
        else:
            return None
from city_engine.models import Residential, list_of_models, waterworks_buildings, PowerPlant, WindPlant, Waterworks, Building
from citizen_engine.models import Citizen
from django.db.models import Sum
from city_engine.abstract import RootClass


class CityStatsCenter(object):
    def __init__(self, city):
        self.city = city
        self.create_stats_for_city()

        self.energy_bilans = self.energy_stats.city_energy_bilans()
        self.energy_allocation = self.energy_stats.calculate_energy_allocation_in_city()
        self.energy_production = self.energy_stats.calculate_energy_production_in_city()

        self.water_bilans = self.water_stats.city_water_bilans()
        self.water_production = self.water_stats.calculate_water_production_in_city()
        self.water_allocation = self.water_stats.calculate_water_allocation_in_city()

        self.building_under_construction = self.building_stats.list_of_buildings_under_construction()
        self.list_of_buildings = self.building_stats.list_of_buildings()

        self.current_population = Citizen.objects.filter(city=self.city).count()
        self.max_population = self.populations_stats.calculate_max_population()

    def create_stats_for_city(self):
        self.energy_stats = CityEnergyStats(self.city)
        self.water_stats = CityWaterStats(self.city)
        self.populations_stats = CityPopulationStats(self.city)
        self.building_stats = CityBuildingStats(self.city)


class CityEnergyStats(RootClass):

    def city_energy_bilans(self):
        return self.calculate_energy_production_in_city() - self.calculate_energy_allocation_in_city()

    def calculate_energy_production_in_city(self):
        return sum([b.total_production() for b in self.list_of_buildings_in_city(abstract_class=PowerPlant)])

    def calculate_energy_allocation_in_city(self):
        return sum([b.energy_allocated for b in self.list_of_buildings_in_city(abstract_class=PowerPlant)])

    def calculate_energy_usage_in_city(self):
        return sum([b.energy_required for b in self.list_of_buildings_in_city()])


class CityWaterStats(RootClass):

    def city_water_bilans(self):
        return self.calculate_water_production_in_city() - self.calculate_water_allocation_in_city()

    def calculate_water_production_in_city(self):
        return sum([b.total_production() for b in self.list_of_buildings_in_city(abstract_class=Waterworks)])

    def calculate_water_usage_in_city(self):
        return sum([b.water_required for b in self.list_of_buildings_in_city()])

    def calculate_water_allocation_in_city(self):
        return sum([b.water_allocated for b in self.list_of_buildings_in_city(abstract_class=Waterworks)])


class CityBuildingStats(RootClass):

    def list_of_buildings_under_construction(self):
        return [[b['name'], b['current_build_time'], b['build_time']] for b in self.list_of_buildings_in_city_with_values(
            'if_under_construction', 'name', 'current_build_time', 'build_time') if b['if_under_construction'] is True]

    def list_of_buildings(self):
        return [b['name'] for b in self.list_of_buildings_in_city_with_values('if_under_construction', 'name')
                if b['if_under_construction'] is False]


class CityPopulationStats(RootClass):

    def calculate_max_population(self):
        total = Residential.objects.filter(city=self.city).aggregate(Sum('max_population'))['max_population__sum']
        if total:
            return total
        else:
            return 0

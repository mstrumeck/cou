from city_engine.models import Residential, PowerPlant, Waterworks
from citizen_engine.models import Citizen
from django.db.models import Sum
from city_engine.abstract import RootClass


class CityStatsCenter(object):
    def __init__(self, city, data):
        self.city = city
        self.data = data
        self.create_stats_for_city()

        self.energy_bilans = self.energy_stats.city_energy_bilans()
        self.energy_allocation = self.energy_stats.calculate_energy_allocation_in_city()
        self.energy_production = self.energy_stats.calculate_energy_production_in_city()

        self.raw_water_bilans = self.raw_water_stats.raw_city_water_bilans()
        self.raw_water_production = self.raw_water_stats.calculate_raw_water_production_in_city()
        self.raw_water_allocation = self.raw_water_stats.calculate_raw_water_allocation_in_city()

        self.clean_water_bilans = self.clean_water_stats.clean_city_water_bilans()
        self.clean_water_production = self.clean_water_stats.calculate_clean_water_production_in_city()
        self.clean_water_allocation = self.clean_water_stats.calculate_clean_water_allocated_in_city()

        self.building_under_construction = self.building_stats.list_of_buildings_under_construction()
        self.list_of_buildings = self.building_stats.list_of_buildings()

        self.current_population = Citizen.objects.filter(city=self.city).count()
        self.max_population = self.populations_stats.calculate_max_population()

    def create_stats_for_city(self):
        self.energy_stats = CityEnergyStats(self.city, self.data)
        self.raw_water_stats = CityRawWaterStats(self.city, self.data)
        self.clean_water_stats = CityCleanWaterStats(self.city, self.data)
        self.populations_stats = CityPopulationStats(self.city)
        self.building_stats = CityBuildingStats(self.city, self.data)


class CityEnergyStats(object):

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def city_energy_bilans(self):
        return self.calculate_energy_production_in_city() - self.calculate_energy_allocation_in_city()

    def calculate_energy_production_in_city(self):
        return sum([b.total_production() for b in self.data.power_plant_buildings])

    def calculate_energy_allocation_in_city(self):
        return sum([b.energy_allocated for b in self.data.power_plant_buildings])

    def calculate_energy_usage_in_city(self):
        return sum([b.energy_required for b in self.data.list_of_buildings])


class CityRawWaterStats(object):

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def raw_city_water_bilans(self):
        return self.calculate_raw_water_production_in_city() - self.calculate_raw_water_allocation_in_city()

    def calculate_raw_water_production_in_city(self):
        return sum([b.total_production() for b in self.data.waterworks_buildings])

    def calculate_raw_water_usage_in_city(self):
        return sum([b.raw_water for b in self.data.sewageworks_buildings])

    def calculate_raw_water_allocation_in_city(self):
        return sum([b.raw_water_allocated for b in self.data.waterworks_buildings])


class CityCleanWaterStats(object):

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def calculate_clean_water_production_in_city(self):
        return sum([b.total_production() for b in self.data.sewageworks_buildings])

    def calculate_clean_water_usage_in_city(self):
        return sum([b.water for b in self.data.list_of_buildings])

    def calculate_clean_water_allocated_in_city(self):
        return sum([b.clean_water_allocated for b in self.data.sewageworks_buildings])

    def clean_city_water_bilans(self):
        return self.calculate_clean_water_production_in_city() - self.calculate_clean_water_allocated_in_city()


class CityBuildingStats(object):
    def __init__(self, city, data):
        self.city = city
        self.data = data

    def list_of_buildings_under_construction(self):
        return [[b['name'], b['current_build_time'], b['build_time']] for b in
                self.data.list_of_building_with_values if b['if_under_construction'] is True]

    def list_of_buildings(self):
        return [b['name'] for b in self.data.list_of_building_with_values
                if b['if_under_construction'] is False]


class CityPopulationStats(object):

    def __init__(self, city):
        self.city = city

    def calculate_max_population(self):
        total = Residential.objects.filter(city=self.city).aggregate(Sum('max_population'))['max_population__sum']
        if total:
            return total
        else:
            return 0

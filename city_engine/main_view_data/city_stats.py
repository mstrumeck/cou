from city_engine.models import Residential, list_of_models, electricity_buildings, waterworks_buildings
from citizen_engine.models import Citizen
from django.db.models import Sum


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


class CityEnergyStats(object):
    def __init__(self, city):
        self.city = city

    def city_energy_bilans(self):
        return self.calculate_energy_production_in_city() - self.calculate_energy_allocation_in_city()

    def calculate_energy_production_in_city(self):
        energy = 0
        for models in electricity_buildings:
            list_of_buildings = models.objects.filter(city=self.city)
            for building in list_of_buildings:
                energy += building.total_production()
        return energy

    def calculate_energy_allocation_in_city(self):
        energy_allocated = 0
        for models in electricity_buildings:
            list_of_buildings = models.objects.filter(city=self.city).values('energy_allocated')
            if list_of_buildings.exists():
                for building in list_of_buildings:
                    energy_allocated += building['energy_allocated']
            return energy_allocated

    def calculate_energy_usage_in_city(self):
        total_energy = 0
        for model in list_of_models:
            for building in model.objects.filter(city=self).values('energy_required'):
                total_energy += building['energy_required']
        return total_energy


class CityWaterStats(object):
    def __init__(self, city):
        self.city = city

    def city_water_bilans(self):
        return self.calculate_water_production_in_city() - self.calculate_water_allocation_in_city()

    def calculate_water_production_in_city(self):
        water = 0
        for models in waterworks_buildings:
            list_of_buildings = models.objects.filter(city=self.city)
            for building in list_of_buildings:
                water += building.total_production()
        return water

    def calculate_water_usage_in_city(self):
        total_water = 0
        for model in list_of_models:
            for buildings in model.objects.filter(city=self.city).values('water_required'):
                total_water += buildings['water_required']
        return total_water

    def calculate_water_allocation_in_city(self):
        water_allocated = 0
        for models in waterworks_buildings:
            list_of_buildings = models.objects.filter(city=self.city).values('water_allocated')
            for building in list_of_buildings:
                water_allocated += building['water_allocated']
        return water_allocated


class CityBuildingStats(object):
    def __init__(self, city):
        self.city = city

    def list_of_buildings_under_construction(self):
        building_name, building_cur, building_end = [], [], []
        for model in list_of_models:
            for building in model.objects.filter(city=self.city).values(
                    'if_under_construction',
                    'name', 'current_build_time', 'build_time'):
                if building['if_under_construction'] is True:
                    building_name.append(building['name'])
                    building_cur.append(building['current_build_time'])
                    building_end.append(building['build_time'])
        if not building_name:
            return None
        return zip(building_name, building_cur, building_end)

    def list_of_buildings(self):
        building_names = []
        for model in list_of_models:
            for building in model.objects.filter(city=self.city).values('if_under_construction', 'name'):
                if building['if_under_construction'] is False:
                    try:
                        building_names.append(building['name'])
                    except(AttributeError):
                        pass
        return building_names


class CityPopulationStats(object):
    def __init__(self, city):
        self.city = city

    def calculate_max_population(self):
        if Residential.objects.filter(city=self.city).aggregate(Sum('max_population'))['max_population__sum']:
            return Residential.objects.filter(city=self.city).aggregate(Sum('max_population'))['max_population__sum']
        else:
            return 0

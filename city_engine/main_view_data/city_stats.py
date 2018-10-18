from city_engine.models import Residential, BuldingsWithWorkes, Vehicle, TradeDistrict, PowerPlant, Waterworks, SewageWorks
from citizen_engine.models import Citizen
from django.db.models import Sum


class CityStatsCenter:
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
        self.populations_stats = CityPopulationStats(self.city, self.data)
        self.building_stats = CityBuildingStats(self.city, self.data)


class CityEnergyStats:

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def city_energy_bilans(self):
        return self.calculate_energy_production_in_city() - self.calculate_energy_allocation_in_city()

    def calculate_energy_production_in_city(self):
        return sum([b.total_production(
            self.data.list_of_buildings,
            self.data.citizens_in_city
        ) for b in self.data.list_of_buildings if isinstance(b, PowerPlant)])

    def calculate_energy_allocation_in_city(self):
        return sum([b.energy_allocated for b in self.data.list_of_buildings if isinstance(b, PowerPlant)])

    def calculate_energy_usage_in_city(self):
        return sum([b.energy_required for b in self.data.list_of_buildings])


class CityRawWaterStats:

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def raw_city_water_bilans(self):
        return self.calculate_raw_water_production_in_city() - self.calculate_raw_water_allocation_in_city()

    def calculate_raw_water_production_in_city(self):
        return sum([b.total_production(
            self.data.list_of_buildings,
            self.data.citizens_in_city
        ) for b in self.data.list_of_buildings if isinstance(b, Waterworks)])

    def calculate_raw_water_usage_in_city(self):
        return sum([b.raw_water for b in self.data.list_of_buildings if isinstance(b, SewageWorks)])

    def calculate_raw_water_allocation_in_city(self):
        return sum([b.raw_water_allocated for b in self.data.list_of_buildings if isinstance(b, Waterworks)])


class CityCleanWaterStats:

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def calculate_clean_water_production_in_city(self):
        return sum([b.total_production(
            self.data.list_of_buildings,
            self.data.citizens_in_city
        ) for b in self.data.list_of_buildings if isinstance(b, SewageWorks)])

    def calculate_clean_water_usage_in_city(self):
        return sum([b.water for b in self.data.list_of_buildings])

    def calculate_clean_water_allocated_in_city(self):
        return sum([b.clean_water_allocated for b in self.data.list_of_buildings if isinstance(b, SewageWorks)])

    def clean_city_water_bilans(self):
        return self.calculate_clean_water_production_in_city() - self.calculate_clean_water_allocated_in_city()


class CityBuildingStats:
    def __init__(self, city, data):
        self.city = city
        self.data = data

    def home_areas_demand(self):
        return "{}/{}".format(
            sum(self.data.list_of_workplaces[h]['max_employees'] - self.data.list_of_workplaces[h]['people_in_charge']
                 for h in self.data.list_of_workplaces),
            sum(self.data.list_of_workplaces[h]['max_employees'] for h in self.data.list_of_workplaces))

    def industrial_areas_demand(self):
        return "{}/{}".format(
            sum(self.data.list_of_buildings[i]['max_employees'] - self.data.list_of_buildings[i]['people_in_charge']
                for i in self.data.list_of_buildings
                 if isinstance(i, TradeDistrict)),
            sum(self.data.list_of_buildings[i]['max_employees'] for i in self.data.list_of_buildings
                 if isinstance(i, TradeDistrict)))

    def trade_areas_demand(self):
        return "To implement"
        # return "{}/{}".format(
        #     Residential.objects.filter(city=self.city).aggregate(Sum('max_population'))['max_population__sum'] - Citizen.objects.filter(city=self.city).count() ,
        #     Residential.objects.filter(city=self.city).aggregate(Sum('max_population'))['max_population__sum'])

    def list_of_buildings_under_construction(self):
        return [[b.name, b.current_build_time, b.build_time] for b in
                self.data.list_of_buildings if b.if_under_construction is True]

    def list_of_buildings(self):
        return [b.name for b in self.data.list_of_buildings
                if b.if_under_construction is False]


class CityPopulationStats:

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def calculate_max_population(self):
        total = sum(b.max_population for b in self.data.list_of_buildings if isinstance(b, Residential))
        # total = Residential.objects.filter(city=self.city).aggregate(Sum('max_population'))['max_population__sum']
        if total:
            return total
        else:
            return 0

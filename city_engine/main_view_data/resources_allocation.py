from city_engine.main_view_data.allocation_pattern import AllocationPattern
from city_engine.models import CityField, list_of_models, PowerPlant, Waterworks, Residential, DumpingGround, \
    list_of_buildings_categories, electricity_buildings, waterworks_buildings, WindPlant, ProductionBuilding, WaterTower
from city_engine.main_view_data.trash_management import CollectGarbage
from city_engine.abstract import RootClass
from random import shuffle
from django.db.models import F


class ResourceAllocation(RootClass):

    def run(self):
        self.clean_city_field_data()
        self.clean_resource_data()
        self.launch_resources_allocation_reset()
        self.all_resource_allocation()
        self.pollution_allocation()
        CollectGarbage(self.city).run()

    def clean_city_field_data(self):
        CityField.objects.filter(city=self.city).update(pollution=0)

    def clean_resource_data(self):
        for models in list_of_models:
            models.objects.filter(city=self.city).update(energy=0, water=0)

    def launch_resources_allocation_reset(self):
        for building in electricity_buildings:
            building.objects.filter(city=self.city).update(energy_allocated=0)
        for building in waterworks_buildings:
            building.objects.filter(city=self.city).update(water_allocated=0)

    def all_resource_allocation(self):
        self.energy_resources_allocation()
        self.water_resources_allocation()
        self.pollution_allocation()

    def energy_resources_allocation(self):
        builds_in_city = {(b.city_field.row, b.city_field.col): b for b in
                          self.list_of_building_in_city_excluding(WindPlant)}
        for power_plant in self.list_of_buildings_in_city(abstract_class=PowerPlant):
            pattern = AllocationPattern().create_allocation_pattern(power_plant.city_field.row, power_plant.city_field.col)
            while power_plant.energy_allocated < power_plant.total_production():
                try:
                    next_value = next(pattern)
                except(StopIteration):
                    break
                for field in next_value:
                    if field in builds_in_city:
                        self.energy_allocation(power_plant, builds_in_city[(field)])

    def water_resources_allocation(self):
        builds_in_city = {(b.city_field.row, b.city_field.col): b for b in
                          self.list_of_building_in_city_excluding(WaterTower)}
        for water_tower in self.list_of_buildings_in_city(abstract_class=Waterworks):
            pattern = AllocationPattern().create_allocation_pattern(water_tower.city_field.row, water_tower.city_field.col)
            while water_tower.water_allocated < water_tower.total_production():
                try:
                    next_value = next(pattern)
                except(StopIteration):
                    break
                for field in next_value:
                    if field in builds_in_city:
                        self.water_allocation(water_tower, builds_in_city[(field)])#DOKONCZ

    def energy_allocation(self, building, target_build):
        energy_left = building.total_production() - building.energy_allocated
        energy_to_fill = target_build.energy_required - target_build.energy
        if energy_left >= energy_to_fill:
            building.energy_allocated += energy_to_fill
            target_build.energy += energy_to_fill
        elif energy_left < energy_to_fill:
            building.energy_allocated += energy_left
            target_build.energy += energy_left
        target_build.save()
        building.save()

    def water_allocation(self, building, target_build):
        water_left = building.total_production() - building.water_allocated
        water_to_fill = target_build.water_required - target_build.water
        if water_left >= water_to_fill:
            building.water_allocated += water_to_fill
            target_build.water += water_to_fill
        elif water_left < water_to_fill:
            building.water_allocated += water_left
            target_build.water += water_left
        target_build.save()
        building.save()

    def pollution_allocation(self):
        build = {(b.city_field): b for b in self.list_of_buildings_in_city()}
        for field in CityField.objects.filter(city=self.city):
            if field in build:
                target_build = build[field]
                allocation_pattern = AllocationPattern().return_first_allocation(field.row, field.col)
                for corr in allocation_pattern:
                    if CityField.objects.filter(city=self.city, row=corr[0], col=corr[1]).exists():
                        target_city_field = CityField.objects.get(city=self.city, row=corr[0], col=corr[1])
                        target_city_field.pollution += (target_build.pollution_calculation() / len(allocation_pattern))
                        field.pollution += (target_build.pollution_calculation() / len(allocation_pattern))
                        target_city_field.save()

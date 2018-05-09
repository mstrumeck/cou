from city_engine.main_view_data.allocation_pattern import AllocationPattern
from city_engine.models import CityField, PowerPlant, Waterworks, WindPlant, WaterTower
from city_engine.main_view_data.trash_management import CollectGarbage
from city_engine.abstract import RootClass
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
        for models in self.get_subclasses_of_all_buildings():
            models.objects.filter(city=self.city).update(energy=0, water=0)

    def launch_resources_allocation_reset(self):
        for energy_building in self.get_subclasses(abstract_class=PowerPlant, app_label='city_engine'):
            energy_building.objects.filter(city=self.city).update(energy_allocated=0)
        for waterwork_building in self.get_subclasses(abstract_class=Waterworks, app_label='city_engine'):
            waterwork_building.objects.filter(city=self.city).update(water_allocated=0)

    def check_if_energy_allocation_is_needed(self):
        return sum([b['energy_required'] - b['energy'] for b in
                    self.list_of_buildings_in_city_with_values('energy', 'energy_required')])

    def check_if_water_allocation_is_needed(self):
        return sum([b['water_required'] - b['water'] for b in
                    self.list_of_buildings_in_city_with_values('water', 'water_required')])

    def all_resource_allocation(self):
        self.energy_resources_allocation()
        self.water_resources_allocation()
        self.pollution_allocation()

    def energy_resources_allocation(self):
        builds_in_city = {(b.city_field.row, b.city_field.col): b for b in
                          self.list_of_building_in_city_excluding(WindPlant)}
        for power_plant in self.list_of_buildings_in_city(abstract_class=PowerPlant):
            if self.check_if_energy_allocation_is_needed() > 0 and power_plant.if_under_construction is False:
                power_plant_total_production = power_plant.total_production()
                pattern = AllocationPattern().create_allocation_pattern(power_plant.city_field.row, power_plant.city_field.col)
                if power_plant.energy_allocated < power_plant_total_production:
                    while power_plant.energy_allocated < power_plant_total_production:
                        try:
                            next_value = next(pattern)
                        except(StopIteration):
                            break
                        for field in next_value:
                            if field in builds_in_city:
                                self.energy_allocation(power_plant, power_plant_total_production, builds_in_city[(field)])
            else:
                break

    def water_resources_allocation(self):
        builds_in_city = {(b.city_field.row, b.city_field.col): b for b in
                          self.list_of_building_in_city_excluding(WaterTower)}
        for water_tower in self.list_of_buildings_in_city(abstract_class=Waterworks):
            if self.check_if_water_allocation_is_needed() > 0 and water_tower.if_under_construction is False:
                water_tower_total_production = water_tower.total_production()
                pattern = AllocationPattern().create_allocation_pattern(water_tower.city_field.row, water_tower.city_field.col)
                while water_tower.water_allocated < water_tower_total_production:
                    try:
                        next_value = next(pattern)
                    except(StopIteration):
                        break
                    for field in next_value:
                        if field in builds_in_city:
                            self.water_allocation(water_tower, water_tower_total_production, builds_in_city[(field)])
            else:
                break

    def energy_allocation(self, power_plant, power_plant_total_production, build_to_energize):
        energy_left = power_plant_total_production - power_plant.energy_allocated
        energy_to_fill = build_to_energize.energy_required - build_to_energize.energy
        if energy_left >= energy_to_fill:
            power_plant.energy_allocated = F('energy_allocated') + energy_to_fill
            build_to_energize.energy = F('energy') + energy_to_fill
        elif energy_left < energy_to_fill:
            power_plant.energy_allocated = F('energy_allocated') + energy_left
            build_to_energize.energy = F('energy') + energy_left
        build_to_energize.save()
        power_plant.save()
        build_to_energize.refresh_from_db()
        power_plant.refresh_from_db()

    def water_allocation(self, water_tower, water_tower_total_production, build_to_hydrated):
        water_left = water_tower_total_production - water_tower.water_allocated
        water_to_fill = build_to_hydrated.water_required - build_to_hydrated.water
        if water_left >= water_to_fill:
            water_tower.water_allocated = F('water_allocated') + water_to_fill
            build_to_hydrated.water = F('water') + water_to_fill
        elif water_left < water_to_fill:
            water_tower.water_allocated = F('water_allocated') + water_left
            build_to_hydrated.water = F('water') + water_left
        build_to_hydrated.save()
        water_tower.save()
        build_to_hydrated.refresh_from_db()
        water_tower.refresh_from_db()

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
                        field.pollution = F('pollution') + (target_build.pollution_calculation() / len(allocation_pattern))
                        target_city_field.save()

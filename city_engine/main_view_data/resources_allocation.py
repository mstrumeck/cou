from city_engine.main_view_data.global_variables import HEX_NUM_IN_ROW
from random import shuffle
from city_engine.models import CityField, list_of_models, list_of_buildings_categories, list_of_buildings_with_employees


class ResourceAllocation(object):
    def __init__(self, city):
        self.city = city
        self.clean_city_field_data()
        self.clean_resource_data()
        self.all_resource_allocation()
        self.pollution_allocation()

    def create_allocation_pattern(self, row, col):
        first_alloc = []
        for hex_in_row in range(1, int(HEX_NUM_IN_ROW+1)):
            allocation_pattern = [
                (row - hex_in_row, col),
                (row - hex_in_row, col + hex_in_row),
                (row + hex_in_row, col),
                (row + hex_in_row, col + hex_in_row),
                (row, col - hex_in_row),
                (row, col + hex_in_row)
            ]
            for calculations in allocation_pattern:
                if calculations[0] >= 0 or calculations[1] >= 0:
                    first_alloc.append(calculations)
            shuffle(first_alloc)
            yield first_alloc
            first_alloc = []
            yield self.return_next_alloc(hex_in_row, hex_in_row+1, row, col)

    def return_next_alloc(self, hex_in_row, wave, row, col):
        allocation = []
        allocation_pattern = [
            (row + hex_in_row, col - hex_in_row + wave),
            (row + hex_in_row, col + hex_in_row - wave),
            (row - hex_in_row, col + hex_in_row - wave),
            (row - hex_in_row, col - hex_in_row + wave)
        ]
        for calculation in allocation_pattern:
            if calculation[0] >= 0 or calculation[1] >= 0:
                allocation.append(calculation)
        shuffle(allocation)
        return allocation

    def return_first_allocation(self, row, col):
        alloc = []
        hex_in_row = 1
        allocation_pattern = [
            (row - hex_in_row, col),
            (row - hex_in_row, col + hex_in_row),
            (row + hex_in_row, col),
            (row + hex_in_row, col + hex_in_row),
            (row, col - hex_in_row),
            (row, col + hex_in_row)
        ]
        for calculations in allocation_pattern:
            if calculations[0] >= 0 or calculations[1] >= 0:
                alloc.append(calculations)
        shuffle(alloc)
        return alloc

    def clean_city_field_data(self):
        for field in CityField.objects.filter(city=self.city):
            field.pollution = 0
            field.save()

    def clean_resource_data(self):
        for models in list_of_models:
            list_of_buildings = models.objects.filter(city=self.city)
            for building in list_of_buildings:
                building.energy = 0
                building.water = 0
                building.save()

    def all_resource_allocation(self):
        for building_category in list_of_buildings_categories:
            # for models in building_category:
                list_of_buildings = building_category.objects.filter(city=self.city)
                for building in list_of_buildings:
                    building.resources_allocation_reset()
                    building.save()
                    pattern = self.create_allocation_pattern(building.city_field.row, building.city_field.col)
                    while building.producted_resources_allocation() < building.total_production():
                        try:
                            next_value = next(pattern)
                        except(StopIteration):
                            break
                        for field in next_value:
                            if CityField.objects.filter(city=self.city, row=field[0], col=field[1]):
                                city_field_for_building = CityField.objects.get(city=self.city, row=field[0], col=field[1])
                                if city_field_for_building.if_electricity is False and building.if_electricity is True:
                                    self.energy_allocation(building, city_field_for_building)
                                elif city_field_for_building.if_waterworks is False and building.if_waterworks is True:
                                    self.water_allocation(building, city_field_for_building)

    def energy_allocation(self, building, city_field_of_building):
        energy_left = building.total_production() - building.energy_allocated
        if city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
            for building_type in city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
                if building_type.objects.filter(city_field=city_field_of_building, city=self.city,
                                                if_electricity=False):
                    target_build = building_type.objects.get(city_field=city_field_of_building, city=self.city,
                                                             if_electricity=False)
                    energy_to_fill = target_build.energy_required - target_build.energy
                    if energy_left > energy_to_fill:
                        building.energy_allocated += energy_to_fill
                        target_build.energy += energy_to_fill
                    elif energy_left < energy_to_fill:
                        building.energy_allocated += energy_left
                        target_build.energy += energy_left
                    target_build.save()
                    building.save()

    def water_allocation(self, building, city_field_of_building):
        water_left = building.total_production() - building.water_allocated
        if city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
            for building_type in city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
                if building_type.objects.filter(city_field=city_field_of_building, city=self.city, if_waterworks=False):
                    target_build = building_type.objects.get(city_field=city_field_of_building, city=self.city,
                                                             if_waterworks=False)
                    water_to_fill = target_build.water_required - target_build.water
                    if water_left > water_to_fill:
                        building.water_allocated += water_to_fill
                        target_build.water += water_to_fill
                    elif water_left < water_to_fill:
                        building.water_allocated += water_left
                        target_build.water += water_left
                    target_build.save()
                    building.save()

    def pollution_allocation(self):
        for field in CityField.objects.filter(city=self.city):
            if field.return_list_of_possible_buildings_related_with_type_of_field():
                for building in field.return_list_of_possible_buildings_related_with_type_of_field():
                    if building.objects.filter(city_field=field, city=self.city):
                        target_build = building.objects.get(city_field=field, city=self.city)
                        allocation_pattern = self.return_first_allocation(field.row, field.col)
                        for corr in allocation_pattern:
                            if CityField.objects.filter(city=self.city, row=corr[0], col=corr[1]):
                                target_city_field = CityField.objects.get(city=self.city, row=corr[0], col=corr[1])
                                target_city_field.pollution += (target_build.pollution_calculation() / len(allocation_pattern))
                                field.pollution += (target_build.pollution_calculation() / len(allocation_pattern))
                                target_city_field.save()
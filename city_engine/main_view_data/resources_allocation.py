from city_engine.main_view_data.global_variables import HEX_NUM_IN_ROW
from random import shuffle
from city_engine.models import CityField, list_of_models,\
    list_of_buildings_categories, electricity_buildings, waterworks_buildings,\
    DumpingGround, DustCart, list_of_buildings_in_city, get_subclasses
from django.db.models import F
from city_engine.main_view_data.trash_management import CollectGarbage


class ResourceAllocation(object):
    def __init__(self, city):
        self.city = city
        self.clean_city_field_data()
        self.clean_resource_data()
        self.all_resource_allocation()
        self.pollution_allocation()
        CollectGarbage(self.city).collect_garbage()
        # self.collect_garbage()

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
        self.launch_resources_allocation_reset()
        for building_category in list_of_buildings_categories:
                list_of_buildings = building_category.objects.filter(city=self.city)
                for building in list_of_buildings:
                    pattern = self.create_allocation_pattern(building.city_field.row, building.city_field.col)
                    while building.producted_resources_allocation() < building.total_production():
                        try:
                            next_value = next(pattern)
                        except(StopIteration):
                            break
                        for field in next_value:
                            if CityField.objects.filter(city=self.city, row=field[0], col=field[1]).exists():
                                city_field_for_building = CityField.objects.get(city=self.city, row=field[0], col=field[1])
                                if city_field_for_building.if_electricity is False and building.if_electricity is True:
                                    self.energy_allocation(building, city_field_for_building)
                                elif city_field_for_building.if_waterworks is False and building.if_waterworks is True:
                                    self.water_allocation(building, city_field_for_building)
                                elif building.if_dumping_ground is True:
                                    self.collect_garbage(building)

    def energy_allocation(self, building, city_field_of_building):
        energy_left = building.total_production() - building.energy_allocated
        if city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
            for building_type in city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
                if building_type.objects.filter(city_field=city_field_of_building, city=self.city,
                                                if_electricity=False).exists():
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
                if building_type.objects.filter(city_field=city_field_of_building, city=self.city, if_waterworks=False).exists():
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
                    if building.objects.filter(city_field=field, city=self.city).exists():
                        target_build = building.objects.get(city_field=field, city=self.city)
                        allocation_pattern = self.return_first_allocation(field.row, field.col)
                        for corr in allocation_pattern:
                            if CityField.objects.filter(city=self.city, row=corr[0], col=corr[1]).exists():
                                target_city_field = CityField.objects.get(city=self.city, row=corr[0], col=corr[1])
                                target_city_field.pollution += (target_build.pollution_calculation() / len(allocation_pattern))
                                field.pollution += (target_build.pollution_calculation() / len(allocation_pattern))
                                target_city_field.save()

    # def collect_garbage(self):
    #     if DumpingGround.objects.filter(city=self.city).exists():
    #         for dumping_ground in DumpingGround.objects.filter(city=self.city):
    #             if dumping_ground.max_space_for_trash > dumping_ground.current_space_for_trash:
    #                 for dust_cart in DustCart.objects.filter(dumping_ground=dumping_ground):
    #                     pattern = self.create_allocation_pattern(dumping_ground.city_field.row, dumping_ground.city_field.col)
    #                     while dust_cart.curr_capacity < (dust_cart.max_capacity * dust_cart.effectiveness()):
    #                         try:
    #                             next_value = next(pattern)
    #                         except(StopIteration):
    #                             break
    #                         for field in next_value:
    #                             if CityField.objects.filter(city=self.city, row=field[0], col=field[1]).exists():
    #                                 city_field_of_target = CityField.objects.filter(city=self.city, row=field[0], col=field[1])
    #                                 for building_model in get_subclasses():
    #                                     if building_model.objects.filter(city_field=city_field_of_target).exists():
    #                                         building_with_trash = building_model.objects.get(city_field=city_field_of_target)
    #                                         if building_with_trash.trash.all().exists():
    #                                             for trash in building_with_trash.trash.all():
    #                                                 if dust_cart.curr_capacity < (dust_cart.max_capacity * dust_cart.effectiveness()):
    #                                                     dust_cart.curr_capacity += trash.size
    #                                                     dust_cart.save()
    #                                                     # print(dust_cart.curr_capacity, 'dust_car - after loading')
    #                                                     trash.delete()
    #                     # print(dumping_ground.current_space_for_trash, 'dumping ground before')
    #                     dumping_ground.current_space_for_trash += dust_cart.curr_capacity
    #                     dust_cart.curr_capacity = 0
    #                     dumping_ground.save()
    #                     dust_cart.save()
    #                     # print(dumping_ground.current_space_for_trash, 'dumping_ground after')
    #                     # print(dust_cart.curr_capacity, 'dust_cart-empty')

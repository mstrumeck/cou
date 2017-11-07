from city_engine.models import Residential, ProductionBuilding, \
    WindPlant,\
    CityField, \
    WaterTower, \
    list_of_models, electricity_buildings, waterworks_buildings
from city_engine.main_view_data.board import Board


def create_list_of_buildings_under_construction(city):
    building_name, building_cur, building_end = [], [], []
    for model in list_of_models:
        for building in model.objects.filter(city=city):
            if building.if_under_construction is True:
                building_name.append(building.name)
                building_cur.append(building.current_build_time)
                building_end.append(building.build_time)
    if not building_name:
        return None
    return zip(building_name, building_cur, building_end)


def create_list_of_buildings(city):
    building_names = []
    for model in list_of_models:
        for building in model.objects.filter(city=city):
            if building.if_under_construction is False:
                try:
                    building_names.append(building.name)
                except(AttributeError):
                    pass
    return building_names


def calculate_max_population(city):
    max_population = 0
    for city_field in CityField.objects.filter(city=city):
        if city_field.if_residential is True:
            max_population += Residential.objects.get(city_field=city_field).max_population
    return max_population


def calculate_current_population(city):
    current_population = 0
    for city_field in CityField.objects.filter(city=city):
        if city_field.if_residential is True:
            current_population += Residential.objects.get(city_field=city_field).current_population
    return current_population


def calculate_energy_production_in_city(city):
    energy = 0
    for models in electricity_buildings:
        list_of_buildings = models.objects.filter(city=city)
        for building in list_of_buildings:
            total_production = building.total_production()
            building.total_energy_production = total_production
            building.save()
            energy += total_production

    # for city_field in CityField.objects.filter(city=city):
    #     if city_field.if_electricity is True:
    #         for building in electricity_buildings:
    #             if building.objects.filter(city_field=city_field).count() == 1:
    #                 energy += building.objects.get(city_field=city_field).total_production()
    return energy


def calculate_energy_usage_in_city(city):
    total_energy = 0
    for model in list_of_models:
        for building in model.objects.filter(city=city):
            total_energy += building.energy_required
    return total_energy


def calculate_water_production_in_city(city):
    water = 0
    for models in waterworks_buildings:
        list_of_buildings = models.objects.filter(city=city)
        for building in list_of_buildings:
            water += building.total_production()
    return water


def create_resource_allocation_pattern(hex_id):
    for x in range(1, int(Board.HEX_NUM_IN_ROW+1)):
        first_calculations = [
            hex_id + x,
            hex_id + Board.HEX_NUM_IN_ROW + x,
            hex_id + Board.HEX_NUM_IN_ROW,
            hex_id + Board.HEX_NUM_IN_ROW - x,
            hex_id - x,
            hex_id - Board.HEX_NUM_IN_ROW - x,
            hex_id - Board.HEX_NUM_IN_ROW,
            hex_id - Board.HEX_NUM_IN_ROW + x,
        ]
        for result in first_calculations:
            if result > 0:
                yield result

        if x >= 2:
            second_calculations = [
                hex_id + (x - x * Board.HEX_NUM_IN_ROW) - 1 - x,
                hex_id + (x - x * Board.HEX_NUM_IN_ROW) - x,
                hex_id + (x - x * Board.HEX_NUM_IN_ROW) + 1 - x,
                hex_id + (x + x * Board.HEX_NUM_IN_ROW) - 1 - x,
                hex_id + (x + x * Board.HEX_NUM_IN_ROW) - x,
                hex_id + (x + x * Board.HEX_NUM_IN_ROW) + 1 - x,
                hex_id + (x * Board.HEX_NUM_IN_ROW) - (2 - x) - x,
                hex_id - (x * Board.HEX_NUM_IN_ROW) - (2 - x) - x,
                hex_id + (x * Board.HEX_NUM_IN_ROW) + (2 + x) - x,
                hex_id - (x * Board.HEX_NUM_IN_ROW) + (2 + x) - x
            ]
            for result in second_calculations:
                if result > 0:
                    yield result
            if x % 2 == 0:
                third_calculations = [
                    hex_id + (x * Board.HEX_NUM_IN_ROW) - 3,
                    hex_id - (x * Board.HEX_NUM_IN_ROW) - 3,
                    hex_id + (x * Board.HEX_NUM_IN_ROW) + 3,
                    hex_id - (x * Board.HEX_NUM_IN_ROW) + 3,
                ]
                for result in third_calculations:
                    if result > 0:
                        yield result
            elif x % 3 == 0:
                fourth_calculations = [
                    hex_id + (x * Board.HEX_NUM_IN_ROW) - 3,
                    hex_id - (x * Board.HEX_NUM_IN_ROW) - 3,
                    hex_id + (x * Board.HEX_NUM_IN_ROW) + 3,
                    hex_id - (x * Board.HEX_NUM_IN_ROW) + 3,
                    hex_id + (x * Board.HEX_NUM_IN_ROW) - 4,
                    hex_id - (x * Board.HEX_NUM_IN_ROW) - 4,
                    hex_id + (x * Board.HEX_NUM_IN_ROW) + 4,
                    hex_id - (x * Board.HEX_NUM_IN_ROW) + 4
                ]
                for result in fourth_calculations:
                    if result > 0:
                        yield result


def allocate_resources(city, provider_type):
    for models in list_of_models:
        list = models.objects.filter(city=city)
        for building in list:
            building.energy = 0
            building.save()

    for models in provider_type:
        list_of_buildings = models.objects.filter(city=city)
        for building in list_of_buildings:
            building.energy_allocated = 0
            building.save()
            pattern = create_resource_allocation_pattern(building.city_field.id)
            while building.energy_allocated < building.total_energy_production:
                try:
                    next_value = next(pattern)
                except(StopIteration):
                    break
                if CityField.objects.filter(city=city, field_id=next_value):
                    if CityField.objects.get(city=city, field_id=next_value).if_waterworks is True:
                        energy_deficit = building.total_energy_production - building.energy_allocated
                        watertower = WaterTower.objects.get(city=city, city_field_id=next_value)
                        # watertower.energy = 0
                        # watertower.save()
                        if watertower.energy_required <= energy_deficit:
                            watertower.energy += watertower.energy_required
                            building.energy_allocated += watertower.energy_required
                        else:
                            watertower.energy += energy_deficit
                            building.energy_allocated += energy_deficit
                        watertower.save()
                        building.save()
                    else:
                        pass
                else:
                    pass
            else:
                pass

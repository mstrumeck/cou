from city_engine.models import Residential, WindPlant, CityField, list_of_models, electricity_buildings, ProductionBuilding


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


def calculate_energy_production(city):
    energy = 0
    for city_field in CityField.objects.filter(city=city):
        if city_field.if_electricity is True:
            for building in electricity_buildings:
                if building.objects.filter(city_field=city_field).count() == 1:
                    energy += building.objects.get(city_field=city_field).total_production()
    return energy




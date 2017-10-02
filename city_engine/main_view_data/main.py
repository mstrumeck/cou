from city_engine.models import Residential, ProductionBuilding, PowerPlant, CityField


def create_list_of_buildings_under_construction(city):
    building_name, building_cur, building_end = [], [], []
    model_list = [Residential, ProductionBuilding, PowerPlant]
    buildings_under_construction = zip(building_name, building_cur, building_end)
    for model in model_list:
        for building in model.objects.filter(city=city):
            if building.if_under_construction is True:
                building_name.append(building.name)
                building_cur.append(building.current_build_time)
                building_end.append(building.build_time)
    return buildings_under_construction


def calculate_max_population(city):
    max_population = 0
    for city_field in CityField.objects.filter(city=city):
        if city_field.if_residential is True:
            max_population += Residential.objects.get(city_field=city_field).max_population
    return max_population


def calculate_energy_production(city):
    energy = 0
    for city_field in CityField.objects.filter(city=city):
        if city_field.if_electricity is True:
            energy += PowerPlant.objects.get(city_field=city_field).total_energy_production()
    return energy


def calculate_current_population(city):
    current_population = 0
    for city_field in CityField.objects.filter(city=city):
        if city_field.if_residential is True:
            current_population += Residential.objects.get(city_field=city_field).current_population
    return current_population

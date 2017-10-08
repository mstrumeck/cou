from city_engine.models import CityField, City, list_of_buildings_categories, electricity_buildings, WindPlant


def build_building(request, hex_id, build_type):
    build_type = eval(build_type)
    city = City.objects.get(user_id=request.user.id)
    city_field = CityField.objects.get(field_id=hex_id, city_id=city.id)

    if build_type in electricity_buildings:
        city_field.if_electricity = True

    city_field.save()

    power_plant = build_type()
    power_plant.city = city
    power_plant.build_time = 3
    power_plant.energy_production = 20
    power_plant.city_field = CityField.objects.get(field_id=hex_id, city=city)
    power_plant.save()
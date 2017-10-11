from city_engine.models import CityField, City, electricity_buildings, WindPlant, RopePlant, CoalPlant


def build_building(request, hex_id, build_type):
    build_type = eval(build_type)
    city = City.objects.get(user_id=request.user.id)
    city_field = CityField.objects.get(field_id=hex_id, city_id=city.id)

    if build_type in electricity_buildings:
        city_field.if_electricity = True

    city_field.save()

    building = build_type()
    building.city = city
    building.city_field = CityField.objects.get(field_id=hex_id, city=city)
    city.cash -= building.build_cost
    city.save()
    building.save()

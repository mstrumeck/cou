from city_engine.models import CityField, City, \
    electricity_buildings, waterworks_buildings, list_of_models, \
    WindPlant, RopePlant, CoalPlant, \
    WaterTower, DumpingGround, \
    Residential, ProductionBuilding


def build_building(request, row, col, build_type):
    build_type = eval(build_type)
    city = City.objects.get(user_id=request.user.id)
    city_field = CityField.objects.get(row=row, col=col, city_id=city.id)

    # if hasattr(build_type, 'if_electricity'):
    #     city_field.if_electricity = True
    # if hasattr(build_type, 'if_waterworks'):
    #     city_field.if_waterworks = True
    # if hasattr(build_type, 'if_residential'):
    #     city_field.if_residential = True
    # if hasattr(build_type, 'if_dumping_ground'):
    #     city_field.if_dumping_ground = True
    # if hasattr(build_type, 'if_production'):
    #     city_field.if_production = True

    city_field.save()

    building = build_type()
    building.city = city
    building.city_field = CityField.objects.get(row=row, col=col, city=city)
    city.cash -= building.build_cost

    city.save()
    building.save()

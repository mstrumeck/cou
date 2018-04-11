from city_engine.models import CityField, City, \
    electricity_buildings, waterworks_buildings, list_of_models, \
    WindPlant, RopePlant, CoalPlant, \
    WaterTower, DumpingGround, \
    Residential, ProductionBuilding


def build_building(request, row, col, build_type):
    build_type = eval(build_type)
    city = City.objects.get(user_id=request.user.id)
    city_field = CityField.objects.get(row=row, col=col, city_id=city.id)

    if build_type in electricity_buildings:
        city_field.if_electricity = True
    elif build_type in waterworks_buildings:
        city_field.if_waterworks = True
    elif build_type is DumpingGround:
        city_field.if_dumping_ground = True
    elif build_type is Residential:
        city_field.if_residential = True
    elif build_type is ProductionBuilding:
        city_field.if_production = True

    city_field.save()

    building = build_type()
    building.city = city
    building.city_field = CityField.objects.get(row=row, col=col, city=city)
    city.cash -= building.build_cost

    city.save()
    building.save()

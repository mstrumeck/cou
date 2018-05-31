from city_engine.models import CityField, City, \
    WindPlant, RopePlant, CoalPlant, \
    WaterTower, DumpingGround, \
    Residential, ProductionBuilding, SewageWorks


def build_building(request, row, col, build_type):
    build_type = eval(build_type)
    city = City.objects.get(user_id=request.user.id)
    city_field = CityField.objects.get(row=row, col=col, city_id=city.id)

    city_field.save()

    building = build_type()
    building.city = city
    building.city_field = CityField.objects.get(row=row, col=col, city=city)
    city.cash -= building.build_cost

    city.save()
    building.save()

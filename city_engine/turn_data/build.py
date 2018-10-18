from city_engine.models import CityField, City
from cou.abstract import AbstractAdapter


def build_building(request, row, col, build_type):
    build_type = {sub.__name__: sub for sub in AbstractAdapter().get_subclasses_of_all_buildings()}[build_type]
    city = City.objects.get(user_id=request.user.id)
    city_field = CityField.objects.get(row=row, col=col, city_id=city.id)

    building = build_type()
    building.city = city
    building.city_field = CityField.objects.get(row=row, col=col, city=city)
    city.cash -= building.build_cost

    city.save()
    city_field.save()
    building.save()

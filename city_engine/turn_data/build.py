from city_engine.models import Field, City, StandardLevelResidentialZone
from cou.abstract import AbstractAdapter
from player.models import Profile


def build_building(request, row, col, build_type):
    row = int(row)
    col = int(col)
    build_type = {
        sub.__name__: sub for sub in AbstractAdapter().get_subclasses_of_all_buildings()
    }[build_type]
    profile = Profile.objects.get(user_id=request.user.id)
    city = City.objects.get(player=profile)
    city_field = Field.objects.get(player=profile, row=row, col=col)

    building = build_type()
    building.city = city
    building.city_field = Field.objects.get(player=profile, row=row, col=col)
    city.cash -= building.build_cost

    city.save()
    city_field.save()
    building.save()


def build_resident_zone(request, row, col, max_population):
    row = int(row)
    col = int(col)
    profile = Profile.objects.get(user_id=request.user.id)
    city = City.objects.get(player=profile)
    city_field = Field.objects.get(player=profile, row=row, col=col)

    building = StandardLevelResidentialZone()
    building.self__init(int(max_population))
    building.city = city
    building.city_field = Field.objects.get(player=profile, row=row, col=col)
    city.cash -= building.build_cost

    city.save()
    city_field.save()
    building.save()

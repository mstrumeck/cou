from city_engine.models import list_of_models
from django.db.models import F


class TrashManagement(object):
    def __init__(self, city):
        self.city = city

    def __all_buildings_in_city(self):
        result = []
        for building_type in list_of_models:
            if building_type.objects.exists_in_city(self.city):
                result += building_type.objects.filter_by_city(self.city)
        return result

    def generate_trash(self):
        for building in self.__all_buildings_in_city():
            if building.trash_calculation() > 0:
                building.trash.create(size=building.trash_calculation())

    def update_trash_time(self):
        for building in self.__all_buildings_in_city():
            building.trash.update(time=F('time')+1)

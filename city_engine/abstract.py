from abc import ABC
from django.apps import apps
from city_engine.models import Building


class RootClass(ABC):
    def __init__(self, city):
        self.city = city

    def get_subclasses(self, abstract_class, app_label):
        result = []
        for model in apps.get_app_config(app_label).get_models():
            if issubclass(model, abstract_class) and model is not abstract_class:
                result.append(model)
        return result

    def list_of_buildings_in_city(self, abstract_class=Building, app_label='city_engine'):
        result = []
        for item in self.get_subclasses(abstract_class, app_label):
            if item.objects.filter(city=self.city).exists():
                a = item.objects.filter(city=self.city)
                for data in a:
                    result.append(data)
        return result

    def list_of_building_in_city_excluding(self, *args, abstract_class=Building, app_label='city_engine'):
        result = []
        for item in self.get_subclasses(abstract_class, app_label):
            if item.objects.filter(city=self.city).exists() and item not in args:
                a = item.objects.filter(city=self.city)
                for data in a:
                    result.append(data)
        return result
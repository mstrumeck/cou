from abc import ABC
from django.apps import apps
from city_engine.models import Building, BuldingsWithWorkes, Vehicle


class RootClass(ABC):
    def __init__(self, city):
        self.city = city

    def get_subclasses(self, abstract_class, app_label):
        return [model for model in apps.get_app_config(app_label).get_models()
                if issubclass(model, abstract_class) and model is not abstract_class]

    def get_subclasses_of_all_buildings(self):
        return self.get_subclasses(abstract_class=Building, app_label='city_engine')

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

    def list_of_workplaces(self):
        result = []
        for subclass in self.get_subclasses(BuldingsWithWorkes, 'city_engine'):
            if subclass.objects.filter(city=self.city).exists():
                a = subclass.objects.filter(city=self.city)
                for building in a:
                    result.append(building)
        for subclass in self.get_subclasses(Vehicle, 'city_engine'):
            if subclass.objects.filter(city=self.city).exists():
                b = subclass.objects.filter(city=self.city)
                for vehicle in b:
                    result.append(vehicle)
        return result

    def list_of_buildings_in_city_with_values(self, *args):
        result = []
        for item in self.get_subclasses(abstract_class=Building, app_label='city_engine'):
            if item.objects.filter(city=self.city).exists():
                a = item.objects.filter(city=self.city).values(*args)
                for data in a:
                    result.append(data)
        return result

    def list_of_buildings_in_city_with_only(self, *args):
        result = []
        for item in self.get_subclasses(abstract_class=Building, app_label='city_engine'):
            if item.objects.filter(city=self.city).exists():
                a = item.objects.filter(city=self.city).only(*args)
                for data in a:
                    result.append(data)
        return result
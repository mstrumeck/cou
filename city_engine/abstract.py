from django.apps import apps
from city_engine.models import Building, BuldingsWithWorkes, Vehicle, PowerPlant, Waterworks, WindPlant, SewageWorks


class RootClass(object):
    def __init__(self, city, user):
        self.city = city

        self.user = user

        self.subclasses_of_all_buildings = self.get_subclasses_of_all_buildings()

        self.list_of_buildings = self.clean_list(self.get_quersies_of_buildings())

        self.power_plant_buildings = [b for b in self.list_of_buildings if isinstance(b, PowerPlant)]

        self.waterworks_buildings = [b for b in self.list_of_buildings if isinstance(b, Waterworks)]

        self.sewageworks_buildings = [b for b in self.list_of_buildings if isinstance(b, SewageWorks)]

        self.list_of_building_with_values = self.list_of_buildings_in_city_with_values(
            'if_under_construction', 'name', 'current_build_time', 'build_time', 'maintenance_cost')
        self.list_of_buildings_only = self.list_of_buildings_in_city_with_only('if_under_construction')

    def datasets_for_turn_calculation(self):
        power_resources_allocation_dataset = {
            'list_of_source': [b for b in self.power_plant_buildings if b.if_under_construction is False],
            'list_without_source': {(b.city_field.row, b.city_field.col): b for b in self.list_of_buildings if not isinstance(b, PowerPlant)},
            'allocated_resource': 'energy_allocated',
            'msg': 'power'
        }
        raw_water_resources_allocation_dataset = {
            'list_of_source': [b for b in self.waterworks_buildings if b.if_under_construction is False],
            'list_without_source': {(b.city_field.row, b.city_field.col): b for b in self.list_of_buildings if isinstance(b, SewageWorks)},
            'allocated_resource': 'raw_water_allocated',
            'msg': 'raw_water'
        }
        clean_water_resources_allocation_dataset = {
            'list_of_source': [b for b in self.sewageworks_buildings if b.if_under_construction is False],
            'list_without_source': {(b.city_field.row, b.city_field.col): b for b in self.list_of_buildings
                                    if not isinstance(b, SewageWorks) and not isinstance(b, Waterworks)},
            'allocated_resource': 'clean_water_allocated',
            'msg': 'clean_water'
        }
        return [power_resources_allocation_dataset, raw_water_resources_allocation_dataset,
                clean_water_resources_allocation_dataset]

    def get_subclasses(self, abstract_class, app_label):
        return [model for model in apps.get_app_config(app_label).get_models()
                if issubclass(model, abstract_class) and model is not abstract_class]

    def get_subclasses_of_all_buildings(self):
        return self.get_subclasses(abstract_class=Building, app_label='city_engine')

    def get_quersies_of_buildings(self):
        return [sub.objects.filter(city=self.city) for sub in self.subclasses_of_all_buildings
                if sub.objects.filter(city=self.city).exists()]

    def clean_list(self, iter):
        result = []
        for item in iter:
            for data in item:
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
        for item in self.subclasses_of_all_buildings:
            if item.objects.filter(city=self.city).exists():
                a = item.objects.filter(city=self.city).values(*args)
                for data in a:
                    result.append(data)
        return result

    def list_of_buildings_in_city_with_only(self, *args):
        result = []
        for item in self.subclasses_of_all_buildings:
            if item.objects.filter(city=self.city).exists():
                a = item.objects.filter(city=self.city).only(*args)
                for data in a:
                    result.append(data)
        return result
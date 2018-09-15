from django.apps import apps
from city_engine.models import Building, CityField, BuldingsWithWorkes, Vehicle, PowerPlant, Waterworks, SewageWorks, Residential
from abc import ABCMeta
from django.db.models import Sum
from resources.models import Resource
from citizen_engine.models import Citizen, Education, Profession


class BasicAbstract(metaclass=ABCMeta):

    def get_subclasses(self, abstract_class, app_label):
        return [model for model in apps.get_app_config(app_label).get_models()
                if issubclass(model, abstract_class) and model is not abstract_class]

    def get_subclasses_of_all_buildings(self):
        return self.get_subclasses(abstract_class=Building, app_label='city_engine')

    def get_queries_of_vehicles(self):
        result = {}
        for sub in self.get_subclasses(abstract_class=Vehicle, app_label='city_engine'):
            data = sub.objects.filter(city=self.city)
            if data.exists():
                for v in data:
                    result[v] = {'people_in_charge': v.employee.count()}
        return result

    def get_quersies_of_buildings(self):
        result = {}
        for sub in self.get_subclasses_of_all_buildings():
            if sub.objects.filter(city=self.city).exists():
                data = sub.objects.filter(city=self.city)
                for b in data:
                    result[b] = {'trash': [trash for trash in b.trash.all() if b.trash.all().exists()],
                                 'row_col_cor': (b.city_field.row, b.city_field.col),
                                 'people_in_charge': b.resident.count() if isinstance(b, Residential) else b.employee.count()}
        return result


class AbstractAdapter(BasicAbstract):
    pass


class ResourcesData(BasicAbstract):
    def __init__(self, city, user):
        self.city = city
        self.user = user
        self.subclasses_of_all_resources = self.get_subclasses(Resource, 'resources')
        self.resources = {ob.__name__: self.resources_size_and_sum(ob) for ob in [sub for sub in self.subclasses_of_all_resources]
                          if self.resources_size_and_sum(ob)[1]}

    def resources_size_and_sum(self, ob):
        data = ob.objects.filter(owner=self.user)
        return [data, data.values('size').aggregate(Sum('size'))['size__sum']]


class RootClass(BasicAbstract):
    def __init__(self, city, user):
        self.city = city
        self.user = user
        self.citizens_in_city = {c: {'educations': c.education_set.all(),
                                     'professions': c.profession_set.all(),
                                     'current_education': c.education_set.filter(if_current=True).last()}
                                 for c in Citizen.objects.filter(city=self.city)}
        self.city_fields_in_city = {f: {
            'row_col': (f.row, f.col),
            'pollution' : f.pollution
        } for f in CityField.objects.filter(city=self.city)}
        self.list_of_buildings = self.get_quersies_of_buildings()
        self.vehicles = self.get_queries_of_vehicles()
        self.list_of_workplaces = {**{b: self.list_of_buildings[b] for b in self.list_of_buildings
                                      if isinstance(b, BuldingsWithWorkes)}, **self.vehicles}

    def datasets_for_turn_calculation(self):
        power_resources_allocation_dataset = {
            'resource': 'energy',
            'list_of_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings if isinstance(b, PowerPlant)},
            'list_without_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                                    if not isinstance(b, PowerPlant)},
            'allocated_resource': 'energy_allocated',
            'msg': 'power'
        }
        raw_water_resources_allocation_dataset = {
            'list_of_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings if isinstance(b, Waterworks)},
            'list_without_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                                    if isinstance(b, SewageWorks)},
            'allocated_resource': 'raw_water_allocated',
            'msg': 'raw_water'
        }
        clean_water_resources_allocation_dataset = {
            'list_of_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings if isinstance(b, SewageWorks)},
            'list_without_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                                    if not isinstance(b, SewageWorks) and not isinstance(b, Waterworks)},
            'allocated_resource': 'clean_water_allocated',
            'msg': 'clean_water'
        }
        return [power_resources_allocation_dataset, raw_water_resources_allocation_dataset, clean_water_resources_allocation_dataset]



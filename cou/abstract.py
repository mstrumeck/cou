from django.apps import apps
from city_engine.models import Building, CityField, BuldingsWithWorkes, Vehicle, PowerPlant,\
    Waterworks, SewageWorks, Residential, StandardLevelResidentialZone
from abc import ABCMeta
from django.db.models import Sum
from resources.models import Resource
from citizen_engine.models import Citizen, Education, Profession, Family
from cou.global_var import ELEMENTARY, COLLEGE, PHD
from player.models import Profile
from cou.data_containers import BuildingDataContainer, CitizenDataContainer, VehicleDataContainer, \
    CityFieldDataContainer, ResidentialDataContainer, FamilyDataContainer


class BasicAbstract(metaclass=ABCMeta):

    def get_subclasses(self, abstract_class, app_label):
        return [model for model in apps.get_app_config(app_label).get_models()
                if issubclass(model, abstract_class) and model is not abstract_class]

    def get_subclasses_of_all_buildings(self):
        return self.get_subclasses(abstract_class=Building, app_label='city_engine')

    def get_queries_of_vehicles(self):
        result = []
        for sub in self.get_subclasses(abstract_class=Vehicle, app_label='city_engine'):
            data = sub.objects.filter(city=self.city)
            if data.exists():
                for v in data:
                    result.append(v)
        return result

    def get_quersies_of_buildings(self):
        result = []
        for sub in self.get_subclasses_of_all_buildings():
            if sub.objects.filter(city=self.city).exists():
                data = sub.objects.filter(city=self.city)
                for b in data:
                    result.append(b)
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
        self.profile = Profile.objects.get(user_id=self.user.id)
        self.to_save = []
        self.city_fields_in_city = {}
        self.citizens_in_city = {}
        self.vehicles = {}
        self.list_of_buildings = {}
        self.families = {}
        self.preprocess_data()
        self.list_of_workplaces = {**{b: self.list_of_buildings[b] for b in self.list_of_buildings
                                      if isinstance(b, BuldingsWithWorkes)}, **self.vehicles}

    def preprocess_buildings(self, buildings, citizens):
        for b in (b for b in buildings if not isinstance(b, Residential)):
            self.to_save.append(b)
            self.list_of_buildings[b] = BuildingDataContainer(instance=b,
                                                              citizens=citizens,
                                                              citizens_data=self.citizens_in_city,
                                                              fields_data=self.city_fields_in_city,
                                                              profile=self.profile)

    def preprocess_citizens(self, citizens, residentials):
        for citizen in citizens:
            self.to_save.append(citizen)
            self.citizens_in_city[citizen] = CitizenDataContainer(citizen, self.to_save, residentials)

    def preprocess_vehicles(self, vehicles, citizens):
        for vehicle in vehicles:
            self.to_save.append(vehicle)
            self.vehicles[vehicle] = VehicleDataContainer(instance=vehicle, citizens=citizens, citizens_in_city=self.citizens_in_city)

    def preprocess_city_fields(self):
        for field in CityField.objects.filter(city=self.city):
            self.city_fields_in_city[field] = CityFieldDataContainer(field)
            self.to_save.append(field)

    def preprocess_residentials(self, buildings, citizens):
        for residential in (r for r in buildings if isinstance(r, Residential)):
            self.to_save.append(residential)
            self.list_of_buildings[residential] = ResidentialDataContainer(instance=residential,
                                                                           citizens=citizens,
                                                                           citizens_data=self.citizens_in_city,
                                                                           fields_data=self.city_fields_in_city,
                                                                           profile=self.profile)

    def preprocess_families(self):
        for family in Family.objects.filter(city=self.city):
            if family.citizen_set.all():
                self.to_save.append(family)
                self.families[family] = FamilyDataContainer(instance=family,
                                                            citizens=self.citizens_in_city,
                                                            residents=[self.list_of_buildings[r] for r in self.list_of_buildings if isinstance(r, Residential)])
            else:
                family.delete()

    def preprocess_data(self):
        citizens = Citizen.objects.filter(city=self.city)
        buildings = self.get_quersies_of_buildings()
        vehicles = self.get_queries_of_vehicles()
        self.preprocess_city_fields()
        self.preprocess_residentials(buildings, citizens)
        self.preprocess_citizens(citizens, [self.list_of_buildings[r] for r in self.list_of_buildings if isinstance(r, Residential)])
        self.preprocess_families()
        self.preprocess_buildings(buildings, citizens)
        self.preprocess_vehicles(vehicles, citizens)

    def datasets_for_turn_calculation(self):
        power_resources_allocation_dataset = {
            'resource': 'energy',
            'list_of_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                               if isinstance(b, PowerPlant) and b.if_under_construction is False},
            'list_without_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                                    if not isinstance(b, PowerPlant) and b.if_under_construction is False},
            'allocated_resource': 'energy_allocated',
            'msg': 'power'
        }
        raw_water_resources_allocation_dataset = {
            'list_of_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings if isinstance(b, Waterworks)
                               and b.if_under_construction is False},
            'list_without_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                                    if isinstance(b, SewageWorks) and b.if_under_construction is False},
            'allocated_resource': 'raw_water_allocated',
            'msg': 'raw_water'
        }
        clean_water_resources_allocation_dataset = {
            'list_of_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings if isinstance(b, SewageWorks)
                               and b.if_under_construction is False},
            'list_without_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                                    if not isinstance(b, SewageWorks) and not isinstance(b, Waterworks)
                                    and b.if_under_construction is False},
            'allocated_resource': 'clean_water_allocated',
            'msg': 'clean_water'
        }
        return [raw_water_resources_allocation_dataset, clean_water_resources_allocation_dataset, power_resources_allocation_dataset]



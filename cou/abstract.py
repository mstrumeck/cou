from abc import ABC

from django.apps import apps

from citizen_engine.models import Citizen, Family
from city_engine.models import Building, CityField, BuldingsWithWorkes, Vehicle, PowerPlant, \
    Waterworks, SewageWorks, Residential, TradeDistrict
from company_engine.models import Company
from cou.data_containers import BuildingDataContainer, CitizenDataContainer, VehicleDataContainer, \
    CityFieldDataContainer, ResidentialDataContainer, FamilyDataContainer, CompaniesDataContainer, MarketDataContainer
from player.models import Profile


class BasicAbstract(ABC):

    def get_subclasses(self, abstract_class, app_label):
        return [model for model in apps.get_app_config(app_label).get_models()
                if issubclass(model, abstract_class) and model is not abstract_class]

    def get_queries_of_residents(self):
        result = []
        for sub in self.get_subclasses(abstract_class=Residential, app_label='city_engine'):
            data = sub.objects.filter(city=self.city)
            if data.exists():
                for r in data:
                    result.append(r)
        return result

    def get_subclasses_of_all_buildings(self):
        return self.get_subclasses(abstract_class=Building, app_label='city_engine') + self.get_subclasses(abstract_class=Building, app_label='resources')

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

    def get_queries_of_companies(self, trade_districts):
        result = []
        for td in trade_districts:
            for sub in self.get_subclasses(abstract_class=Company, app_label='company_engine'):
                if sub.objects.filter(trade_district=td).exists():
                    data = sub.objects.filter(trade_district=td)
                    for c in data:
                        result.append(c)
        return result


class AbstractAdapter(BasicAbstract):
    pass


class RootClass(BasicAbstract):
    def __init__(self, city, user):
        self.city = city
        self.user = user
        self.profile = Profile.objects.get(user_id=self.user.id)
        self.market = MarketDataContainer(self.profile.market)
        self.to_save = []
        self.city_fields_in_city = {}
        self.citizens_in_city = {}
        self.vehicles = {}
        self.list_of_buildings = {}
        self.families = {}
        self.companies = {}
        self.preprocess_data()
        self.list_of_workplaces = {**{b: self.list_of_buildings[b] for b in self.list_of_buildings
                                      if isinstance(b, BuldingsWithWorkes)}, **self.vehicles, **self.companies}

    def preprocess_companies(self, companies, citizens):
        for c in companies:
            self.to_save.append(c)
            self.companies[c] = CompaniesDataContainer(instance=c,
                                                       citizens=citizens,
                                                       citizens_in_city=self.citizens_in_city)

    def preprocess_buildings(self, buildings, citizens):
        for b in (b for b in buildings if not isinstance(b, Residential)):
            self.to_save.append(b)
            self.list_of_buildings[b] = BuildingDataContainer(instance=b,
                                                              citizens=citizens,
                                                              citizens_data=self.citizens_in_city,
                                                              profile=self.profile,
                                                              vehicles=self.vehicles)

    def preprocess_citizens(self, citizens, residentials):
        for citizen in citizens:
            self.to_save.append(citizen)
            self.citizens_in_city[citizen] = CitizenDataContainer(citizen, self.to_save, residentials)

    def preprocess_city_fields(self):
        for field in CityField.objects.filter(city=self.city):
            self.city_fields_in_city[field] = CityFieldDataContainer(field)
            self.to_save.append(field)

    def preprocess_residentials(self, buildings):
        for residential in (r for r in buildings if isinstance(r, Residential)):
            self.to_save.append(residential)
            self.list_of_buildings[residential] = ResidentialDataContainer(instance=residential,
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
        # vehicles = self.get_queries_of_vehicles()
        companies = self.get_queries_of_companies((b for b in buildings if isinstance(b,  TradeDistrict)))
        self.preprocess_city_fields()
        self.preprocess_residentials(buildings)
        self.preprocess_citizens(citizens,
                                 [self.list_of_buildings[r] for r in self.list_of_buildings if isinstance(r, Residential)])
        self.preprocess_families()
        self.preprocess_buildings(buildings, citizens)
        # self.preprocess_vehicles(vehicles, citizens)
        self.preprocess_companies(companies, citizens)

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



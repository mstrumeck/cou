from abc import ABC

from django.apps import apps

from citizen_engine.models import Citizen, Family
from city_engine.models import (
    Building,
    Field,
    PowerPlant,
    Waterworks,
    SewageWorks,
    Residential,
    TradeDistrict,
    AnimalFarm
)
from city_engine.temp_models import DataContainersWithEmployees
from company_engine.models import Company
from player.models import Profile
from resources.models import Cattle
from resources.temp_models import MarketDataContainer


class BasicAbstract(ABC):
    def get_subclasses(self, abstract_class, app_label):
        return [
            model
            for model in apps.get_app_config(app_label).get_models()
            if issubclass(model, abstract_class) and model is not abstract_class
        ]

    def get_queries_of_residents(self):
        result = []
        for sub in self.get_subclasses(
            abstract_class=Residential, app_label="city_engine"
        ):
            data = sub.objects.filter(city=self.city)
            if data.exists():
                for r in data:
                    result.append(r)
        return result

    def get_subclasses_of_all_buildings(self):
        return self.get_subclasses(
            abstract_class=Building, app_label="city_engine"
        ) + self.get_subclasses(abstract_class=Building, app_label="resources")

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
            for sub in self.get_subclasses(
                abstract_class=Company, app_label="company_engine"
            ):
                if sub.objects.filter(trade_district=td).exists():
                    data = sub.objects.filter(trade_district=td)
                    for c in data:
                        result.append(c)
        return result


class AbstractAdapter(BasicAbstract):
    pass


class RootClass(BasicAbstract):
    def __init__(self, city, user, is_turn_calculation=False):
        self.city = city
        self.user = user
        self.is_turn_calculation = is_turn_calculation
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
        if self.list_of_buildings:
            self.max_row = max([self.list_of_buildings[r].instance.city_field.row or 0 for r in self.list_of_buildings])
            self.min_row = min([self.list_of_buildings[r].instance.city_field.row or 0 for r in self.list_of_buildings])
            self.max_col = max([self.list_of_buildings[r].instance.city_field.col or 0 for r in self.list_of_buildings])
            self.min_col = min([self.list_of_buildings[r].instance.city_field.col or 0 for r in self.list_of_buildings])
        self.list_of_workplaces = {
            **{
                b: self.list_of_buildings[b]
                for b in self.list_of_buildings
                if isinstance(self.list_of_buildings[b], DataContainersWithEmployees)
            },
            **self.vehicles,
            **self.companies,
        }

    def kill_person(self, person_instance):
        del self.citizens_in_city[person_instance.instance]
        person_instance.instance.delete()

    def destroy_building(self, building):
        for x in self.list_of_buildings[building.instance].all_people_in_building:
            x.instance.workplace_object = None
            x.instance.save()
        del self.list_of_buildings[building.instance]
        building.instance.delete()

    def preprocess_companies(self, companies):
        for c in companies:
            self.to_save.append(c)
            self.companies[c] = c.temp_model(instance=c, profile=self.profile, employees=self.citizens_in_city, market=self.market)

    def preprocess_buildings(self, buildings):
        for b in (b for b in buildings
                  if not isinstance(b, Residential)
                     and not isinstance(b, TradeDistrict)
                     and not isinstance(b, Company)
                     and not isinstance(b, AnimalFarm)):
            self.to_save.append(b)
            self.list_of_buildings[b] = b.temp_model(
                instance=b,
                profile=self.profile,
                employees=self.citizens_in_city,
                market=self.market)

    def probability_of_death(self, diseases):
        for d in (d for d in diseases if d.is_fatal):
            if d.is_disease_cause_death():
                return True
        return False

    def preprocess_citizens(self, citizens):
        for citizen in citizens:
            diseases = list(citizen.disease_set.all())
            if self.is_turn_calculation:
                if self.probability_of_death(diseases):
                    citizen.kill()
                    continue

            self.to_save.append(citizen)
            self.citizens_in_city[citizen] = citizen.temp_model(
                instance=citizen,
                to_save=self.to_save,
                home=self.list_of_buildings[citizen.resident_object] if citizen.resident_object else None,
                diseases=diseases
            )

    def preprocess_city_fields(self):
        for field in Field.objects.filter(player=self.profile):
            self.city_fields_in_city[field] = field.temp_model(instance=field)
            self.to_save.append(field)

    def preprocess_residentials(self, buildings):
        for residential in (r for r in buildings if isinstance(r, Residential)):
            self.to_save.append(residential)
            self.list_of_buildings[residential] = residential.temp_model(
                instance=residential,
                profile=self.profile,
            )

    def add_citizen_data_to_residentials(self):
        for residential in self.list_of_buildings:
            self.list_of_buildings[residential].fill_data_by_residents(
                [self.citizens_in_city[c] for c in residential.resident.all()]
            )

    def preprocess_families(self):
        for family in Family.objects.filter(city=self.city):
            if family.citizen_set.all():
                self.to_save.append(family)
                self.families[family] = family.temp_model(
                    instance=family,
                    citizens=self.citizens_in_city,
                    residents=[
                        self.list_of_buildings[r]
                        for r in self.list_of_buildings
                        if isinstance(r, Residential)
                    ],
                )
            else:
                family.delete()

    def preprocess_animal_farms(self, buildings):
        for af in (b for b in buildings if isinstance(b, AnimalFarm)):
            self.list_of_buildings[af] = af.temp_model(
                instance=af,
                profile=self.profile,
                employees=self.citizens_in_city,
                cattle=Cattle.objects.filter(farm=af).last(),
                market=self.market)

    def preprocess_data(self):
        citizens = Citizen.objects.filter(city=self.city)
        buildings = self.get_quersies_of_buildings()
        companies = self.get_queries_of_companies(
            (b for b in buildings if isinstance(b, TradeDistrict))
        )
        self.preprocess_city_fields()
        self.preprocess_residentials(buildings)
        self.preprocess_citizens(citizens)
        self.add_citizen_data_to_residentials()
        self.preprocess_families()
        self.preprocess_buildings(buildings)
        self.preprocess_animal_farms(buildings)
        self.preprocess_companies(companies)

    def datasets_for_turn_calculation(self):
        power_resources_allocation_dataset = {
            "resource": "energy",
            "list_of_source": [
                self.list_of_buildings[b]
                for b in self.list_of_buildings
                if isinstance(b, PowerPlant) and b.if_under_construction is False
            ],
            "list_without_source": [
                self.list_of_buildings[b]
                for b in self.list_of_buildings
                if not isinstance(b, PowerPlant) and b.if_under_construction is False
                                   ] + [self.companies[c] for c in self.companies],
            "allocated_resource": "energy_allocated",
        }
        raw_water_resources_allocation_dataset = {
            "list_of_source": [
                self.list_of_buildings[b]
                for b in self.list_of_buildings
                if isinstance(b, Waterworks) and b.if_under_construction is False
            ],
            "list_without_source": [
                self.list_of_buildings[b]
                for b in self.list_of_buildings
                if isinstance(b, SewageWorks) and b.if_under_construction is False
            ],
            "allocated_resource": "raw_water_allocated",
        }
        clean_water_resources_allocation_dataset = {
            "list_of_source": [
                self.list_of_buildings[b]
                for b in self.list_of_buildings
                if isinstance(b, SewageWorks) and b.if_under_construction is False
            ],
            "list_without_source": [
                self.list_of_buildings[b]
                for b in self.list_of_buildings
                if not isinstance(b, SewageWorks)
                and not isinstance(b, Waterworks)
                and b.if_under_construction is False
            ] + [self.companies[c] for c in self.companies],
            "allocated_resource": "clean_water_allocated",
        }
        return [
            power_resources_allocation_dataset,
            raw_water_resources_allocation_dataset,
            clean_water_resources_allocation_dataset,
        ]

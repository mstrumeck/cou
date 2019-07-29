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
    AnimalFarm,
    District,
    Farm
)
from city_engine.temp_models import DataContainersWithEmployees, TempTradeDistrict, TempResidential, TempDistrict
from company_engine.models import Company
from player.models import Profile
from resources.models import Cattle
from resources.temp_models import MarketDataContainer
import itertools


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

    def get_queries_of_companies(self, trade_district):
        result = []
        for sub in self.get_subclasses(
                abstract_class=Company, app_label="company_engine"
        ):
            if sub.objects.filter(trade_district=trade_district).exists():
                data = sub.objects.filter(trade_district=trade_district)
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
        self.list_of_trade_districts = {}
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
                b.instance: b
                for b in self.list_of_buildings.values()
                if isinstance(b, DataContainersWithEmployees)
            },
            **self.companies
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
                diseases=diseases,
                workplace=self._get_citizen_workplace(citizen.workplace_object) if citizen.workplace_object else None
            )

    def _get_citizen_workplace(self, workplace):
        if self.list_of_buildings.get(workplace):
            return self.list_of_buildings[workplace]
        return self.companies[workplace]

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
                field=self.city_fields_in_city[residential.city_field]
            )

    def add_citizen_data_to_residentials(self):
        for residential in (r for r in self.list_of_buildings.values() if isinstance(r, TempResidential)):
            residential.fill_data_by_residents(
                [self.citizens_in_city[c] for c in residential.instance.resident.all()]
            )

    def add_citizen_data_to_buildings(self):
        for b in (b for b in list(itertools.chain(self.list_of_buildings.values(), self.companies.values())) if not isinstance(b, TempResidential)):
            b.create_employess_data({c.instance: c for c in self.citizens_in_city.values() if c.instance.workplace_object == b.instance})

        for d in self.list_of_trade_districts.values():
            d.get_people_in_charge()

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
                cattle=Cattle.objects.filter(farm=af).last(),
                market=self.market)

    def preprocess_trade_districts(self):
        if TradeDistrict.objects.filter(city=self.city).exists():
            for td in TradeDistrict.objects.filter(city=self.city):
                companies = {c: c.temp_model(
                            instance=c,
                            profile=self.profile,
                            market=self.market,
                ) for c in self.get_queries_of_companies(td)
                }
                for k in companies.keys():
                    self.companies[k] = companies[k]
                self.list_of_trade_districts[td] = TempTradeDistrict(
                    instance=td,
                    companies={c.instance: c for c in companies.values() if c.instance.trade_district == td},
                    support_buildings={},
                    profile=self.profile)

    def preprocess_data(self):
        citizens = Citizen.objects.filter(city=self.city)
        buildings = self.get_quersies_of_buildings()
        self.preprocess_city_fields()
        self.preprocess_residentials(buildings)
        self.preprocess_buildings(buildings)
        self.preprocess_trade_districts()
        self.preprocess_animal_farms(buildings)
        self.preprocess_citizens(citizens)
        self.add_citizen_data_to_residentials()
        self.preprocess_families()
        self.add_citizen_data_to_buildings()

    def datasets_for_turn_calculation(self):
        power_resources_allocation_dataset = {
            "resource": "energy",
            "list_of_source": [
                b
                for b in self.list_of_buildings.values()
                if isinstance(b.instance, PowerPlant) and b.instance.if_under_construction is False
            ],
            "list_without_source": list(itertools.chain([
                b
                for b in self.list_of_buildings.values()
                if not isinstance(b.instance, PowerPlant) and b.instance.if_under_construction is False
                                   ], self.list_of_trade_districts.values())),
            "allocated_resource": "energy_allocated",
        }
        raw_water_resources_allocation_dataset = {
            "list_of_source": [
                b
                for b in self.list_of_buildings.values()
                if isinstance(b.instance, Waterworks) and b.instance.if_under_construction is False
            ],
            "list_without_source": [
                b
                for b in self.list_of_buildings.values()
                if isinstance(b.instance, SewageWorks) and b.instance.if_under_construction is False
            ],
            "allocated_resource": "raw_water_allocated",
        }
        clean_water_resources_allocation_dataset = {
            "list_of_source": [
                b
                for b in self.list_of_buildings.values()
                if isinstance(b.instance, SewageWorks) and b.instance.if_under_construction is False
            ],
            "list_without_source": list(itertools.chain([b for b in self.list_of_buildings.values()
                if not isinstance(b.instance, SewageWorks)
                and not isinstance(b.instance, Waterworks)
                and b.instance.if_under_construction is False
            ], self.list_of_trade_districts.values())),
            "allocated_resource": "clean_water_allocated",
        }
        return [
            power_resources_allocation_dataset,
            raw_water_resources_allocation_dataset,
            clean_water_resources_allocation_dataset,
        ]

from abc import ABC

from django.apps import apps

from city_engine.models import (
    BuldingsWithWorkes,
    TradeDistrict,
    DumpingGround,
    DustCart,
)
from company_engine.models import FoodCompany, Food, Company
from cou.global_var import ELEMENTARY, COLLEGE, PHD
from resources.models import AnimalFarm, Cattle, MarketResource, Mass


class DataContainersWithEmployees(ABC):
    def _create_data_for_building_with_worker(
        self, instance, citizens, citizens_in_city
    ):
        self.workers_costs = 0
        self.max_employees = sum(
            [
                instance.elementary_employee_needed,
                instance.college_employee_needed,
                instance.phd_employee_needed,
            ]
        )

        self.elementary_employees = [
            e
            for e in citizens
            if e.workplace_object == instance
            and citizens_in_city[e].current_profession.education in (ELEMENTARY, "None")
        ]

        self.elementary_vacancies = instance.elementary_employee_needed - len(
            [
                e
                for e in citizens
                if e.workplace_object == instance
                and citizens_in_city[e].current_profession.education == ELEMENTARY
            ]
        )

        self.college_employees = [
            e
            for e in citizens
            if e.workplace_object == instance
            and citizens_in_city[e].current_profession.education == COLLEGE
        ]

        self.college_vacancies = instance.college_employee_needed - len(
            [
                e
                for e in citizens
                if e.workplace_object == instance
                and citizens_in_city[e].current_profession.education == COLLEGE
            ]
        )

        self.phd_employees = [
            e
            for e in citizens
            if e.workplace_object == instance
            and citizens_in_city[e].current_profession.education == PHD
        ]

        self.phd_vacancies = instance.phd_employee_needed - len(
            [
                e
                for e in citizens
                if e.workplace_object == instance
                and citizens_in_city[e].current_profession.education == PHD
            ]
        )

        self.all_employees = (
            self.elementary_employees + self.college_employees + self.phd_employees
        )
        self.people_in_charge = len(self.all_employees)

    def _create_data_for_dumping_ground(self, bi, citizens, citizens_in_city, vehicles):
        self.vehicles = {}
        if DustCart.objects.filter(dumping_ground=bi).exists:
            for dc in DustCart.objects.filter(dumping_ground=bi):
                vehicles[dc] = VehicleDataContainer(
                    instance=dc, citizens=citizens, citizens_in_city=citizens_in_city
                )

    def _create_data_for_animal_farm(self, bi):
        cattle_query = Cattle.objects.filter(farm=bi)
        if cattle_query:
            self.cattle = list(cattle_query).pop()
        else:
            self.cattle = []

    def _create_data_for_trade_district(self, bi):
        self.people_in_charge = 0
        for model in [
            model
            for model in apps.get_app_config("company_engine").get_models()
            if issubclass(model, Company) and model is not Company
        ]:
            if model.objects.filter(trade_district=bi).exists():
                for instance in model.objects.filter(trade_district=bi):
                    self.people_in_charge += instance.employee.count()


class CompaniesDataContainer(DataContainersWithEmployees):
    def __init__(self, instance, citizens, citizens_in_city):
        self.ci = instance
        self.energy, self.energy_required = 0, 0
        self.water, self.water_required = 0, 0
        self._create_data_for_building_with_worker(instance, citizens, citizens_in_city)
        self.goods = {}
        self.semafor()
        self.create_goods_produced_by_company()
        self._calculate_operation_requirements()

    def _calculate_operation_requirements(self):
        self.water_required = len(self.all_employees) * 2
        self.energy_required = len(self.all_employees) * 4
        # DIRTY HACK - TO REMOVE
        self.water = self.water_required
        self.energy = self.energy_required

    def save_all(self):
        for good in self.goods:
            self.goods[good].save_all()

    def semafor(self):
        if isinstance(self.ci, FoodCompany):
            self.available_components = [Mass]
            self.goods_to_product = [Food]

    def _calculate_new_price(self, resource_in_company, size, price):
        return (resource_in_company.price + price) / (resource_in_company.size + size)

    def add_new_good(self, good_type, size, quality, price):
        if good_type in self.goods:
            for good_in_company in self.goods[good_type].instances:
                if good_in_company.quality == quality:
                    good_in_company.size += size
                    good_in_company.price = price
                    return
            self.goods[good_type].instances.append(
                good_type.objects.create(
                    size=size, quality=quality, price=price, company=self.ci
                )
            )
        else:
            self.goods[good_type] = ResourcesDataContainer(
                [
                    good_type.objects.create(
                        size=size, quality=quality, price=price, company=self.ci
                    )
                ]
            )

    def create_goods_produced_by_company(self):
        for good in self.goods_to_product:
            if good.objects.filter(company=self.ci).exists():
                self.goods[good] = ResourcesDataContainer(
                    instances_list=list(good.objects.filter(company=self.ci))
                )


class ResourcesDataContainer:
    def __init__(self, instances_list):
        self.instances = instances_list
        self.total_size = self._get_total_size()
        self.avg_quality = self._get_avg_quality()
        self.avg_price = self._get_avg_price()

    def _get_total_size(self):
        return sum([x.size for x in self.instances])

    def _get_avg_quality(self):
        return sum([x.quality for x in self.instances]) / len(self.instances)

    def _get_avg_price(self):
        return sum([x.price for x in self.instances]) / len(self.instances)

    def save_all(self):
        for good in self.instances:
            if good.size > 0:
                good.save()
            elif good.id is not None and good.size == 0:
                good.delete()


class MarketDataContainer:
    def __init__(self, instance):
        self.mi = instance
        self.resources = {}
        self.create_resources_in_market(instance)

    def create_resources_in_market(self, instance):
        subclasses = (
            model
            for model in apps.get_app_config("resources").get_models()
            if issubclass(model, MarketResource) and model is not MarketResource
        )
        for sub in subclasses:
            if sub.objects.filter(market=instance).exists():
                self.resources[sub] = ResourcesDataContainer(
                    list(sub.objects.filter(market=instance))
                )

    def save_all(self):
        for good in self.resources:
            self.resources[good].save_all()

    def _calculate_new_price(self, resource_in_market, size, price):
        return (resource_in_market.price + price) / (resource_in_market.size + size)

    def add_new_resource(self, resource_type, size, quality, price, market):
        if resource_type in self.resources:
            for resource_in_market in self.resources[resource_type].instances:
                if quality == resource_in_market.quality:
                    resource_in_market.size += size
                    resource_in_market.price = self._calculate_new_price(
                        resource_in_market, size, price
                    )
                    return
            self.resources[resource_type].instances.append(
                resource_type.objects.create(
                    size=size, quality=quality, price=price, market=market
                )
            )
        else:
            self.resources[resource_type] = ResourcesDataContainer(
                [
                    resource_type.objects.create(
                        size=size, quality=quality, price=price, market=market
                    )
                ]
            )


class CityFieldDataContainer:
    def __init__(self, instance):
        self.row_col = (instance.row, instance.col)
        self.pollution = instance.pollution


class VehicleDataContainer(DataContainersWithEmployees):
    def __init__(self, instance, citizens, citizens_in_city):
        self.bi = instance
        self._create_data_for_building_with_worker(instance, citizens, citizens_in_city)


class CitizenDataContainer:
    def __init__(self, instance, to_save, residentials):
        self.ci = instance
        self.educations = self.ci.education_set.all()
        self.professions = self.ci.profession_set.all()
        to_save += list(self.educations) + list(self.professions)
        current_educations = [e for e in self.educations if e.if_current is True]
        current_professions = [p for p in self.professions if p.if_current is True]
        self.current_education = (
            current_educations.pop() if current_educations else None
        )
        self.current_profession = (
            current_professions.pop() if current_professions else None
        )
        self.home = (
            [r for r in residentials if r.bi == self.ci.resident_object].pop()
            if self.ci.resident_object
            else None
        )
        self.salary_expectation = self.__calculate_salary_expectation()

    def __calculate_salary_expectation(self) -> float:
        return (
            round(
                self.home.rent
                * ((1 + self.current_profession.proficiency) * len(self.educations)),
                2,
            )
            if self.home and self.current_profession
            else 0
        )


class FamilyDataContainer:
    def __init__(self, instance, citizens, residents):
        self.fi = (instance,)
        self.members = [m for m in citizens if m.family == instance]
        self.parents = [
            m for m in self.members if m.partner_id in [m.id for m in self.members]
        ]
        self.place_of_living = self.__give_place_of_living(residents)
        self.cash = sum([m.cash for m in self.members])

    def __give_place_of_living(self, residents):
        place_of_livings = [
            r for r in residents if r.bi in [p.resident_object for p in self.members]
        ]
        return place_of_livings.pop() if place_of_livings else None

    def pay_rent(self, city, profile):
        if self.place_of_living:
            if self.place_of_living.rent <= self.cash:
                guard = 0
                while self.place_of_living.rent > guard:
                    for member in (m for m in self.members if m.age >= 18):
                        if member.cash > 0:
                            member.cash -= 1
                            self.cash -= 1
                            guard += 1
                import decimal

                tax_diff = guard * profile.standard_residential_zone_taxation
                self.place_of_living.bi.cash += decimal.Decimal(guard - tax_diff)
                city.cash += decimal.Decimal(tax_diff)
            else:
                for member in self.members:
                    member.resident_object = None
                self.place_of_living = None


class ResidentialDataContainer:
    def __init__(self, instance, fields_data, profile):
        self.bi = instance
        self.profile = profile
        self.trash = [
            trash for trash in instance.trash.all() if instance.trash.all().exists()
        ]
        self.row_col_cor = (instance.city_field.row, instance.city_field.col)
        self.people_in_charge = instance.resident.count()
        self.__create_data_for_residential(fields_data)

    def __create_data_for_residential(self, fields_data):
        divider = 2.5
        basic_rent = (
            (
                self.bi.build_cost
                * (self.profile.standard_residential_zone_taxation / divider)
            )
            / self.bi.max_population
            if self.bi.build_cost and self.bi.max_population
            else 0
        )
        taxation = basic_rent * self.profile.standard_residential_zone_taxation
        pollution_penalty = (
            basic_rent * (fields_data[self.bi.city_field].pollution / 100)
            if fields_data[self.bi.city_field].pollution
            else 0
        )
        self.rent = (basic_rent - pollution_penalty) + taxation


class BuildingDataContainer(DataContainersWithEmployees):
    def __init__(self, instance, citizens_data, citizens, profile, vehicles):
        self.bi = instance
        self.profile = profile
        self.trash = [
            trash for trash in instance.trash.all() if instance.trash.all().exists()
        ]
        self.row_col_cor = (instance.city_field.row, instance.city_field.col)
        self.semafor(citizens, citizens_data, vehicles)

    def semafor(self, citizens, citizens_data, vehicles):
        if isinstance(self.bi, BuldingsWithWorkes):
            self._create_data_for_building_with_worker(self.bi, citizens, citizens_data)
        if isinstance(self.bi, AnimalFarm):
            self._create_data_for_animal_farm(self.bi)
        if isinstance(self.bi, TradeDistrict):
            self._create_data_for_trade_district(self.bi)
        if isinstance(self.bi, DumpingGround):
            self._create_data_for_dumping_ground(
                self.bi, citizens, citizens_data, vehicles
            )

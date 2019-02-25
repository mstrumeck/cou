from abc import ABC

from django.apps import apps

from city_engine.models import (
    PowerPlant,
    SewageWorks,
    Waterworks
)
from resources.models import MarketResource


class DataContainersWithEmployees(ABC):

    def _calculate_wage_for_employees(
        self, wage_of_employees, total_wages, total_level, employees, employee_needed
    ):
        if employee_needed:
            total_wages.append(wage_of_employees)
            total_level.append(
                (
                    sum(
                        [
                            e.current_profession.proficiency
                            if e.current_profession
                            else 0
                            for e in employees
                        ]
                    )
                    / float(employee_needed)
                )
                * wage_of_employees
            )

    def employee_productivity(self, citizens_data):
        wages = []
        total = []
        self._calculate_wage_for_employees(
            wage_of_employees=1,
            total_wages=wages,
            total_level=total,
            employees=[citizens_data[e] for e in self.elementary_employees],
            employee_needed=self.bi.elementary_employee_needed,
        )
        self._calculate_wage_for_employees(
            wage_of_employees=2,
            total_wages=wages,
            total_level=total,
            employees=[citizens_data[e] for e in self.college_employees],
            employee_needed=self.bi.college_employee_needed,
        )
        self._calculate_wage_for_employees(
            wage_of_employees=3,
            total_wages=wages,
            total_level=total,
            employees=[citizens_data[e] for e in self.phd_employees],
            employee_needed=self.bi.phd_employee_needed,
        )
        if wages and total:
            return float(sum(total)) / float(sum(wages))
        else:
            return 0

    def _get_productivity(self, citizens):
        employee_productivity = self.employee_productivity(citizens)
        if employee_productivity == 0:
            return 0
        else:
            t = [
                employee_productivity,
                self._energy_productivity(),
                self._water_productivity(),
            ]
            return float(sum(t)) / float(len(t))

    def _water_productivity(self):
        if self.water is 0:
            return 0.0
        else:
            return float(self.water) / float(self.bi.water_required)

    def _energy_productivity(self):
        if self.energy is 0:
            return 0.0
        else:
            return float(self.energy) / float(self.energy_required)

    def _get_clean_water_total_production(self, citizens_data):
        if self.employee_productivity(citizens_data) == 0:
            return 0
        else:
            t = [
                    self.employee_productivity(citizens_data),
                    self._energy_productivity(),
                ]
            if self.raw_water <= self.raw_water_required:
                # return data_container.raw_water
                return int(self.raw_water * (float(sum(t)) / float(len(t))))

    def allocate_resources_in_target(self, target, data):
        if isinstance(self.bi, PowerPlant):
            self.allocate_energy_in_target(target)
        if isinstance(self.bi, Waterworks):
            self.allocate_raw_water_in_target(target, data.citizens_in_city)
        if isinstance(self.bi, SewageWorks):
            self.allocate_clean_water_in_target(target)

    def allocate_clean_water_in_target(self, target):
        if (
            hasattr(target, "water")
            and not isinstance(target, SewageWorks)
            and not isinstance(target, Waterworks)
        ):
            while (
                target.water_required > target.water
                and self.total_production > 0
                and self.clean_water_allocated < self.total_production
            ):
                self.clean_water_allocated += 1
                target.water += 1

    def allocate_raw_water_in_target(self, target, citizens_in_city):
        if hasattr(target, "raw_water"):
            while (
                target.raw_water_required > target.raw_water
                and self.raw_water_allocated < self.total_production
            ):
                self.raw_water_allocated += 1
                target.raw_water += 1
            target.total_production = target._get_clean_water_total_production(citizens_in_city)

    def allocate_energy_in_target(self, target):
        if hasattr(target, "energy") and not isinstance(target, PowerPlant):
            while (
                target.energy_required > target.energy
                and self.energy_allocated < self.total_production
            ):
                self.energy_allocated += 1
                target.energy += 1


class CompaniesDataContainer(DataContainersWithEmployees):
    def __init__(self, instance, citizens, citizens_data, semafor):
        self.bi = instance
        self.energy, self.energy_required = 0, 0
        self.water, self.water_required = 0, 0
        self.row_col_cor = (instance.trade_district.city_field.row, instance.trade_district.city_field.col)
        self.goods = {}
        semafor.select_semafor_schema(self, citizens, citizens_data)
        self.create_goods_produced_by_company()
        self._calculate_operation_requirements()

    def _calculate_operation_requirements(self):
        self.water_required = len(self.all_employees) * 2
        self.energy_required = len(self.all_employees) * 4

    def save_all(self):
        for good in self.goods:
            self.goods[good].save_all()

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
                    size=size, quality=quality, price=price, company=self.bi
                )
            )
        else:
            self.goods[good_type] = ResourcesDataContainer(
                [
                    good_type.objects.create(
                        size=size, quality=quality, price=price, company=self.bi
                    )
                ]
            )

    def create_goods_produced_by_company(self):
        for good in self.goods_to_product:
            if good.objects.filter(company=self.bi).exists():
                self.goods[good] = ResourcesDataContainer(
                    instances_list=list(good.objects.filter(company=self.bi))
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
    def __init__(self, instance):
        self.bi = instance


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
        self.raw_water = 0
        self.energy, self.energy_required = 0, 0
        self.water, self.water_required = 0, 0
        self.profile = profile
        self.trash = [
            trash for trash in instance.trash.all() if instance.trash.all().exists()
        ]
        self.row_col_cor = (instance.city_field.row, instance.city_field.col)
        self.people_in_charge = instance.resident.count()
        self.__create_data_for_residential(fields_data)
        self.__resources_demand()

    def __resources_demand(self):
        self.water_required = self.people_in_charge * 3
        self.energy_required = self.people_in_charge * 3

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
    def __init__(self, instance, citizens_data, citizens, profile, vehicles, semafor):
        self.bi = instance
        self.raw_water = 0
        self.energy, self.energy_required = 0, 0
        self.water, self.water_required = 0, 0
        self.profile = profile
        self.trash = [
            trash for trash in instance.trash.all() if instance.trash.all().exists()
        ]
        self.row_col_cor = (instance.city_field.row, instance.city_field.col)
        semafor.select_semafor_schema(self, citizens, citizens_data, vehicles)

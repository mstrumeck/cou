from city_engine.models import Building, CityField, BuldingsWithWorkes, Vehicle, PowerPlant,\
    Waterworks, SewageWorks, Residential, StandardLevelResidentialZone
from cou.global_var import ELEMENTARY, COLLEGE, PHD
from citizen_engine.models import Family
from decimal import getcontext


class CityFieldDataContainer:
    def __init__(self, instance):
        self.row_col = (instance.row, instance.col)
        self.pollution = instance.pollution


class VehicleDataContainer:
    def __init__(self, instance, citizens, citizens_in_city):
        self.bi = instance
        self.citizens = citizens
        self.citizens_in_city = citizens_in_city
        self.people_in_charge = instance.resident.count() if isinstance(instance,
                                                                        Residential) else instance.employee.count()
        self.__create_data_for_building_with_worker()

    def __create_data_for_building_with_worker(self):
        self.max_employees = sum([self.bi.elementary_employee_needed,
                                  self.bi.college_employee_needed,
                                  self.bi.phd_employee_needed])

        self.elementary_employees = [e for e in self.citizens
                                     if e.workplace_object == self.bi
                                     and self.citizens_in_city[e].current_profession.education == ELEMENTARY]

        self.elementary_vacancies = self.bi.elementary_employee_needed - len(
            [e for e in self.citizens if e.workplace_object == self.bi
             and self.citizens_in_city[e].current_profession.education == ELEMENTARY])

        self.college_employees = [e for e in self.citizens
                                  if e.workplace_object == self.bi
                                  and self.citizens_in_city[e].current_profession.education == COLLEGE]

        self.college_vacancies = self.bi.college_employee_needed - len(
            [e for e in self.citizens if e.workplace_object == self.bi
             and self.citizens_in_city[e].current_profession.education == COLLEGE])

        self.phd_employees = [e for e in self.citizens
                              if e.workplace_object == self.bi
                              and self.citizens_in_city[e].current_profession.education == PHD]

        self.phd_vacancies = self.bi.phd_employee_needed - len(
            [e for e in self.citizens if e.workplace_object == self.bi
             and self.citizens_in_city[e].current_profession.education == PHD])

        self.all_employees = self.elementary_employees + self.college_employees + self.phd_employees


class CitizenDataContainer:
    def __init__(self, instance, to_save, residentials):
        self.ci = instance
        self.educations = self.ci.education_set.all()
        self.professions = self.ci.profession_set.all()
        to_save += list(self.educations) + list(self.professions)
        current_educations = [e for e in self.educations if e.if_current is True]
        current_professions = [p for p in self.professions if p.if_current is True]
        self.current_education = current_educations.pop() if current_educations else None
        self.current_profession = current_professions.pop() if current_professions else None
        self.home = [r for r in residentials if r.bi == self.ci.resident_object].pop() if self.ci.resident_object else None
        self.salary_expectation = self.__calculate_salary_expectation()

    def __calculate_salary_expectation(self) -> float:
        return self.home.rent * ((1 + self.current_profession.proficiency) * len(self.educations)) \
            if self.home and self.current_profession else 0


class FamilyDataContainer:
    def __init__(self, instance, citizens, residents):
        self.fi = instance,
        self.members = [m for m in citizens if m.family == instance]
        self.parents = [m for m in self.members if m.partner_id in [m.id for m in self.members]]
        self.place_of_living = self.__give_place_of_living(residents)
        self.cash = sum([m.cash for m in self.members])

    def __give_place_of_living(self, residents):
        place_of_livings = [r for r in residents if r.bi in [p.resident_object for p in self.members]]
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
    def __init__(self, instance, citizens_data, citizens, fields_data, profile):
        self.bi = instance
        self.citizens_in_city = citizens_data
        self.citizens = citizens
        self.field_data = fields_data
        self.profile = profile
        self.trash = [trash for trash in instance.trash.all() if instance.trash.all().exists()]
        self.row_col_cor = (instance.city_field.row, instance.city_field.col)
        self.people_in_charge = instance.resident.count() if isinstance(instance, Residential) else instance.employee.count()
        self.__create_data_for_residential()

    def __create_data_for_residential(self):
        divider = 2.5
        basic_rent = (self.bi.build_cost * (self.profile.standard_residential_zone_taxation/divider))\
                     / self.bi.max_population if self.bi.build_cost and self.bi.max_population else 0
        taxation = basic_rent * self.profile.standard_residential_zone_taxation
        pollution_penalty = basic_rent * (self.field_data[self.bi.city_field].pollution / 100) \
            if self.field_data[self.bi.city_field].pollution else 0
        self.rent = (basic_rent - pollution_penalty) + taxation


class BuildingDataContainer:
    def __init__(self, instance, citizens_data, citizens, fields_data, profile):
        self.bi = instance
        self.citizens_in_city = citizens_data
        self.citizens = citizens
        self.field_data = fields_data
        self.profile = profile
        self.trash = [trash for trash in instance.trash.all() if instance.trash.all().exists()]
        self.row_col_cor = (instance.city_field.row, instance.city_field.col)
        self.people_in_charge = instance.resident.count() if isinstance(instance, Residential) else instance.employee.count()
        self.semafor()

    def semafor(self):
        if isinstance(self.bi, BuldingsWithWorkes):
            self.__create_data_for_building_with_worker()

    def __create_data_for_building_with_worker(self):
        self.max_employees = sum([self.bi.elementary_employee_needed,
                                  self.bi.college_employee_needed,
                                  self.bi.phd_employee_needed])

        self.elementary_employees = [e for e in self.citizens
                                     if e.workplace_object == self.bi
                                     and self.citizens_in_city[e].current_profession.education == ELEMENTARY]

        self.elementary_vacancies = self.bi.elementary_employee_needed - len(
            [e for e in self.citizens if e.workplace_object == self.bi
             and self.citizens_in_city[e].current_profession.education == ELEMENTARY])

        self.college_employees = [e for e in self.citizens
                                     if e.workplace_object == self.bi
                                     and self.citizens_in_city[e].current_profession.education == COLLEGE]

        self.college_vacancies = self.bi.college_employee_needed - len(
            [e for e in self.citizens if e.workplace_object == self.bi
             and self.citizens_in_city[e].current_profession.education == COLLEGE])

        self.phd_employees = [e for e in self.citizens
                              if e.workplace_object == self.bi
                              and self.citizens_in_city[e].current_profession.education == PHD]

        self.phd_vacancies = self.bi.phd_employee_needed - len(
            [e for e in self.citizens if e.workplace_object == self.bi
             and self.citizens_in_city[e].current_profession.education == PHD])

        self.all_employees = [w for w in self.citizens if w.workplace_object == self.bi]

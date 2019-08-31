import decimal
import random
from itertools import chain


class TempCitizen:
    def __init__(self, instance, to_save, home, diseases, workplace):
        self.instance = instance
        self.workplace = workplace
        self.educations = self.instance.education_set.all()
        self.professions = self.instance.profession_set.all()
        to_save.extend(list(chain(self.educations, self.professions)))
        current_educations = [e for e in self.educations if e.if_current is True]
        current_professions = [p for p in self.professions if p.if_current is True]
        self.current_education = (current_educations.pop() if current_educations else None)
        self.current_profession = (current_professions.pop() if current_professions else None)
        self.home = home
        self.salary_expectation = self._calculate_salary_expectation()
        self.diseases = diseases

    def change_citizen_into_criminal(self):
        self.current_profession.if_current = False
        self.workplace = None
        self.current_profession = self.instance.create_criminal_profession()

    def is_become_a_criminal(self):
        return random.random() > self._probability_of_become_a_criminal()

    def _probability_of_become_a_criminal(self):
        education = self.get_avg_all_edu_effectiveness(3)
        pollutions = self._get_sum_of_pollutions()
        sum_of_all_trashes = sum([trash.size for trash in self._get_list_of_trashes()])
        plus_factors = education + self.instance.health
        minus_factors = (pollutions + sum_of_all_trashes) / 10.00
        factor_if_homeless = self._is_factor_exist(self.home)
        factor_if_unemployed = self._is_factor_exist(self.workplace)
        return plus_factors - (minus_factors + factor_if_unemployed + factor_if_homeless)

    def _is_factor_exist(self, factor):
        return -0.25 if factor else 0.25

    def _get_list_of_trashes_from_temp_object(self, obj):
        if obj:
            return list(chain(obj.temp_trash, obj.trash))
        return []

    def _get_list_of_trashes(self):
        return list(chain(
            self._get_list_of_trashes_from_temp_object(self.home),
            self._get_list_of_trashes_from_temp_object(self.workplace)
        ))

    def _calculate_salary_expectation(self) -> float:
        home_rent = self.home.rent if self.home else 0
        return (round(home_rent * ((1 + self.current_profession.proficiency) * len(self.educations)), 2, )
                if self.home and self.current_profession else 0)

    def probability_of_being_sick(self):
        chance_to_get_sick = self._get_chance_to_get_sick()
        if random.random() > chance_to_get_sick:
            self.instance.create_disease(self.diseases, chance_to_get_sick)

    def get_avg_all_edu_effectiveness(self, divisor=None):
        if divisor:
            return sum([edu.effectiveness for edu in self.educations]) / divisor
        return sum([edu.effectiveness for edu in self.educations]) / len(self.educations)

    def _get_chance_to_get_sick(self):
        base = self.instance.health + self.get_wage_avg_all_edu_effectiveness()
        pollution = self.instance.health * self._get_sum_of_pollutions()
        age = self.instance.health * (self.instance.age / 100.00)
        return base - pollution - age

    def _get_pollution_from_place_of_living(self):
        return self.home.field.pollution if self.home else 0

    def _get_pollution_from_workplace(self):
        return self.workplace.pollution_calculation() if self.workplace else 0

    def _get_sum_of_pollutions(self):
        return sum([self._get_pollution_from_place_of_living(), self._get_pollution_from_workplace()])/100.00

    def get_wage_avg_all_edu_effectiveness(self):
        avg_with_wage_for_educations = 6
        return sum([edu.effectiveness for edu in self.educations]) / avg_with_wage_for_educations


class TempFamily:
    def __init__(self, instance, citizens, residents):
        self.fi = instance
        self.members = [m for m in citizens if m.family == instance]
        self.parents = [m for m in self.members if m.partner_id in [m.id for m in self.members]]
        self.place_of_living = self.__give_place_of_living(residents)
        self.cash = sum([m.cash for m in self.members])

    def __give_place_of_living(self, residents):
        place_of_livings = [r for r in residents if r.instance in [p.resident_object for p in self.members]]
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

                tax_diff = guard * profile.standard_residential_zone_taxation
                self.place_of_living.instance.cash += decimal.Decimal(guard - tax_diff)
                city.cash += decimal.Decimal(tax_diff)
            else:
                for member in self.members:
                    member.resident_object = None
                self.place_of_living = None

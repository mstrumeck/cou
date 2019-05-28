import decimal
import random

import citizen_engine.models as ce_models


class TempCitizen:
    def __init__(self, instance, to_save, home, diseases):
        self.instance = instance
        self.educations = self.instance.education_set.all()
        self.professions = self.instance.profession_set.all()
        to_save += list(self.educations) + list(self.professions)
        current_educations = [e for e in self.educations if e.if_current is True]
        current_professions = [p for p in self.professions if p.if_current is True]
        self.current_education = (current_educations.pop() if current_educations else None)
        self.current_profession = (current_professions.pop() if current_professions else None)
        self.home = home
        self.salary_expectation = self._calculate_salary_expectation()
        self.diseases = diseases

    def _calculate_salary_expectation(self) -> float:
        home_rent = self.home.rent if self.home else 0
        return (round(home_rent * ((1 + self.current_profession.proficiency) * len(self.educations)), 2,)
                if self.home and self.current_profession else 0)

    def probability_of_being_sick(self):
        chance_to_get_sick = self._get_chance_to_get_sick()
        if random.random() > chance_to_get_sick:
            disease = ce_models.Disease.objects.create(
                citizen=self.instance,
                is_fatal=random.choice([True, False]) if chance_to_get_sick < 0.35 else False)
            self.diseases.append(disease)

    def get_avg_all_edu_effectiveness(self):
        return sum([edu.effectiveness for edu in self.educations]) / len(self.educations)

    def _get_chance_to_get_sick(self):
        base = self.instance.health + self.get_wage_avg_all_edu_effectiveness()
        pollution = self.instance.health * self._get_sum_of_pollutions()
        age = self.instance.health * (self.instance.age/100.00)
        return base - pollution - age

    def _get_pollution_from_place_of_living(self):
        return self.instance.resident_object.city_field.pollution if self.instance.resident_object else random.randrange(20)

    def _get_pollution_from_workplace(self):
        return self.instance.workplace_object.city_field.pollution if self.instance.workplace_object else 0

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
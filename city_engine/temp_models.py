import random

import itertools

from cou.global_var import COLLEGE, ELEMENTARY, PHD


class TempTrash:
    def __init__(self, size, owner):
        self.size = size
        self.owner = owner

    def delete(self):
        del self


class TempBuild:
    def __init__(self, instance, profile):
        self.instance = instance
        self.profile = profile
        self.energy, self.energy_required = 0, 0
        self.water, self.water_required = 0, 0
        self.row_col_cor = self._get_row_col_cor()
        self.trash = [trash for trash in instance.trash.all() if instance.trash.all().exists()]
        self.temp_trash = []
        self.is_in_fire = False
        self.fire_prevention = 0.0
        self.criminal_prevention = 0.0
        self.pollution_rate = 0.0

    def convert_temp_trash_to_perm(self):
        for t in self.temp_trash:
            self.trash.append(self.instance.trash.create(size=t.size, time=1))

    def create_trash(self):
        if self.trash_calculation():
            self.temp_trash.append(TempTrash(size=self.trash_calculation(), owner=self))

    def trash_calculation(self):
        return float(self.pollution_calculation()) * float(self.pollution_rate)

    def pollution_calculation(self):
        return self.pollution_rate * self.people_in_charge

    def _get_sum_of_edu_avg_effectiveness_with_wages(self, citizens):
        return sum([c.get_wage_avg_all_edu_effectiveness() for c in citizens])

    def _get_sum_of_edu_avg_effectiveness(self, citizens):
        return sum([c.get_avg_all_edu_effectiveness() for c in citizens])

    def set_in_fire(self):
        self.is_in_fire = True

    def probability_of_fire(self):
        fire_factors = self._get_fire_factors()
        fire_probability_divisor = len(fire_factors) * 2
        fire_probability = sum(fire_factors) / fire_probability_divisor
        base_probability_of_fire = 0.6
        if random.random() < (base_probability_of_fire - fire_probability):
            self.set_in_fire()

    def _get_row_col_cor(self):
        return (self.instance.city_field.row, self.instance.city_field.col)


class DataContainersWithEmployees(TempBuild):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile)
        self.market = market
        self.workers_costs = 0
        self.pollution_rate = 0.4
        self.max_employees = sum(
            [self.instance.elementary_employee_needed,
             self.instance.college_employee_needed,
             self.instance.phd_employee_needed]
        )

    def create_employess_data(self, employees):
        self.elementary_employees = self.get_employees_by_education(employees, (ELEMENTARY, "None"))
        self.college_employees = self.get_employees_by_education(employees, (COLLEGE, ))
        self.phd_employees = self.get_employees_by_education(employees, (PHD, ))
        self.elementary_vacancies = self.instance.elementary_employee_needed - len(self.elementary_employees)
        self.college_vacancies = self.instance.college_employee_needed - len(self.college_employees)
        self.phd_vacancies = self.instance.phd_employee_needed - len(self.phd_employees)
        self.all_people_in_building = (self.elementary_employees + self.college_employees + self.phd_employees)
        self.people_in_charge = len(self.all_people_in_building)

    def update_proficiency_of_profession_for_employees(self):
        for employee in self.all_people_in_building:
            employee.current_profession.update_proficiency(employee)

    def _get_fire_factors(self):
        return [self._get_productivity(), self._get_quality() / 100.00, self.fire_prevention]

    def _get_quality(self, num_of_employee_categories=3):
        total = []
        e = [
            (self.elementary_employees, self.instance.elementary_employee_needed),
            (self.college_employees, self.instance.college_employee_needed),
            (self.phd_employees, self.instance.phd_employee_needed)
        ]
        for employees, needed_employees in e:
            if employees and needed_employees:
                total.append(self._get_sum_of_edu_avg_effectiveness(employees) / needed_employees / num_of_employee_categories)
        return round(100 * sum(total))

    def wage_payment(self, city):
        import decimal

        total_payment = []
        for e in self.all_people_in_building:
            se = decimal.Decimal(e.salary_expectation)
            e.instance.cash += se
            city.cash -= se
            total_payment.append(se)
        self.workers_costs = sum(total_payment)

    def get_employees_by_education(self, employees, education_level):
        return [employees[e] for e in employees if e.workplace_object == self.instance
                and employees[e].current_profession.education in education_level]

    def _get_productivity(self):
        employee_productivity = self.employee_productivity()
        if employee_productivity == 0:
            return 0
        else:
            t = [employee_productivity, self._energy_productivity(), self._water_productivity()]
            return float(sum(t)) / float(len(t))

    def _water_productivity(self):
        if self.water is 0:
            return 0.0
        else:
            return float(self.water) / float(self.water_required)

    def _energy_productivity(self):
        if self.energy is 0:
            return 0.0
        else:
            return float(self.energy) / float(self.energy_required)

    def _calculate_wage_for_employees(
        self, wage_of_employees, total_wages, total_level, employees, employee_needed
    ):
        if employee_needed:
            total_wages.append(wage_of_employees)
            total_level.append(
                (sum(
                    [e.current_profession.proficiency if e.current_profession and not e.diseases else 0 for e in employees]) / float(employee_needed)) * wage_of_employees
            )

    def employee_productivity(self):
        wages = []
        total = []
        self._calculate_wage_for_employees(
            wage_of_employees=1,
            total_wages=wages,
            total_level=total,
            employees=self.elementary_employees,
            employee_needed=self.instance.elementary_employee_needed,
        )
        self._calculate_wage_for_employees(
            wage_of_employees=2,
            total_wages=wages,
            total_level=total,
            employees=self.college_employees,
            employee_needed=self.instance.college_employee_needed,
        )
        self._calculate_wage_for_employees(
            wage_of_employees=3,
            total_wages=wages,
            total_level=total,
            employees=self.phd_employees,
            employee_needed=self.instance.phd_employee_needed,
        )
        if wages and total:
            return float(sum(total)) / float(sum(wages))
        else:
            return 0


class TempResidential(TempBuild):
    def __init__(self, instance, profile, field):
        super().__init__(instance, profile)
        self.field = field
        self.rent = self._get_rent()
        self.pollution_rate = 0.4

    def fill_data_by_residents(self, residents):
        self.all_people_in_building = residents
        self.people_in_charge = len(residents)
        self.water_required = self._resources_demand()
        self.energy_required = self._resources_demand()

    def _get_fire_factors(self):
        return [self._get_quality_of_education(), self.fire_prevention]

    def get_citizens_by_education(self, citizens, education_level):
        return [c for c in citizens if c.instance.resident_object == self.instance and c.instance.edu_title in education_level]

    def _get_quality_of_education(self):
        total = []
        wages = []
        e = [
            (self.get_citizens_by_education(self.all_people_in_building, (ELEMENTARY, "None")), 3),
            (self.get_citizens_by_education(self.all_people_in_building, (COLLEGE,)), 2),
            (self.get_citizens_by_education(self.all_people_in_building, (PHD,)), 1)
        ]
        for employees, wage in e:
            if employees:
                wages.append(wage)
                total.append(self._get_sum_of_edu_avg_effectiveness(employees) / self.people_in_charge)
        if wages:
            return sum(total) / float(max(wages))
        return 0

    def _resources_demand(self):
        return self.people_in_charge * 3

    def _get_rent(self):
        divider = 2.5
        basic_rent = (
            (self.instance.build_cost * (self.profile.standard_residential_zone_taxation / divider))
            / self.instance.max_population
            if self.instance.build_cost and self.instance.max_population
            else 0
        )
        taxation = basic_rent * self.profile.standard_residential_zone_taxation
        pollution_penalty = (
            basic_rent * self.field.pollution
            if self.field.pollution
            else 0
        )
        return (basic_rent - pollution_penalty) + taxation


class TempDistrict:
    def __init__(self, instance, profile, companies, support_buildings):
        self.instance = instance
        self.profile = profile
        self.companies = companies
        self.support_buildings = support_buildings
        self.row_col_cor = self._get_row_col_cor()
        self.trash = []
        self.temp_trash = []
        self.fire_prevention = 0.0

    def allocate_resources(self):
        if self.companies or self.support_buildings:
            num_of_sb = len(self.support_buildings) if self.support_buildings else 0
            num_of_c = len(self.companies) if self.companies else 0
            energy_to_allocate = int(self.energy / (num_of_sb + num_of_c))
            water_to_allocate = int(self.water / (num_of_sb + num_of_c))
            for b in itertools.chain(self.companies.values(), self.support_buildings.values()):
                b.energy = energy_to_allocate
                b.water = water_to_allocate

    def convert_temp_trash_to_perm(self):
        for t in self.temp_trash:
            self.trash.append(self.instance.trash.create(size=t.size, time=1))

    def create_trash(self):
        if self.companies:
            for c in self.companies.values():
                if c.trash_calculation():
                    self.temp_trash.append(TempTrash(size=c.trash_calculation(), owner=c))

        if self.support_buildings:
            for s in self.support_buildings.values():
                if s.trash_calculation():
                    self.temp_trash.append(TempTrash(size=s.trash_calculation(), owner=s))

    def trash_calculation(self):
        return self.pollution_calculation() * self.pollution_rate

    def pollution_calculation(self):
        return self.pollution_rate * self.people_in_charge

    def _get_data_from_support_buildings(self):
        if self.support_buildings:
            return sum([sb.people_in_charge for sb in self.support_buildings.values()]),\
                   sum([sb.water_required for sb in self.support_buildings.values()]),\
                   sum([sb.energy_required for sb in self.support_buildings.values()])
        return 0, 0, 0

    def _get_data_from_companies(self):
        if self.companies:
            return sum([b.people_in_charge for b in self.companies.values()]),\
                   sum([c.water_required for c in self.companies.values()]),\
                   sum([c.energy_required for c in self.companies.values()]),
        return 0, 0, 0

    def get_people_in_charge(self):
        people_in_charge_sb, water_required_sb, energy_required_sb = self._get_data_from_support_buildings()
        people_in_charge_c, water_required_c, energy_required_c = self._get_data_from_companies()
        self.people_in_charge = people_in_charge_c + people_in_charge_sb
        self.energy, self.energy_required = 0, energy_required_c + energy_required_sb
        self.water, self.water_required = 0, water_required_c + water_required_sb

    def _get_row_col_cor(self):
        return (self.instance.city_field.row, self.instance.city_field.col)

    def _get_trash(self):
        return [c.trash.all() for c in self.companies]


class TempTradeDistrict(TempDistrict):
    def __init__(self, instance, profile, companies, support_buildings=None):
        super().__init__(instance, profile, companies, support_buildings)


class TempPowerPlant(DataContainersWithEmployees):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.energy_allocated = 0

    def pollution_calculation(self):
        return (self.instance.power_nodes + self.people_in_charge) * self.pollution_rate

    def _get_total_production(self):
        if not self.employee_productivity():
            return 0
        else:
            t = [self.employee_productivity(), self._water_productivity()]
            return int(
                (float(sum(t)) / float(len(t))) * self.energy_production * self.instance.power_nodes)

    def allocate_resources_in_target(self, target):
        if hasattr(target, "energy") and not isinstance(target, TempPowerPlant):
            while (
                target.energy_required > target.energy
                and self.energy_allocated < self._get_total_production()
            ):
                self.energy_allocated += 1
                target.energy += 1


class TempWindPlant(TempPowerPlant):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.energy_production = 100
        self.max_power_nodes = 10
        self.water_required = 5


class TempCoalPlant(TempPowerPlant):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.energy_production = 200
        self.max_power_nodes = 2
        self.water_required = 20


class TempRopePlant(TempPowerPlant):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.energy_production = 150
        self.max_power_nodes = 4
        self.water_required = 20


class TempWaterTower(DataContainersWithEmployees):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.raw_water_production = 100
        self.raw_water_allocated = 0

    def allocate_resources_in_target(self, target):
        if hasattr(target, "raw_water"):
            while (
                target.raw_water_required > target.raw_water
                and self.raw_water_allocated < self._get_total_production()
            ):
                self.raw_water_allocated += 1
                target.raw_water += 1

    def _get_total_production(self):
        if not self.employee_productivity():
            return 0
        else:
            t = [
                self.employee_productivity(),
                self._energy_productivity(),
            ]
            return int(float(sum(t)) / float(len(t)) * self.raw_water_production)


class TempSewageWorks(DataContainersWithEmployees):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.raw_water_required = 1000
        self.raw_water = 0
        self.clean_water_allocated = 0

    def allocate_resources_in_target(self, target):
        if (hasattr(target, "water") and not isinstance(target, TempSewageWorks) and not isinstance(target, TempWaterTower)):
            while (
                target.water_required > target.water
                and self._get_total_production() > 0
                and self.clean_water_allocated < self._get_total_production()
            ):
                self.clean_water_allocated += 1
                target.water += 1

    def _get_total_production(self):
        if not self.employee_productivity():
            return 0
        else:
            t = [self.employee_productivity(), self._energy_productivity()]
            if self.raw_water <= self.raw_water_required:
                # return self.raw_water
                return int(self.raw_water * (float(sum(t)) / float(len(t))))


class TempDumpingGround(DataContainersWithEmployees):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.current_capacity = instance.current_space_for_trash

    def create_employess_data(self, employees):
        super().create_employess_data(employees)
        self.total_employees_capacity = self._get_total_employees_capacity()

    def _get_total_employees_capacity(self):
        return (100 * self._get_productivity()) * self.people_in_charge

    def collect_trash(self, building):
        if self.total_employees_capacity:
            for trash in building.trash:
                while self.total_employees_capacity >= self.current_capacity and trash.size > 0:
                    self.current_capacity += 1
                    trash.size -= 1
                if trash.size == 0:
                    trash.delete()

            for trash in building.temp_trash:
                while self.total_employees_capacity >= self.current_capacity and trash.size > 0:
                    self.current_capacity += 1
                    trash.size -= 1
                if trash.size <= 0:
                    building.temp_trash.remove(trash)


class TempFarm(DataContainersWithEmployees):
    pass


class TempAnimalFarm(TempFarm):
    def __init__(self, instance, profile, market, cattle):
        super().__init__(instance, profile, market)
        self.cattle = cattle


class TempClinic(DataContainersWithEmployees):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.energy_required = 10
        self.water_required = 15
        self.max_treatment_capacity = 30

    def create_employess_data(self, employees):
        super().create_employess_data(employees)
        self.current_treatment_capacity = int((self.people_in_charge / self.max_employees) * self.max_treatment_capacity)

    def work(self, list_of_buildings):
        pattern = sorted(
            list_of_buildings.values(), key=lambda x: (
                abs(x.row_col_cor[0] - self.row_col_cor[0]),
                abs(x.row_col_cor[1] - self.row_col_cor[1])
            ))
        after_treatment = []
        for b in pattern:
            if isinstance(b, TempPrison):
                for c in list(itertools.chain(b.all_people_in_building, b.prisoners)):
                    if self._check_treatment_for_citizen(c, after_treatment):
                        return
            else:
                for c in b.all_people_in_building:
                    if self._check_treatment_for_citizen(c, after_treatment):
                        return

    def _check_treatment_for_citizen(self, citizen, after_treatment):
        if citizen.diseases and citizen not in after_treatment:
            self._treat_citizen(citizen, after_treatment)
        if self.current_treatment_capacity <= 0:
            return True

    def _treat_citizen(self, c, after_treatment):
        self.current_treatment_capacity -= 1
        after_treatment.append(c)
        if self._get_productivity() > random.random():
            c.diseases[0].delete()


class TempFireStation(DataContainersWithEmployees):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.energy_required = 10
        self.water_required = 20
        self._max_fire_prevention_capacity = 15

    def ensure_fire_prevention(self, buildings_in_city):
        pattern = sorted([b for b in buildings_in_city.values() if not isinstance(b, TempFireStation)], key=lambda x: (
            abs(x.row_col_cor[0] - self.row_col_cor[0]),
            abs(x.row_col_cor[1] - self.row_col_cor[1]),
        ))
        for b in pattern[:self.fire_prevention_capacity]:
            b.fire_prevention = self._get_productivity()

    def create_employess_data(self, employees):
        super().create_employess_data(employees)
        self.fire_prevention_capacity = int((self.people_in_charge / self.max_employees) * self._max_fire_prevention_capacity)

    def is_handle_with_fire(self):
        return random.random() < self._get_productivity()


class TempPoliceStation(DataContainersWithEmployees):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.energy_required = 10
        self.water_required = 10
        self._max_crime_prevention_capacity = 15

    def create_employess_data(self, employees):
        super().create_employess_data(employees)
        self.criminal_prevention_capacity = int((self.people_in_charge / self.max_employees) * self._max_crime_prevention_capacity)

    def ensure_crime_prevention(self, buildings_in_city):
        pattern = sorted(
            [b for b in buildings_in_city.values() if not isinstance(b, TempPoliceStation)],
            key=lambda x: (
                abs(x.row_col_cor[0] - self.row_col_cor[0]),
                abs(x.row_col_cor[1] - self.row_col_cor[1]),
            ))
        prevention = self._get_productivity()
        for b in pattern[:self.criminal_prevention_capacity]:
            if b.criminal_prevention < prevention:
                b.criminal_prevention = prevention


class TempPrison(DataContainersWithEmployees):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)
        self.energy_required = 20
        self.water_required = 10
        self._max_prison_capacity = 15

    def create_employess_data(self, employees):
        super().create_employess_data(employees)
        self.prison_capacity = int((self.people_in_charge / self.max_employees) * self._max_prison_capacity) - self.num_of_prisoners

    def rehabilitation_for_criminal(self, criminal):
        criminal.current_profession.proficiency -= self._get_productivity() / 100.00
        criminal.current_profession.save(update_fields=['proficiency'])

    def conduct_rehabilitation(self):
        for criminal in self.prisoners:
            self.rehabilitation_for_criminal(criminal)

    def release_criminal(self, criminal):
        criminal.instance.jail = None
        criminal.current_profession.delete()
        criminal.current_profession = None
        criminal.instance.save(update_fields=["jail"])

    def put_criminal_to_jail(self, criminal):
        criminal.instance.jail = self.instance
        criminal.instance.resident_object = None
        criminal.home = None
        criminal.instance.save(update_fields=["jail", "resident_object_id"])

    def is_has_place(self):
        return self.prison_capacity > self.num_of_prisoners

    def _resources_demand(self):
        return self.num_of_prisoners * 3

    def fill_data_by_prisoners(self, prisoners):
        self.prisoners = prisoners
        self.num_of_prisoners = len(prisoners)
        self.water_required += self._resources_demand()
        self.energy_required += self._resources_demand()

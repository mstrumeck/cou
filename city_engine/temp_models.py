import random

from cou.global_var import COLLEGE, ELEMENTARY, PHD


class TempBuild:
    def __init__(self, instance, profile):
        self.instance = instance
        self.profile = profile
        self.energy, self.energy_required = 0, 0
        self.water, self.water_required = 0, 0
        self.row_col_cor = self._get_row_col_cor()
        self.trash = [trash for trash in instance.trash.all() if instance.trash.all().exists()]
        self.is_in_fire = False
        self.fire_prevention = 0.0

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
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile)
        self.market = market
        self.workers_costs = 0
        self.max_employees = sum(
            [self.instance.elementary_employee_needed,
             self.instance.college_employee_needed,
             self.instance.phd_employee_needed]
        )
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
    def __init__(self, instance, profile):
        super().__init__(instance, profile)
        self.rent = self._get_rent()

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
            (
                self.instance.build_cost
                * (self.profile.standard_residential_zone_taxation / divider)
            )
            / self.instance.max_population
            if self.instance.build_cost and self.instance.max_population
            else 0
        )
        taxation = basic_rent * self.profile.standard_residential_zone_taxation
        pollution_penalty = (
            basic_rent * (self.instance.city_field.pollution / 100)
            if self.instance.city_field.pollution
            else 0
        )
        return (basic_rent - pollution_penalty) + taxation


class TempTradeDistrict(TempBuild):
    def __init__(self, instance, profile, building_in_district):
        super().__init__(instance, profile)
        self.building_in_district = building_in_district

    # def _create_data_for_trade_district(self, data_container):
    #     data_container.people_in_charge = 0
    #     for model in [
    #         model
    #         for model in apps.get_app_config("company_engine").get_models()
    #         if issubclass(model, Company) and model is not Company
    #     ]:
    #         if model.objects.filter(trade_district=data_container.bi).exists():
    #             for instance in model.objects.filter(trade_district=data_container.bi):
    #                 data_container.people_in_charge += instance.employee.count()


class TempPowerPlant(DataContainersWithEmployees):
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
        self.energy_allocated = 0

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
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
        self.energy_production = 100
        self.max_power_nodes = 10
        self.water_required = 5


class TempCoalPlant(TempPowerPlant):
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
        self.energy_production = 200
        self.max_power_nodes = 2
        self.water_required = 20


class TempRopePlant(TempPowerPlant):
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
        self.energy_production = 150
        self.max_power_nodes = 4
        self.water_required = 20


class TempWaterTower(DataContainersWithEmployees):
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
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
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
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
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
        self.current_capacity = instance.current_space_for_trash
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


class TempFarm(DataContainersWithEmployees):
    pass


class TempAnimalFarm(TempFarm):
    def __init__(self, instance, profile, employees, market, cattle):
        super().__init__(instance, profile, employees, market)
        self.cattle = cattle


class TempClinic(DataContainersWithEmployees):
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
        self.energy_required = 10
        self.water_required = 15
        self.max_treatment_capacity = 30
        self.current_treatment_capacity = int((self.people_in_charge / self.max_employees) * self.max_treatment_capacity)

    def work(self, list_of_buildings):
        pattern = sorted(
            [list_of_buildings[b] for b in list_of_buildings], key=lambda x: (
                abs(x.row_col_cor[0] - self.row_col_cor[0]),
                abs(x.row_col_cor[1] - self.row_col_cor[1])
            ))
        after_treatment = []
        for b in pattern:
            for c in b.all_people_in_building:
                if c.diseases and c not in after_treatment:
                    self._treat_citizen(c, after_treatment)
                if self.current_treatment_capacity <= 0:
                    return

    def _treat_citizen(self, c, after_treatment):
        self.current_treatment_capacity -= 1
        after_treatment.append(c)
        if self._get_productivity() > random.random():
            c.diseases[0].delete()


class TempFireStation(DataContainersWithEmployees):
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
        self.energy_required = 10
        self.water_required = 20
        self._max_fire_prevention_capacity = 15
        self.fire_prevention_capacity = int((self.people_in_charge / self.max_employees) * self._max_fire_prevention_capacity)

    def ensure_fire_prevention(self, buildings_in_city):
        pattern = sorted([b for b in buildings_in_city.values() if not isinstance(b, TempFireStation)], key=lambda x: (
            abs(x.row_col_cor[0] - self.row_col_cor[0]),
            abs(x.row_col_cor[1] - self.row_col_cor[1]),
        ))
        for b in pattern[:self.fire_prevention_capacity]:
            b.fire_prevention = self._get_productivity()

    def is_handle_with_fire(self):
        return True if random.random() < self._get_productivity() else False

import decimal

from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from cou.global_var import ELEMENTARY, COLLEGE, STANDARD_RESIDENTIAL_ZONE_COST_PER_RESIDENT


class Trash(models.Model):
    size = models.PositiveIntegerField(default=0)
    time = models.PositiveIntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()


class City(models.Model):
    user = models.ForeignKey(User)
    name = models.TextField(max_length=15, unique=True)
    cash = models.DecimalField(default=1000000, decimal_places=2, max_digits=20)
    trade_zones_taxation = models.FloatField(default=0.05)
    publish = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class CityField(models.Model):
    city = models.ForeignKey(City)
    col = models.PositiveIntegerField()
    row = models.PositiveIntegerField()
    pollution = models.PositiveIntegerField(default=0)


class Building(models.Model):
    city = models.ForeignKey(City)
    city_field = models.ForeignKey(CityField)
    cash = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    if_under_construction = models.BooleanField(default=True)
    build_cost = models.PositiveIntegerField(default=0)
    maintenance_cost = models.PositiveIntegerField(default=0)
    build_time = models.PositiveIntegerField()
    current_build_time = models.PositiveIntegerField(default=1)
    trash = GenericRelation(Trash)
    #Energy
    energy = models.PositiveIntegerField(default=0)
    energy_required = models.PositiveIntegerField(default=0)
    #Water
    water = models.PositiveIntegerField(default=0)
    water_required = models.PositiveIntegerField(default=0)
    #Pollution
    pollution_rate = models.FloatField(default=0.0)
    pollution_product = models.PositiveIntegerField(default=0)
    recycling = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False


class BuldingsWithWorkes(Building):
    profession_type_provided = models.CharField(default="", max_length=1)
    elementary_employee_needed = models.PositiveIntegerField(default=0)
    college_employee_needed = models.PositiveIntegerField(default=0)
    phd_employee_needed = models.PositiveIntegerField(default=0)
    employee = GenericRelation(to='citizen_engine.Citizen',
                               object_id_field='workplace_object_id',
                               content_type_field='workplace_content_type'
                               )

    def calculate_price_of_good(self, workers_costs, size_of_production):
        if workers_costs and size_of_production:
            return workers_costs/decimal.Decimal(size_of_production)
        return 0

    def wage_payment(self, city, data):
        import decimal
        total_payment = []
        for e in data.list_of_workplaces[self].all_employees:
            se = decimal.Decimal(data.citizens_in_city[e].salary_expectation)
            e.cash += se
            city.cash -= se
            total_payment.append(se)
        data.list_of_workplaces[self].workers_costs = sum(total_payment)

    def trash_calculation(self, employee):
        return float(self.pollution_calculation(employee)) * float(self.pollution_rate)

    def pollution_calculation(self, employee):
        return self.pollution_rate * float(employee)

    def update_proficiency_of_profession_for_employees(self, employees):
        for employee in employees:
            employee.current_profession.update_proficiency(employee)

    def calculate_wage_for_employees(self, wage_of_employees, total_wages, total_level, employees, employee_needed):
        if employee_needed:
            total_wages.append(wage_of_employees)
            total_level.append(
                (sum([e.current_profession.proficiency
                     if e.current_profession else 0 for e in employees])/float(employee_needed))*wage_of_employees)

    def employee_productivity(self, workplaces, citizens):
        wages = []
        total = []
        self.calculate_wage_for_employees(
            wage_of_employees=1,
            total_wages=wages,
            total_level=total,
            employees=[citizens[e] for e in workplaces[self].elementary_employees],
            employee_needed=self.elementary_employee_needed
        )
        self.calculate_wage_for_employees(
            wage_of_employees=2,
            total_wages=wages,
            total_level=total,
            employees=[citizens[e] for e in workplaces[self].college_employees],
            employee_needed=self.college_employee_needed
        )
        self.calculate_wage_for_employees(
            wage_of_employees=3,
            total_wages=wages,
            total_level=total,
            employees=[citizens[e] for e in workplaces[self].phd_employees],
            employee_needed=self.phd_employee_needed
        )
        return float(sum(total))/float(sum(wages))

    def _get_quality(self, workplaces, citizens):
        total = []
        employee_categories = ['elementary_employees', 'college_employees', 'phd_employees']
        employee_categories_needed = ['elementary_employee_needed', 'college_employee_needed', 'phd_employee_needed']
        for e_cat, e_cat_needed in zip(employee_categories, employee_categories_needed):
            employees = self._get_employee_by_appendix(workplaces, citizens, e_cat)
            if employees:
                total.append(self._get_sum_edu_effectiveness(employees) / getattr(self, e_cat_needed) / 3)
        return round(100 * sum(total))

    def _get_employee_by_appendix(self, workplaces, citizens, appendix):
        return [citizens[e] for e in getattr(workplaces[self], appendix)] if getattr(workplaces[self], appendix) else []

    def _get_avg_all_edu_effectiveness(self, citizen):
        return sum([edu.effectiveness for edu in citizen.educations])/len([edu.effectiveness for edu in citizen.educations])

    def _get_sum_edu_effectiveness(self, employee_cat):
        return sum([self._get_avg_all_edu_effectiveness(c) for c in employee_cat])

    def __water_productivity(self):
        if self.water is 0:
            return 0.0
        else:
            return float(self.water)/float(self.water_required)

    def __energy_productivity(self):
        if self.energy is 0:
            return 0.0
        else:
            return float(self.energy)/float(self.energy_required)

    def productivity(self, workplaces, citizens):
        employee_productivity = self.employee_productivity(workplaces, citizens)
        if employee_productivity == 0:
            return 0
        else:
            t = [employee_productivity, self.__energy_productivity(), self.__water_productivity()]
            return float(sum(t))/float(len(t))

    class Meta:
        abstract = True


class Residential(Building):
    name = models.CharField(max_length=20, default='Budynek Mieszkalny')
    population = models.PositiveIntegerField(default=0)
    max_population = models.PositiveIntegerField(default=0)
    build_time = models.PositiveIntegerField(default=0)
    build_cost = models.PositiveIntegerField(default=0)
    water_required = models.PositiveIntegerField(default=0)
    energy_required = models.PositiveIntegerField(default=0)
    resident = GenericRelation(to='citizen_engine.Citizen',
                               object_id_field='resident_object_id',
                               content_type_field='resident_content_type'
                               )

    class Meta:
        abstract = True

    def pollution_calculation(self, employee):
        return float(employee) * self.pollution_rate

    def trash_calculation(self, employee):
        return self.pollution_calculation(employee) * self.population


class StandardLevelResidentialZone(Residential):
    name = models.CharField(max_length=30, default="Normalna dzielnica mieszkalna")

    def self__init(self, max_population):
        self.max_population = 1 if max_population <= 0 else max_population
        self.build_time = 1 if max_population <= 4 else int(max_population/4)
        self.build_cost = STANDARD_RESIDENTIAL_ZONE_COST_PER_RESIDENT * max_population


class TradeDistrict(Building):
    name = models.CharField(default='Dzielnica handlowa', max_length=20)
    if_under_construction = models.BooleanField(default=False)
    build_time = models.PositiveIntegerField(default=0)
    current_build_time = models.PositiveIntegerField(default=0)
    pollution_rate = models.FloatField(default=1.5)
    pollution_product = models.PositiveIntegerField(default=0)

    def trash_calculation(self, employee):
        return float(self.pollution_calculation(employee)) * float(self.pollution_rate)

    def pollution_calculation(self, employee):
        return self.pollution_rate * float(employee)


class ProductionBuilding(BuldingsWithWorkes):
    name = models.CharField(max_length=20, default='Strefa przemysłowa')
    profession_type_provided = models.CharField(default="Pracownik strefy przemysłowej", max_length=30)

    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    elementary_employee_needed = models.PositiveIntegerField(default=20)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.water_required += 5
            self.energy_required += 5


class PowerPlant(BuldingsWithWorkes):
    name = models.CharField(max_length=20)
    power_nodes = models.PositiveIntegerField(default=0)
    max_power_nodes = models.PositiveIntegerField(default=1)
    energy_production = models.PositiveIntegerField(default=0)
    energy_allocated = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def pollution_calculation(self, employee):
        return (self.power_nodes + employee) * self.pollution_rate

    def allocate_resource_in_target(self, target, tp):
        if hasattr(target, 'energy') and not isinstance(target, PowerPlant):
            while target.energy_required > target.energy and tp > 0 and self.energy_allocated <= tp:
                self.energy_allocated += 1
                target.energy += 1
                tp -= 1

    def __water_productivity(self):
        if self.water is 0:
            return 0.0
        else:
            return float(self.water)/float(self.water_required)

    def total_production(self, workplaces, citizens):
        if self.employee_productivity(workplaces, citizens) == 0:
            return 0
        else:
            t = [self.employee_productivity(workplaces, citizens), self.__water_productivity()]
            return int((float(sum(t))/float(len(t))) * self.energy_production * self.power_nodes)

    def __str__(self):
        return self.name


class WindPlant(PowerPlant):
    name = models.CharField(default='Elektrownia wiatrowa', max_length=20)
    profession_type_provided = models.CharField(default="Pracownik elektrowni wiatrowej", max_length=30)
    build_time = models.PositiveIntegerField(default=3)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    pollution_rate = models.FloatField(default=1.8)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.power_nodes = 1
            self.max_power_nodes = 10
            self.energy_production = 100
            self.water_required = 20


class RopePlant(PowerPlant):
    name = models.CharField(default='Elektrownia na ropę', max_length=20)
    profession_type_provided = models.CharField(default="Pracownik elektrowni na ropę", max_length=30)
    build_time = models.PositiveIntegerField(default=5)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
    water_required = models.PositiveIntegerField(default=15)
    pollution_rate = models.FloatField(default=1.3)
    elementary_employee_needed = models.PositiveIntegerField(default=10)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.power_nodes = 1
            self.max_power_nodes = 4
            self.energy_production = 500
            self.water_required = 200


class CoalPlant(PowerPlant):
    name = models.CharField(default='Elektrownia węglowa', max_length=20)
    profession_type_provided = models.CharField(default="Pracownik elektrowni węglowej", max_length=30)
    build_time = models.PositiveIntegerField(default=4)
    build_cost = models.PositiveIntegerField(default=150)
    maintenance_cost = models.PositiveIntegerField(default=15)
    pollution_rate = models.FloatField(default=1.5)
    elementary_employee_needed = models.PositiveIntegerField(default=15)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.power_nodes = 1
            self.max_power_nodes = 4
            self.energy_production = 450
            self.water_required = 150


class Waterworks(BuldingsWithWorkes):
    name = models.CharField(max_length=20)
    raw_water_allocated = models.PositiveIntegerField(default=0)
    raw_water_production = models.PositiveIntegerField(default=0)
    pollution_rate = models.FloatField(default=0.5)

    class Meta:
        abstract = True

    def pollution_calculation(self, employee):
        return employee * self.pollution_rate

    def __energy_productivity(self):
        if self.energy is 0:
            return 0.0
        else:
            return float(self.energy)/float(self.energy_required)

    def total_production(self, workplaces, citizens):
        if self.employee_productivity(workplaces, citizens) == 0:
            return 0
        else:
            t = [self.employee_productivity(workplaces, citizens), self.__energy_productivity()]
            return int(float(sum(t))/float(len(t)) * self.raw_water_production)


class WaterTower(Waterworks):
    name = models.CharField(default='Wieża ciśnień', max_length=20)
    profession_type_provided = models.CharField(default="Pracownik wieży ciśnień", max_length=30)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=50)
    maintenance_cost = models.PositiveIntegerField(default=5)
    energy_required = models.PositiveIntegerField(default=3)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def allocate_resource_in_target(self, target, tp):
        if hasattr(target, 'raw_water'):
            while target.raw_water_required >= target.raw_water and tp > 0 and self.raw_water_allocated <= tp:
                self.raw_water_allocated += 1
                target.raw_water += 1
                tp -= 1

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.raw_water_production = 5000
            self.energy_required = 50


class SewageWorks(BuldingsWithWorkes):
    name = models.CharField(default='Oczyszczalnia ścieków', max_length=30)
    profession_type_provided = models.CharField(default="Pracownik oczyszczalni", max_length=30)
    build_time = models.PositiveIntegerField(default=2)
    build_cost = models.PositiveIntegerField(default=75)
    maintenance_cost = models.PositiveIntegerField(default=10)
    energy_required = models.PositiveIntegerField(default=5)
    pollution_rate = models.FloatField(default=2.0)
    raw_water = models.PositiveIntegerField(default=0)
    raw_water_required = models.PositiveIntegerField(default=0)
    clean_water_allocated = models.PositiveIntegerField(default=0)
    elementary_employee_needed = models.PositiveIntegerField(default=3)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.raw_water_required = 10000
            self.energy_required = 100

    def allocate_resource_in_target(self, target, tp):
        if hasattr(target, 'water') and not isinstance(target, SewageWorks) and not isinstance(target, Waterworks):
            while target.water_required >= target.water and tp > 0 and self.clean_water_allocated <= tp:
                self.clean_water_allocated += 1
                target.water += 1
                tp -= 1

    def __energy_productivity(self):
        if self.energy is 0:
            return 0.0
        else:
            return float(self.energy)/float(self.energy_required)

    def total_production(self, workplaces, citizens):
        if self.employee_productivity(workplaces, citizens) == 0:
            return 0
        else:
            try:
                t = [self.employee_productivity(workplaces, citizens), self.__energy_productivity()]
                if self.raw_water <= self.raw_water_required:
                    return self.raw_water
                    # return int(self.raw_water * (float(sum(t))/float(len(t))))
            except(ZeroDivisionError):
                return 0
        return 0


class Farm(BuldingsWithWorkes):
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
    energy_required = models.PositiveIntegerField(default=10)
    water_required = models.PositiveIntegerField(default=20)
    elementary_employee_needed = models.PositiveIntegerField(default=10)

    time_to_grow_from = models.PositiveIntegerField(default=0)
    time_to_grow_to = models.PositiveIntegerField(default=0)
    accumulate_harvest = models.FloatField(default=0)
    accumulate_harvest_costs = models.FloatField(default=0)
    max_harvest = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    @classmethod
    def _get_veg_info(cls):
        return cls.VEG_TYPE[0], cls.VEG_TYPE[1]

    def update_harvest(self, turn, data):
        if turn >= self.time_to_grow_from and turn < self.time_to_grow_to:
            harvest_size = self.max_harvest * self.productivity(data.list_of_workplaces, data.citizens_in_city)
            self.accumulate_harvest_costs += float(self.calculate_price_of_good(data.list_of_workplaces[self].workers_costs, harvest_size))
            self.accumulate_harvest += harvest_size
        elif turn >= self.time_to_grow_to and self.accumulate_harvest > 0:
            veg_type, veg_name = self._get_veg_info()
            data.market.add_new_resource(resource_type=veg_type,
                                         size=int(self.accumulate_harvest),
                                         quality=self._get_quality(data.list_of_workplaces, data.citizens_in_city),
                                         price=round(self.accumulate_harvest_costs, 2),
                                         market=data.market.mi)
            self.accumulate_harvest = 0
            self.accumulate_harvest_costs = 0

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False

    def __str__(self):
        return self.name


class AnimalFarm(BuldingsWithWorkes):
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
    energy_required = models.PositiveIntegerField(default=10)
    water_required = models.PositiveIntegerField(default=20)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False

    class Meta:
        abstract = True


class School(BuldingsWithWorkes):
    name = models.CharField(default="Szkoła", max_length=6)
    max_students = models.PositiveIntegerField(default=0)
    age_of_start = models.PositiveIntegerField(default=0)
    years_of_education = models.PositiveIntegerField(default=0)
    entry_education = models.CharField(default="", max_length=1)
    education_type_provided = models.CharField(default="", max_length=1)
    student = GenericRelation(to='citizen_engine.Citizen',
                              object_id_field='school_object_id',
                              content_type_field='school_content_type')

    def monthly_run(self, citizen_in_city, player):
        teachers_with_data = {t: citizen_in_city[t] for t in citizen_in_city
                              if t.workplace_object == self
                              and citizen_in_city[t].current_profession
                              and len(citizen_in_city[t].educations) >= 2}
        for p in (c for c in citizen_in_city if c.school_object == self and citizen_in_city[c].current_education):
            citizen_education = citizen_in_city[p].current_education
            try:
                total_effectiveness = (sum([teachers_with_data[e].current_profession.proficiency for e in teachers_with_data])
                                       / len(teachers_with_data)) * player.primary_school_education_ratio
                citizen_education.effectiveness += total_effectiveness
            except ZeroDivisionError:
                pass

    def yearly_run(self, citizens_in_city):
        for p in (c for c in citizens_in_city if c.age >= self.age_of_start and c.edu_title == self.entry_education):
            if p.school_object is None:
                self.check_for_student_in_city(p, citizens_in_city[p])
            elif p.school_object == self:
                self.update_year_of_school_for_student(p, citizens_in_city[p].current_education)

    def check_for_student_in_city(self, p, p_data):
        education = apps.get_model('citizen_engine', 'Education')
        citizen_educations = [e for e in p_data.educations if e.name == self.education_type_provided]
        if citizen_educations:
            c = citizen_educations.pop()
            c.if_current = True
        else:
            education.objects.create(citizen=p, name=self.education_type_provided, max_year_of_learning=self.years_of_education)
        p.school_object = self

    def update_year_of_school_for_student(self, p, e):
        e.cur_year_of_learning += 1
        if e.cur_year_of_learning == e.max_year_of_learning:
            p.edu_title = self.education_type_provided
            p.school_object = None
            e.if_current = False

    class Meta:
        abstract = True


class PrimarySchool(School):
    name = models.CharField(default="Szkoła Podstawowa", max_length=17)
    max_students = models.PositiveIntegerField(default=10)
    energy_required = models.PositiveIntegerField(default=5)
    water_required = models.PositiveIntegerField(default=10)
    build_time = models.PositiveIntegerField(default=2)
    college_employee_needed = models.PositiveIntegerField(default=5)

    age_of_start = models.PositiveIntegerField(default=8)
    years_of_education = models.PositiveIntegerField(default=8)
    entry_education = models.CharField(default='None', max_length=4)
    education_type_provided = models.CharField(default=ELEMENTARY, max_length=8)
    profession_type_provided = models.CharField(default="Nauczyciel", max_length=10)
    qualification_needed = models.CharField(default=COLLEGE, max_length=10)


class DumpingGround(BuldingsWithWorkes):
    name = models.CharField(default='Wysypisko śmieci', max_length=20)
    profession_type_provided = models.CharField(default="Pracownik wysypiska śmieci", max_length=30)
    build_time = models.PositiveIntegerField(default=2)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    energy_required = models.PositiveIntegerField(default=1)
    limit_of_dust_cars = models.PositiveIntegerField(default=6)
    current_space_for_trash = models.PositiveIntegerField(default=0)
    max_space_for_trash = models.PositiveIntegerField(default=10000)
    pollution_rate = models.FloatField(default=3.0)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.water_required += 10
            DustCart.objects.create(dumping_ground=self, city=self.city)


class Vehicle(models.Model):
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=20)
    cost = models.PositiveIntegerField(default=0)
    maintenance_cost = models.PositiveIntegerField(default=0)
    profession_type_provided = models.CharField(default="", max_length=1)
    elementary_employee_needed = models.PositiveIntegerField(default=0)
    college_employee_needed = models.PositiveIntegerField(default=0)
    phd_employee_needed = models.PositiveIntegerField(default=0)
    employee = GenericRelation(to='citizen_engine.Citizen',
                               object_id_field='workplace_object_id',
                               content_type_field='workplace_content_type'
                               )

    def update_proficiency_of_profession_for_employees(self, employees):
        for employee in employees:
            employee.current_profession.update_proficiency(employee)

    def wage_payment(self, city, data):
        import decimal
        total_payment = []
        for e in data.list_of_workplaces[self].all_employees:
            se = decimal.Decimal(data.citizens_in_city[e].salary_expectation)
            e.cash += se
            city.cash -= se
            total_payment.append(se)
        data.list_of_workplaces[self].workers_costs = sum(total_payment)

    def calculate_wage_for_employees(self, wage_of_employees, total_wages, total_level, employees, employee_needed):
        if employee_needed:
            total_wages.append(wage_of_employees)
            total_level.append(
                (sum([e.current_profession.proficiency
                     if e.current_profession else 0 for e in employees])/float(employee_needed))*wage_of_employees)

    def employee_productivity(self, workplaces, citizens):
        wages = []
        total = []
        self.calculate_wage_for_employees(
            wage_of_employees=1,
            total_wages=wages,
            total_level=total,
            employees=[citizens[e] for e in workplaces[self].elementary_employees],
            employee_needed=self.elementary_employee_needed
        )
        self.calculate_wage_for_employees(
            wage_of_employees=2,
            total_wages=wages,
            total_level=total,
            employees=[citizens[e] for e in workplaces[self].college_employees],
            employee_needed=self.college_employee_needed
        )
        self.calculate_wage_for_employees(
            wage_of_employees=3,
            total_wages=wages,
            total_level=total,
            employees=[citizens[e] for e in workplaces[self].phd_employees],
            employee_needed=self.phd_employee_needed
        )
        return float(sum(total))/float(sum(wages))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class DustCart(Vehicle):
    dumping_ground = models.ForeignKey(DumpingGround, on_delete=models.SET_NULL, null=True)
    profession_type_provided = models.CharField(default="Śmieciarz", max_length=30)
    name = models.CharField(default="Śmieciarka", max_length=20)
    cost = models.PositiveIntegerField(default=10)
    elementary_employee_needed = models.PositiveIntegerField(default=3)
    curr_capacity = models.PositiveIntegerField(default=0)
    max_capacity = models.PositiveIntegerField(default=60)

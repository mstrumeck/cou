# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
from cou.global_var import ELEMENTARY, COLLEGE, PHD, EDUCATION
from django.apps import apps


class Trash(models.Model):
    size = models.PositiveIntegerField(default=0)
    time = models.PositiveIntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()


class City(models.Model):
    user = models.ForeignKey(User)
    name = models.TextField(max_length=15, unique=True)
    cash = models.DecimalField(default=10000, decimal_places=2, max_digits=20)
    mass = models.PositiveIntegerField(default=0)
    mass_price = models.DecimalField(default=2, decimal_places=2, max_digits=20)
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

    def elementary_vacancies(self):
        return self.elementary_employee_needed - self.employee.filter(edu_title=ELEMENTARY).count()

    def college_vacancies(self):
        return self.college_employee_needed - self.employee.filter(edu_title=COLLEGE).count()

    def phd_vacancies(self):
        return self.phd_employee_needed - self.employee.filter(edu_title=PHD).count()

    def trash_calculation(self, employee):
        return float(self.pollution_calculation(employee)) * float(self.pollution_rate)

    def pollution_calculation(self, employee):
        return self.pollution_rate * float(employee)

    def employee_productivity(self, workplaces, citizens):
        wages = []
        total = []
        if self.elementary_employee_needed:
            wages.append(1)
            elementary_employees = sum([citizens[e]['current_profession'].cur_level
                                        if citizens[e]['current_profession'] else 0
                                        for e in workplaces[self]['elementary_employees']])
            total.append(elementary_employees/float(self.elementary_employee_needed))
        if self.college_employee_needed:
            wages.append(2)
            college_employees = sum([citizens[e]['current_profession'].cur_level
                                     if citizens[e]['current_profession'] else 0
                                     for e in workplaces[self]['college_employees']])
            total.append((college_employees/float(self.college_employee_needed))*2)
        if self.phd_employee_needed:
            wages.append(3)
            phd_employees = sum([citizens[e]['current_profession'].cur_level
                                 if citizens[e]['current_profession'] else 0
                                 for e in workplaces[self]['phd_employees']])
            total.append((phd_employees/float(self.phd_employee_needed))*3)
        return float(sum(total))/float(sum(wages))

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
    max_population = models.PositiveIntegerField(default=30)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    water_required = models.PositiveIntegerField(default=5)
    energy_required = models.PositiveIntegerField(default=5)
    resident = GenericRelation(to='citizen_engine.Citizen',
                               object_id_field='resident_object_id',
                               content_type_field='resident_content_type'
                               )

    def pollution_calculation(self, employee):
        return float(employee) * self.pollution_rate

    def trash_calculation(self, employee):
        return self.pollution_calculation(employee) * self.population


class TradeDistrict(BuldingsWithWorkes):
    name = models.CharField(default='Strefa handlowa', max_length=20)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    elementary_employee_needed = models.PositiveIntegerField(default=20)
    resource_cost_per_good = models.PositiveIntegerField(default=1)
    max_goods_stored = models.PositiveIntegerField(default=100)
    goods_stored = models.PositiveIntegerField(default=0)
    cash = models.PositiveIntegerField(default=100)
    resources_stored = models.PositiveIntegerField(default=0)
    max_resources_stored = models.PositiveIntegerField(default=100)
    water_required = models.PositiveIntegerField(default=20)
    energy_required = models.PositiveIntegerField(default=30)

    def creating_goods(self, city, employee_list, workplaces_list):
        self.buy_resources(city, employee_list, workplaces_list)
        self.product_goods(employee_list, workplaces_list)

    def buy_resources(self, city, employee_list, workplaces_list):
        if self.resources_stored / self.max_resources_stored < 0.8:
            resources_diff = (self.max_resources_stored - self.resources_stored) * self.productivity(employee_list, workplaces_list)
            while self.cash > city.mass_price and city.mass > 0 and resources_diff > 0:
                resources_diff -= 1
                self.cash -= city.mass_price
                city.cash += city.mass_price
                city.mass -= 1
                self.resources_stored += 1

    def product_goods(self, employee_list, workplaces_list):
        if self.goods_stored / self.max_goods_stored < 0.5:
            goods_diff = (self.max_goods_stored - self.goods_stored) * self.productivity(employee_list, workplaces_list)
            while self.resources_stored > self.resource_cost_per_good and goods_diff > 0:
                self.resources_stored -= self.resource_cost_per_good
                self.goods_stored += 1
                goods_diff -= 1


class ProductionBuilding(BuldingsWithWorkes):
    name = models.CharField(max_length=20, default='Strefa przemysłowa')
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
    if_electricity = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def pollution_calculation(self, employee):
        return (self.power_nodes + employee) * self.pollution_rate

    def allocate_resource_in_target(self, target, tp):
        if hasattr(target, 'energy') and not isinstance(target, PowerPlant):
            while target.energy_required >= target.energy \
                    and tp > 0 \
                    and self.energy_allocated <= tp:
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
            self.power_nodes += 1
            self.max_power_nodes += 10
            self.energy_production += 15
            self.water_required += 10


class RopePlant(PowerPlant):
    name = models.CharField(default='Elektrownia na ropę', max_length=20)
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
            self.power_nodes += 1
            self.max_power_nodes += 4
            self.energy_production += 50
            self.water_required += 15


class CoalPlant(PowerPlant):
    name = models.CharField(default='Elektrownia węglowa', max_length=20)
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
            self.power_nodes += 1
            self.max_power_nodes += 4
            self.energy_production += 40
            self.water_required += 20


class Waterworks(BuldingsWithWorkes):
    name = models.CharField(max_length=20)
    raw_water_allocated = models.PositiveIntegerField(default=0)
    raw_water_production = models.PositiveIntegerField(default=0)
    if_waterworks = models.BooleanField(default=True)
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
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=50)
    maintenance_cost = models.PositiveIntegerField(default=5)
    energy_required = models.PositiveIntegerField(default=3)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def allocate_resource_in_target(self, target, tp):
        if hasattr(target, 'raw_water'):
            while target.raw_water_required >= target.raw_water \
                    and tp > 0 \
                    and self.raw_water_allocated <= tp:
                self.raw_water_allocated += 1
                target.raw_water += 1
                tp -= 1

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.raw_water_production += 20


class SewageWorks(BuldingsWithWorkes):
    name = models.CharField(default='Oczyszczalnia ścieków', max_length=30)
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
            self.raw_water_required += 1000

    def allocate_resource_in_target(self, target, tp):
        if hasattr(target, 'water') \
                and not isinstance(target, SewageWorks) \
                and not isinstance(target, Waterworks):
            while target.water_required >= target.water \
                    and tp > 0 \
                    and self.clean_water_allocated <= tp:
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
                    return int(self.raw_water * (float(sum(t))/float(len(t))))
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
    accumulate_harvest = models.PositiveIntegerField(default=0)
    max_harvest = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def update_harvest(self, turn, owner, workplaces, citizens):
        if turn >= self.time_to_grow_from and turn < self.time_to_grow_to:
            self.accumulate_harvest += int(self.max_harvest * self.productivity(workplaces, citizens))
        elif turn >= self.time_to_grow_to and self.accumulate_harvest > 0:
            self.veg.create(size=self.accumulate_harvest, owner=owner)
            self.accumulate_harvest = 0

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


class CattleFarm(AnimalFarm):
    name = models.CharField(default='Farma byłda', max_length=15)
    animal = GenericRelation('resources.Cattle')
    pastures = models.PositiveIntegerField(default=1)
    cattle_breeding_rate = models.FloatField(default=0.014)
    accumulate_breding = models.FloatField(default=0)

    def cattle_farm_productivity(self, cat):
        return ((cat.size / self.pastures) ** -0.3) * 2

    def farm_operation(self, turn, owner, workplaces, citizens):
        if self.animal.count() != 0:
            cat = self.animal.last()
            if turn != 8:
                self.accumulate_breding += (self.cattle_breeding_rate * self.productivity(workplaces, citizens))
                cat.resource_production(owner, self.pastures)
            else:
                cat.size += (cat.size * self.accumulate_breding * self.cattle_farm_productivity(cat))
                self.accumulate_breding = 0
                cat.resource_production(owner, self.pastures)
        else:
            self.animal.create(owner=owner, size=10)


class PotatoFarm(Farm):
    name = models.CharField(default='Farma ziemniaków', max_length=20)
    veg = GenericRelation('resources.Potato')
    time_to_grow_from = models.PositiveIntegerField(default=2)
    time_to_grow_to = models.PositiveIntegerField(default=6)
    max_harvest = models.PositiveIntegerField(default=10)


class BeanFarm(Farm):
    name = models.CharField(default='Farma fasoli', max_length=15)
    veg = GenericRelation('resources.Bean')
    time_to_grow_from = models.PositiveIntegerField(default=4)
    time_to_grow_to = models.PositiveIntegerField(default=8)
    max_harvest = models.PositiveIntegerField(default=8)


class LettuceFarm(Farm):
    name = models.CharField(default='Farma sałaty', max_length=15)
    veg = GenericRelation('resources.Lettuce')
    time_to_grow_from = models.PositiveIntegerField(default=3)
    time_to_grow_to = models.PositiveIntegerField(default=5)
    max_harvest = models.PositiveIntegerField(default=12)


class MassConventer(BuldingsWithWorkes):
    name = models.CharField(default="Konwenter Masy", max_length=16)
    energy_required = models.PositiveIntegerField(default=5)
    water_required = models.PositiveIntegerField(default=10)
    mass_production_rate = models.PositiveIntegerField(default=20)
    build_time = models.PositiveIntegerField(default=1)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def product_mass(self, city, workplaces, citizens):
        city.mass += int(self.mass_production_rate * self.productivity(workplaces, citizens))


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
        teachers_with_profession = {t: citizen_in_city[t]['current_profession'] for t in citizen_in_city
                                    if t.workplace_object == self
                                    and citizen_in_city[t]['current_profession']
                                    and citizen_in_city[t][
                                        'current_profession'].name == self.profession_type_provided
                                    and len(citizen_in_city[t]['educations']) >= 2}
        for p in (c for c in citizen_in_city if c.school_object == self and citizen_in_city[c]['current_education']):
            citizen_education = citizen_in_city[p]['current_education']
            try:
                total_effectiveness = (sum([teachers_with_profession[e].cur_level for e in teachers_with_profession])
                                       / len(teachers_with_profession)) * player.primary_school_education_ratio
                citizen_education.effectiveness += total_effectiveness
                citizen_education.save()
            except ZeroDivisionError:
                pass
        for teacher in teachers_with_profession:
            teachers_with_profession[teacher].update_level(citizen_in_city)
            teachers_with_profession[teacher].save()

    def yearly_run(self, citizens_in_city):
        for p in (c for c in citizens_in_city if c.age >= self.age_of_start and c.edu_title == self.entry_education):
            if p.school_object is None:
                self.check_for_student_in_city(p)
            elif p.school_object == self:
                self.update_year_of_school_for_student(p, citizens_in_city[p]['current_education'])

    def check_for_student_in_city(self, p):
        education = apps.get_model('citizen_engine', 'Education')
        education.objects.create(citizen=p, name=self.education_type_provided, max_year_of_learning=self.years_of_education)
        p.school_object = self

    def update_year_of_school_for_student(self, p, e):
        e.cur_year_of_learning += 1
        if e.cur_year_of_learning == e.max_year_of_learning:
            p.edu_title = self.education_type_provided
            p.school_object = None
            e.if_current = False
        e.save()

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
    if_dumping_ground = models.BooleanField(default=True)
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

    def elementary_vacancies(self):
        return self.elementary_employee_needed - self.employee.filter(edu_title=ELEMENTARY).count()

    def college_vacancies(self):
        return self.college_employee_needed - self.employee.filter(edu_title=COLLEGE).count()

    def phd_vacancies(self):
        return self.phd_employee_needed - self.employee.filter(edu_title=PHD).count()

    def employee_productivity(self, workplaces, citizens):
        wages = []
        total = []
        if self.elementary_employee_needed:
            wages.append(1)
            elementary_employees = sum([citizens[e]['current_profession'].cur_level
                                        if citizens[e]['current_profession'] else 0
                                        for e in workplaces[self]['elementary_employees']])
            total.append(elementary_employees/float(self.elementary_employee_needed))
        if self.college_employee_needed:
            wages.append(2)
            college_employees = sum([citizens[e]['current_profession'].cur_level
                                     if citizens[e]['current_profession'] else 0
                                     for e in workplaces[self]['college_employees']])
            total.append((college_employees/float(self.college_employee_needed))*2)
        if self.phd_employee_needed:
            wages.append(3)
            phd_employees = sum([citizens[e]['current_profession'].cur_level
                                 if citizens[e]['current_profession'] else 0
                                 for e in workplaces[self]['phd_employees']])
            total.append((phd_employees/float(self.phd_employee_needed))*3)
        return float(sum(total))/float(sum(wages))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class DustCart(Vehicle):
    dumping_ground = models.ForeignKey(DumpingGround, on_delete=models.SET_NULL, null=True)
    name = models.CharField(default="Śmieciarka", max_length=20)
    cost = models.PositiveIntegerField(default=10)
    elementary_employee_needed = models.PositiveIntegerField(default=3)
    curr_capacity = models.PositiveIntegerField(default=0)
    max_capacity = models.PositiveIntegerField(default=60)

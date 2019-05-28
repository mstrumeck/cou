import decimal

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from city_engine.temp_models import (
    TempResidential,
    TempTradeDistrict,
    DataContainersWithEmployees,
    TempRopePlant,
    TempCoalPlant,
    TempAnimalFarm,
    TempPowerPlant,
    TempSewageWorks,
    TempWaterTower,
    TempFarm,
    TempBuild,
    TempWindPlant,
    TempDumpingGround,
    TempClinic,
    TempFireStation
)
from cou.global_var import (
    ELEMENTARY,
    COLLEGE,
    STANDARD_RESIDENTIAL_ZONE_COST_PER_RESIDENT,
)
from map_engine.models import Field
from map_engine.models import Map
from player.models import Profile


class Trash(models.Model):
    size = models.PositiveIntegerField(default=0)
    time = models.PositiveIntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()


class City(models.Model):
    player = models.ForeignKey(Profile, on_delete=True)
    map = models.ForeignKey(Map, on_delete=True)
    name = models.TextField(max_length=15, unique=True)
    cash = models.DecimalField(default=1000000, decimal_places=2, max_digits=20)
    trade_zones_taxation = models.FloatField(default=0.05)
    publish = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    temp_model = TempBuild
    city = models.ForeignKey(City, on_delete=True)
    city_field = models.ForeignKey(Field, on_delete=True)
    cash = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    if_under_construction = models.BooleanField(default=True)
    build_cost = models.PositiveIntegerField(default=0)
    maintenance_cost = models.PositiveIntegerField(default=0)
    build_time = models.PositiveIntegerField()
    current_build_time = models.PositiveIntegerField(default=1)
    trash = GenericRelation(Trash)
    # Pollution
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
    temp_model = DataContainersWithEmployees
    profession_type_provided = models.CharField(default="", max_length=1)
    elementary_employee_needed = models.PositiveIntegerField(default=0)
    college_employee_needed = models.PositiveIntegerField(default=0)
    phd_employee_needed = models.PositiveIntegerField(default=0)
    employee = GenericRelation(
        to="citizen_engine.Citizen",
        object_id_field="workplace_object_id",
        content_type_field="workplace_content_type",
    )

    def calculate_price_of_good(self, workers_costs, size_of_production):
        if workers_costs and size_of_production:
            return workers_costs / decimal.Decimal(size_of_production)
        return 0

    def trash_calculation(self, employee):
        return float(self.pollution_calculation(employee)) * float(self.pollution_rate)

    def pollution_calculation(self, employee):
        return self.pollution_rate * float(employee)

    class Meta:
        abstract = True


class Residential(Building):
    temp_model = TempResidential
    name = models.CharField(max_length=20, default="Budynek Mieszkalny")
    population = models.PositiveIntegerField(default=0)
    max_population = models.PositiveIntegerField(default=0)
    build_time = models.PositiveIntegerField(default=0)
    build_cost = models.PositiveIntegerField(default=0)
    resident = GenericRelation(
        to="citizen_engine.Citizen",
        object_id_field="resident_object_id",
        content_type_field="resident_content_type",
    )

    class Meta:
        abstract = True

    def pollution_calculation(self, employee):
        return float(employee) * self.pollution_rate

    def trash_calculation(self, employee):
        return self.pollution_calculation(employee) * self.population


class StandardLevelResidentialZone(Residential):
    temp_model = TempResidential
    name = models.CharField(max_length=30, default="Normalna dzielnica mieszkalna")

    def self__init(self, max_population):
        self.max_population = 1 if max_population <= 0 else max_population
        self.build_time = 1 if max_population <= 4 else int(max_population / 4)
        self.build_cost = STANDARD_RESIDENTIAL_ZONE_COST_PER_RESIDENT * max_population


class TradeDistrict(Building):
    temp_model = TempTradeDistrict
    name = models.CharField(default="Dzielnica handlowa", max_length=20)
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
    name = models.CharField(max_length=20, default="Strefa przemysłowa")
    profession_type_provided = models.CharField(
        default="Pracownik strefy przemysłowej", max_length=30
    )

    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    elementary_employee_needed = models.PositiveIntegerField(default=20)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False


class PowerPlant(BuldingsWithWorkes):
    temp_model = TempPowerPlant
    name = models.CharField(max_length=20)
    power_nodes = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def pollution_calculation(self, employee):
        return (self.power_nodes + employee) * self.pollution_rate

    def __str__(self):
        return self.name


class WindPlant(PowerPlant):
    temp_model = TempWindPlant
    name = models.CharField(default="Elektrownia wiatrowa", max_length=20)
    profession_type_provided = models.CharField(
        default="Pracownik elektrowni wiatrowej", max_length=30
    )
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


class RopePlant(PowerPlant):
    temp_model = TempRopePlant
    name = models.CharField(default="Elektrownia na ropę", max_length=20)
    profession_type_provided = models.CharField(
        default="Pracownik elektrowni na ropę", max_length=30
    )
    build_time = models.PositiveIntegerField(default=5)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
    pollution_rate = models.FloatField(default=1.3)
    elementary_employee_needed = models.PositiveIntegerField(default=10)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.power_nodes = 1


class CoalPlant(PowerPlant):
    temp_model = TempCoalPlant
    name = models.CharField(default="Elektrownia węglowa", max_length=20)
    profession_type_provided = models.CharField(
        default="Pracownik elektrowni węglowej", max_length=30
    )
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


class Waterworks(BuldingsWithWorkes):
    temp_model = TempWaterTower
    name = models.CharField(max_length=20)
    pollution_rate = models.FloatField(default=0.5)

    class Meta:
        abstract = True

    def pollution_calculation(self, employee):
        return employee * self.pollution_rate


class WaterTower(Waterworks):
    temp_model = TempWaterTower
    name = models.CharField(default="Wieża ciśnień", max_length=20)
    profession_type_provided = models.CharField(
        default="Pracownik wieży ciśnień", max_length=30
    )
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=50)
    maintenance_cost = models.PositiveIntegerField(default=5)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False


class SewageWorks(BuldingsWithWorkes):
    temp_model = TempSewageWorks
    name = models.CharField(default="Oczyszczalnia ścieków", max_length=30)
    profession_type_provided = models.CharField(
        default="Pracownik oczyszczalni", max_length=30
    )
    build_time = models.PositiveIntegerField(default=2)
    build_cost = models.PositiveIntegerField(default=75)
    maintenance_cost = models.PositiveIntegerField(default=10)
    pollution_rate = models.FloatField(default=2.0)
    elementary_employee_needed = models.PositiveIntegerField(default=3)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False


class Farm(BuldingsWithWorkes):
    temp_model = TempFarm
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
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
        container = data.list_of_buildings[self]
        if turn >= self.time_to_grow_from and turn < self.time_to_grow_to:
            harvest_size = self.max_harvest * container._get_productivity()
            self.accumulate_harvest_costs += float(
                self.calculate_price_of_good(
                    data.list_of_workplaces[self].workers_costs, harvest_size
                )
            )
            self.accumulate_harvest += harvest_size
        elif turn >= self.time_to_grow_to and self.accumulate_harvest > 0:
            veg_type, veg_name = self._get_veg_info()
            data.market.add_new_resource(
                resource_type=veg_type,
                size=int(self.accumulate_harvest),
                quality=container._get_quality(),
                price=round(self.accumulate_harvest_costs, 2),
                market=data.market.mi,
            )
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
    temp_model = TempAnimalFarm
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False

    class Meta:
        abstract = True


class School(BuldingsWithWorkes):
    temp_model = DataContainersWithEmployees
    name = models.CharField(default="Szkoła", max_length=6)
    max_students = models.PositiveIntegerField(default=0)
    age_of_start = models.PositiveIntegerField(default=0)
    years_of_education = models.PositiveIntegerField(default=0)
    entry_education = models.CharField(default="", max_length=1)
    education_type_provided = models.CharField(default="", max_length=1)
    student = GenericRelation(
        to="citizen_engine.Citizen",
        object_id_field="school_object_id",
        content_type_field="school_content_type",
    )

    def monthly_run(self, citizen_in_city, player):
        teachers_with_data = {
            t: citizen_in_city[t]
            for t in citizen_in_city
            if t.workplace_object == self
            and citizen_in_city[t].current_profession
            and len(citizen_in_city[t].educations) >= 2
        }
        for p in (
            c
            for c in citizen_in_city
            if c.school_object == self and citizen_in_city[c].current_education
        ):
            citizen_education = citizen_in_city[p].current_education
            try:
                total_effectiveness = (
                    sum(
                        [
                            teachers_with_data[e].current_profession.proficiency
                            for e in teachers_with_data
                        ]
                    )
                    / len(teachers_with_data)
                ) * player.primary_school_education_ratio
                citizen_education.effectiveness += total_effectiveness
            except ZeroDivisionError:
                pass

    def yearly_run(self, citizens_in_city):
        for p in (
            c
            for c in citizens_in_city
            if c.age >= self.age_of_start and c.edu_title == self.entry_education
        ):
            if p.school_object is None:
                self.check_for_student_in_city(p, citizens_in_city[p])
            elif p.school_object == self:
                self.update_year_of_school_for_student(
                    p, citizens_in_city[p].current_education
                )

    def check_for_student_in_city(self, p, p_data):
        education = apps.get_model("citizen_engine", "Education")
        citizen_educations = [
            e for e in p_data.educations if e.name == self.education_type_provided
        ]
        if citizen_educations:
            c = citizen_educations.pop()
            c.if_current = True
        else:
            education.objects.create(
                citizen=p,
                name=self.education_type_provided,
                max_year_of_learning=self.years_of_education,
            )
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
    temp_model = DataContainersWithEmployees
    name = models.CharField(default="Szkoła Podstawowa", max_length=17)
    max_students = models.PositiveIntegerField(default=10)
    build_time = models.PositiveIntegerField(default=2)
    college_employee_needed = models.PositiveIntegerField(default=5)

    age_of_start = models.PositiveIntegerField(default=8)
    years_of_education = models.PositiveIntegerField(default=8)
    entry_education = models.CharField(default="None", max_length=4)
    education_type_provided = models.CharField(default=ELEMENTARY, max_length=8)
    profession_type_provided = models.CharField(default="Nauczyciel", max_length=10)
    qualification_needed = models.CharField(default=COLLEGE, max_length=10)


class DumpingGround(BuldingsWithWorkes):
    temp_model = TempDumpingGround
    name = models.CharField(default="Wysypisko śmieci", max_length=20)
    profession_type_provided = models.CharField(
        default="Pracownik wysypiska śmieci", max_length=30
    )
    build_time = models.PositiveIntegerField(default=2)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    current_space_for_trash = models.PositiveIntegerField(default=0)
    max_space_for_trash = models.PositiveIntegerField(default=10000)
    pollution_rate = models.FloatField(default=3.0)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time += 1
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False


class MedicalEstablishment(BuldingsWithWorkes):

    class Meta:
        abstract = True


class Clinic(MedicalEstablishment):
    temp_model = TempClinic
    name = models.CharField(default="Klinika", max_length=20)
    build_time = models.PositiveIntegerField(default=2)
    build_cost = models.PositiveIntegerField(default=1000)
    college_employee_needed = models.PositiveIntegerField(default=10)
    phd_employee_needed = models.PositiveIntegerField(default=5)


class FireStation(BuldingsWithWorkes):
    temp_model = TempFireStation
    name = models.CharField(default="Straż Pożarna", max_length=20)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=1500)
    elementary_employee_needed = models.PositiveIntegerField(default=10)
    college_employee_needed = models.PositiveIntegerField(default=5)

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.apps import apps


class CityFilter(models.Manager):

    def exists_in_city(self):
        if self.filter(city=self.city).exists():
            return True
        else:
            return False

    def filter_by_city(self):
            return self.filter(city=self.city)


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
    publish = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class CityField(models.Model):
    city = models.ForeignKey(City)
    col = models.PositiveIntegerField()
    row = models.PositiveIntegerField()
    pollution = models.PositiveIntegerField(default=0)

    # def return_list_of_possible_buildings_related_with_type_of_field(self):
    #     if self.if_electricity is True:
    #         return electricity_buildings
    #     elif self.if_waterworks is True:
    #         return waterworks_buildings
    #     else:
    #         return None


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
    #Managers
    objects = CityFilter()

    class Meta:
        abstract = True
    #
    # def spend_resources(self):
    #     self.spend_energy()
    #     self.spend_water()
    #     self.save()
    #
    # def spend_water(self):
    #     if self.water > 0:
    #         self.water -= 1
    #
    # def spend_energy(self):
    #     if self.energy > 0:
    #         self.energy -= 1


    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.save()
                return True
        else:
            return False


class BuldingsWithWorkes(Building):
    max_employees = models.PositiveIntegerField(default=0)
    employee = GenericRelation('citizen_engine.Citizen')

    def trash_calculation(self):
        return self.pollution_calculation() * self.pollution_rate

    def pollution_calculation(self):
        return self.pollution_rate * self.employee.count()

    class Meta:
        abstract = True


class Residential(Building):
    name = models.CharField(max_length=20, default='Budynek Mieszkalny')
    population = models.PositiveIntegerField(default=0)
    max_population = models.PositiveIntegerField(default=30)
    if_residential = models.BooleanField(default=True)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)

    # def build_status(self):
    #     if self.if_under_construction is True:
    #         if self.current_build_time < self.build_time:
    #             self.current_build_time += 1
    #             self.save()
    #             return False
    #         elif self.current_build_time == self.build_time:
    #             self.if_under_construction = False
    #             self.if_residential = True
    #             self.save()
    #             return True
    #     else:
    #         return False

    def pollution_calculation(self):
        return self.population * self.pollution_rate

    def trash_calculation(self):
        return self.pollution_calculation() * self.population


class ProductionBuilding(BuldingsWithWorkes):
    name = models.CharField(max_length=20, default='Budynek Przemysłowy')
    if_production = models.BooleanField(default=True)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    max_employees = models.PositiveIntegerField(default=20)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.save()
                return True
        else:
            return False


class PowerPlant(BuldingsWithWorkes):
    name = models.CharField(max_length=20)
    power_nodes = models.PositiveIntegerField(default=0)
    max_power_nodes = models.PositiveIntegerField(default=1)
    energy_production = models.PositiveIntegerField(default=0)
    energy_allocated = models.PositiveIntegerField(default=0)
    if_electricity = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def pollution_calculation(self):
        return (self.power_nodes + self.employee.count()) * self.pollution_rate

    def resources_allocation_reset(self):
        self.energy_allocated = 0
        self.save()

    def producted_resources_allocation(self):
        return self.energy_allocated

    def total_production(self):
        if self.employee.count() is 0 or self.max_employees is 0:
            return 0
        else:
            if self.water is 0:
                water_productivity = 0.0
            else:
                water_productivity = float(self.water) / float(self.water_required)
        employees_productivity = float(self.employee.count()) / float(self.max_employees)
        productivity = (water_productivity + employees_productivity)/2
        total = (productivity * int(self.energy_production)) * int(self.power_nodes)
        return int(total)

    # def build_status(self):
    #     if self.if_under_construction is True:
    #         if self.current_build_time < self.build_time:
    #             self.current_build_time += 1
    #             self.save()
    #             return False
    #         elif self.current_build_time == self.build_time:
    #             self.if_under_construction = False
    #             self.max_employees = 1
    #             self.power_nodes = 1
    #             self.max_power_nodes = 2
    #             self.energy_production = 1
    #             self.save()
    #             return True
    #     else:
    #         return False

    def __str__(self):
        return self.name


class WindPlant(PowerPlant):
    name = models.CharField(default='Elektrownia wiatrowa', max_length=20)
    build_time = models.PositiveIntegerField(default=3)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    water_required = models.PositiveIntegerField(default=10)
    pollution_rate = models.FloatField(default=1.8)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 5
                self.power_nodes = 1
                self.max_power_nodes = 10
                self.energy_production = 15
                self.save()
                return True
        else:
            return False


class RopePlant(PowerPlant):
    name = models.CharField(default='Elektrownia na ropę', max_length=20)
    build_time = models.PositiveIntegerField(default=5)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
    water_required = models.PositiveIntegerField(default=15)
    pollution_rate = models.FloatField(default=1.3)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 10
                self.power_nodes = 1
                self.max_power_nodes = 4
                self.energy_production = 50
                self.save()
                return True
        else:
            return False


class CoalPlant(PowerPlant):
    name = models.CharField(default='Elektrownia węglowa', max_length=20)
    build_time = models.PositiveIntegerField(default=4)
    build_cost = models.PositiveIntegerField(default=150)
    maintenance_cost = models.PositiveIntegerField(default=15)
    water_required = models.PositiveIntegerField(default=20)
    pollution_rate = models.FloatField(default=1.5)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 15
                self.power_nodes = 1
                self.max_power_nodes = 4
                self.energy_production = 40
                self.save()
                return True
        else:
            return False


class Waterworks(BuldingsWithWorkes):
    name = models.CharField(max_length=20)
    water_allocated = models.PositiveIntegerField(default=0)
    water_production = models.PositiveIntegerField(default=0)
    if_waterworks = models.BooleanField(default=True)
    pollution_rate = models.FloatField(default=0.5)

    class Meta:
        abstract = True

    def pollution_calculation(self):
        return self.employee.count() * self.pollution_rate

    def resources_allocation_reset(self):
        self.water_allocated = 0
        self.save()

    def producted_resources_allocation(self):
        return self.water_allocated

    def total_production(self):
        if self.employee.count() is 0 or self.max_employees is 0:
            return 0
        else:
            if self.energy is 0:
                energy_productivity = 0.0
            else:
                energy_productivity = float(self.energy)/float(self.energy_required)
            employees_productivity = float(self.employee.count())/float(self.max_employees)
            productivity = float((energy_productivity+employees_productivity)/2)
            total = (productivity * int(self.water_production))
            return int(total)


class WaterTower(Waterworks):
    name = models.CharField(default='Wieża ciśnień', max_length=20)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=50)
    maintenance_cost = models.PositiveIntegerField(default=5)
    energy_required = models.PositiveIntegerField(default=3)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 5
                self.water_production = 20
                self.save()
                return True
        else:
            return False


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

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 5
                DustCart.objects.create(dumping_ground=self, city=self.city)
                self.save()
                return True
        else:
            return False


class Vehicle(models.Model):
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=20)
    cost = models.PositiveIntegerField(default=0)
    maintenance_cos = models.PositiveIntegerField(default=0)
    max_employees = models.PositiveIntegerField(default=0)
    employee = GenericRelation('citizen_engine.Citizen')

    class Meta:
        abstract = True


class DustCart(Vehicle):
    dumping_ground = models.ForeignKey(DumpingGround, on_delete=models.SET_NULL, null=True)
    name = models.CharField(default="Śmieciarka", max_length=20)
    cost = models.PositiveIntegerField(default=10)
    max_employees = models.PositiveIntegerField(default=3)
    curr_capacity = models.PositiveIntegerField(default=0)
    max_capacity = models.PositiveIntegerField(default=60)

    def effectiveness(self):
        return float(self.employee.count()) / float(self.max_employees)

    def __str__(self):
        return self.name


electricity_buildings = [WindPlant, RopePlant, CoalPlant]
waterworks_buildings = [WaterTower]
trash_collector = [DumpingGround]
vehicles = [DustCart]
list_of_buildings_categories = electricity_buildings + waterworks_buildings
list_of_buildings_with_employees = electricity_buildings + waterworks_buildings\
                                   + [ProductionBuilding] + [DumpingGround]
list_of_models = [ProductionBuilding, Residential]

for electricity in electricity_buildings:
    list_of_models.append(electricity)

for waterworks in waterworks_buildings:
    list_of_models.append(waterworks)

for trash_building in trash_collector:
    list_of_models.append(trash_building)


def get_subclasses(abstract_class=Building, app_label='city_engine'):
    result = []
    for model in apps.get_app_config(app_label).get_models():
        if issubclass(model, abstract_class) and model is not abstract_class:
            result.append(model)
    return result


def list_of_buildings_in_city(city, abstract_class=Building, app_label='city_engine'):
    result = []
    for item in get_subclasses(abstract_class, app_label):
        if item.objects.filter(city=city).exists():
            a = item.objects.filter(city=city)
            for data in a:
                result.append(data)
    return result


def list_of_workplaces(city):
    result = []
    for subclass in get_subclasses(BuldingsWithWorkes, 'city_engine'):
        if subclass.objects.filter(city=city).exists():
            a = subclass.objects.filter(city=city)
            for building in a:
                result.append(building)
    for subclass in get_subclasses(Vehicle, 'city_engine'):
        if subclass.objects.filter(city=city).exists():
            b = subclass.objects.filter(city=city)
            for vehicle in b:
                result.append(vehicle)
    return result

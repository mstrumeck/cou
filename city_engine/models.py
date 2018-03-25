from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.contrib.auth.models import User


class CityFilter(models.Manager):

    def exists_in_city(self, city):
        if self.filter(city=city).exists():
            return True
        else:
            return False

    def filter_by_city(self, city):
            return self.filter(city=city)


class Trash(models.Model):
    size = models.PositiveIntegerField(default=0)
    time = models.PositiveIntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
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
    if_residential = models.BooleanField(default=False)
    if_production = models.BooleanField(default=False)
    if_electricity = models.BooleanField(default=False)
    if_waterworks = models.BooleanField(default=False)

    def return_list_of_possible_buildings_related_with_type_of_field(self):
        if self.if_electricity is True:
            return electricity_buildings
        elif self.if_waterworks is True:
            return waterworks_buildings
        else:
            return None


class Building(models.Model):
    city = models.ForeignKey(City)
    city_field = models.ForeignKey(CityField)
    if_under_construction = models.BooleanField(default=True)
    if_residential = models.BooleanField(default=False)
    if_production = models.BooleanField(default=False)
    if_electricity = models.BooleanField(default=False)
    if_waterworks = models.BooleanField(default=False)
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
    current_employees = models.PositiveIntegerField(default=0)
    max_employees = models.PositiveIntegerField(default=0)

    def trash_calculation(self):
        return self.pollution_calculation() * self.pollution_rate

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
    type_of_working_building = models.CharField(default='PB', max_length=2)


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
        return (self.power_nodes + self.current_employees) * self.pollution_rate

    def resources_allocation_reset(self):
        self.energy_allocated = 0
        self.save()

    def producted_resources_allocation(self):
        return self.energy_allocated

    def total_production(self):
        if self.current_employees is 0 or self.max_employees is 0:
            return 0
        else:
            if self.water is 0:
                water_productivity = 0
            else:
                water_productivity = float(self.water) / float(self.water_required)
        employees_productivity = float(self.current_employees) / float(self.max_employees)
        productivity = int(water_productivity + employees_productivity)/2
        total = (productivity * int(self.energy_production)) * int(self.power_nodes)
        return int(total)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 1
                self.power_nodes = 1
                self.max_power_nodes = 2
                self.energy_production = 1
                self.save()
                return True
        else:
            return False

    def __str__(self):
        return self.name


class WindPlant(PowerPlant):
    name = models.CharField(default='Elektrownia wiatrowa', max_length=20)
    build_time = models.PositiveIntegerField(default=3)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    water_required = models.PositiveIntegerField(default=10)
    pollution_rate = models.FloatField(default=1.8)
    type_of_working_building = models.CharField(default='WP', max_length=2)

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
                self.energy_production = 5
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
    type_of_working_building = models.CharField(default='RP', max_length=2)

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
                self.energy_production = 30
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
    type_of_working_building = models.CharField(default='CP', max_length=2)

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
                self.energy_production = 20
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
        return self.current_employees * self.pollution_rate

    def resources_allocation_reset(self):
        self.water_allocated = 0
        self.save()

    def producted_resources_allocation(self):
        return self.water_allocated

    def total_production(self):
        if self.current_employees is 0 or self.max_employees is 0:
            return 0
        else:
            if self.energy is 0:
                energy_productivity = 0
            else:
                energy_productivity = float(self.energy)/float(self.energy_required)
            employees_productivity = float(self.current_employees)/float(self.max_employees)
            productivity = float((energy_productivity+employees_productivity)/2)
            total = (productivity * int(self.water_production))
            return int(total)


class WaterTower(Waterworks):
    name = models.CharField(default='Wieża ciśnień', max_length=20)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=50)
    maintenance_cost = models.PositiveIntegerField(default=5)
    energy_required = models.PositiveIntegerField(default=3)
    type_of_working_building = models.CharField(default='WT', max_length=2)

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


electricity_buildings = [WindPlant, RopePlant, CoalPlant]
waterworks_buildings = [WaterTower]
list_of_buildings_categories = electricity_buildings + waterworks_buildings
list_of_buildings_with_employees = electricity_buildings + waterworks_buildings + [ProductionBuilding]
list_of_models = [ProductionBuilding, Residential]

for electricity in electricity_buildings:
    list_of_models.append(electricity)

for waterworks in waterworks_buildings:
    list_of_models.append(waterworks)
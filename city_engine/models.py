from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.db.models import F


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
            self.current_build_time = F('current_build_time') + 1
            self.save()
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.save()


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
    water_required = models.PositiveIntegerField(default=5)
    energy_required = models.PositiveIntegerField(default=5)

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
        if self.current_build_time < self.build_time:
            self.current_build_time = F('current_build_time') + 1
            self.save()
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.water_required = F('water_required') + 5
            self.energy_required = F('energy_required') + 5
            self.save()


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

    def allocate_resource_in_target(self, target, tp):
        if hasattr(target, 'energy') and not isinstance(target, PowerPlant):
            rl = tp - self.energy_allocated
            rtf = target.energy_required - target.energy
            if rl >= rtf:
                self.energy_allocated = F('energy_allocated') + rtf
                target.energy = F('energy') + rtf
            elif rl < rtf:
                self.energy_allocated = F('energy_allocated') + rl
                target.energy = F('energy') + rl
        self.save()
        target.save()
        self.refresh_from_db()
        target.refresh_from_db()

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

    def __str__(self):
        return self.name


class WindPlant(PowerPlant):
    name = models.CharField(default='Elektrownia wiatrowa', max_length=20)
    build_time = models.PositiveIntegerField(default=3)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)
    pollution_rate = models.FloatField(default=1.8)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time = F('current_build_time') + 1
            self.save()
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.max_employees = F('max_employees') + 5
            self.power_nodes = F('power_nodes') + 1
            self.max_power_nodes = F('max_power_nodes') + 10
            self.energy_production = F('energy_production') + 15
            self.water_required = F('water_required') + 10
            self.save()


class RopePlant(PowerPlant):
    name = models.CharField(default='Elektrownia na ropę', max_length=20)
    build_time = models.PositiveIntegerField(default=5)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
    water_required = models.PositiveIntegerField(default=15)
    pollution_rate = models.FloatField(default=1.3)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time = F('current_build_time') + 1
            self.save()
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.max_employees = F('max_employees') + 10
            self.power_nodes = F('power_nodes') + 1
            self.max_power_nodes = F('max_power_nodes') + 4
            self.energy_production = F('energy_production') + 50
            self.water_required = F('water_required') + 15
            self.save()


class CoalPlant(PowerPlant):
    name = models.CharField(default='Elektrownia węglowa', max_length=20)
    build_time = models.PositiveIntegerField(default=4)
    build_cost = models.PositiveIntegerField(default=150)
    maintenance_cost = models.PositiveIntegerField(default=15)
    pollution_rate = models.FloatField(default=1.5)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time = F('current_build_time') + 1
            self.save()
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.max_employees = F('max_employees') + 15
            self.power_nodes = F('power_nodes') + 1
            self.max_power_nodes = F('max_power_nodes') + 4
            self.energy_production = F('energy_production') + 40
            self.water_required = F('water_required') + 20
            self.save()


class Waterworks(BuldingsWithWorkes):
    name = models.CharField(max_length=20)
    raw_water_allocated = models.PositiveIntegerField(default=0)
    raw_water_production = models.PositiveIntegerField(default=0)
    if_waterworks = models.BooleanField(default=True)
    pollution_rate = models.FloatField(default=0.5)

    class Meta:
        abstract = True

    def allocate_resource_in_target(self, target, tp):
        if hasattr(target, 'raw_water'):
            rl = tp - self.raw_water_allocated
            rtf = target.raw_water_required - target.raw_water
            if rl >= rtf:
                self.raw_water_allocated = F('raw_water_allocated') + rtf
                target.raw_water = F('raw_water') + rtf
            elif rl < rtf:
                self.raw_water_allocated = F('raw_water_allocated') + rl
                target.raw_water = F('raw_water') + rl
            self.save()
            target.save()
            self.refresh_from_db()
            target.refresh_from_db()

    def pollution_calculation(self):
        return self.employee.count() * self.pollution_rate

    def total_production(self):
        if self.employee.count() is 0:
            return 0
        else:
            if self.energy is 0:
                energy_productivity = 0.0
            else:
                energy_productivity = float(self.energy)/float(self.energy_required)
            employees_productivity = float(self.employee.count())/float(self.max_employees)
            productivity = float((energy_productivity+employees_productivity)/2)
            total = (productivity * int(self.raw_water_production))
            return int(total)


class WaterTower(Waterworks):
    name = models.CharField(default='Wieża ciśnień', max_length=20)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=50)
    maintenance_cost = models.PositiveIntegerField(default=5)
    energy_required = models.PositiveIntegerField(default=3)

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time = F('current_build_time') + 1
            self.save()
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.max_employees = F('max_employees') + 5
            self.raw_water_production = F('raw_water_production') + 20
            self.save()


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

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time = F('current_build_time') + 1
            self.save()
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.max_employees = F('max_employees') + 3
            self.raw_water_required = F('raw_water_required') + 1000
            self.save()

    def allocate_resource_in_target(self, target, tp):
        if hasattr(target, 'water'):
            rl = tp - self.clean_water_allocated
            rtf = target.water_required - target.water
            if rl >= rtf:
                self.clean_water_allocated = F('clean_water_allocated') + rtf
                target.water = F('water') + rtf
            elif rl < rtf:
                self.clean_water_allocated = F('clean_water_allocated') + rl
                target.water = F('water') + rl
        self.save()
        target.save()
        self.refresh_from_db()
        target.refresh_from_db()

    def total_production(self):
        if self.energy is 0:
            return 0
        else:
            energy_productivity = float(self.energy) / float(self.energy_required)
        try:
            employee_productivity = float(self.employee.count()) / float(self.max_employees)
            productivity = float((employee_productivity + energy_productivity)/2)
            if self.raw_water <= self.raw_water_required:
                return int(self.raw_water * productivity)
            return int(self.raw_water_required * productivity)
        except(ZeroDivisionError):
            return 0


class Farm(BuldingsWithWorkes):
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
    energy_required = models.PositiveIntegerField(default=20)
    water_required = models.PositiveIntegerField(default=40)
    crops = models.PositiveIntegerField(default=0)
    harvest = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def build_status(self):
        if self.current_build_time < self.build_time:
            self.current_build_time = F('current_build_time') + 1
            self.save()
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.max_employees = F('max_employees') + 5
            self.save()

    def update_harvest(self, owner):
        if self.harvest < self.crops:
            self.harvest = F('harvest') + 1
            self.save()
            self.refresh_from_db()
        elif self.harvest == self.crops:
            self.harvest = 0
            self.veg.create(size=60, owner=owner)
            self.save()
            self.refresh_from_db()

    def __str__(self):
        return self.name


class AnimalFarm(BuldingsWithWorkes):
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)
    energy_required = models.PositiveIntegerField(default=10)
    water_required = models.PositiveIntegerField(default=20)

    class Meta:
        abstract = True


class CattleFarm(AnimalFarm):
    name = models.CharField(default='Farma byłda', max_length=15)
    cattle = GenericRelation('city_engine.Cattle')
    cattle_herd_max_size = models.PositiveIntegerField(default=100)

    def farm_operation(self, owner):
        try:
            cat = self.cattle.last()
            if cat.size < self.cattle_herd_max_size:
                cat.size = F('size') + 4
                cat.save()
            cat.milk_production(owner=owner)
        except BaseException:
            self.cattle.create(owner=owner, size=0)


class PotatoFarm(Farm):
    name = models.CharField(default='Farma ziemniaków', max_length=20)
    veg = GenericRelation('city_engine.Potato')
    crops = models.PositiveIntegerField(default=6)


class BeanFarm(Farm):
    name = models.CharField(default='Farma fasoli', max_length=15)
    veg = GenericRelation('city_engine.Bean')
    crops = models.PositiveIntegerField(default=4)


class LettuceFarm(Farm):
    name = models.CharField(default='Farma sałaty', max_length=15)
    veg = GenericRelation('city_engine.Lettuce')
    crops = models.PositiveIntegerField(default=5)


class Resource(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(default='Surowiec', max_length=8)
    size = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class KindOfAnimal(Resource):
    size = models.PositiveIntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()

    class Meta:
        abstract = True


class Cattle(KindOfAnimal):
    name = models.CharField(default='Bydło', max_length=6)
    milk = GenericRelation('city_engine.Milk')
    beef = GenericRelation('city_engine.Beef')

    def milk_production(self, owner):
        try:
            milk = self.milk.last()
            milk.size = F('size') + 4
            milk.save()
        except BaseException:
            self.milk.create(size=0, owner=owner)


class AnimalResources(Resource):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()

    class Meta:
        abstract = True


class Milk(AnimalResources):
    name = models.CharField(default='Mleko', max_length=5)


class Beef(AnimalResources):
    name = models.CharField(default='Wołowina', max_length=8)


class KindOfCultivation(Resource):
    size = models.PositiveIntegerField(default=60)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()

    class Meta:
        abstract = True


class Bean(KindOfCultivation):
    name = models.CharField(default='Fasola', max_length=10)


class Potato(KindOfCultivation):
    name = models.CharField(default='Ziemniaki', max_length=10)


class Lettuce(KindOfCultivation):
    name = models.CharField(default='Sałata', max_length=10)


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
        if self.current_build_time < self.build_time:
            self.current_build_time = F('current_build_time') + 1
            self.save()
        elif self.current_build_time == self.build_time:
            self.if_under_construction = False
            self.max_employees = F('max_employees') + 5
            self.water_required = F('water_required') + 10
            DustCart.objects.create(dumping_ground=self, city=self.city)
            self.save()


class Vehicle(models.Model):
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=20)
    cost = models.PositiveIntegerField(default=0)
    maintenance_cos = models.PositiveIntegerField(default=0)
    max_employees = models.PositiveIntegerField(default=0)
    employee = GenericRelation('citizen_engine.Citizen')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class DustCart(Vehicle):
    dumping_ground = models.ForeignKey(DumpingGround, on_delete=models.SET_NULL, null=True)
    name = models.CharField(default="Śmieciarka", max_length=20)
    cost = models.PositiveIntegerField(default=10)
    max_employees = models.PositiveIntegerField(default=3)
    curr_capacity = models.PositiveIntegerField(default=0)
    max_capacity = models.PositiveIntegerField(default=60)

    def effectiveness(self):
        return float(self.employee.count()) / float(self.max_employees)


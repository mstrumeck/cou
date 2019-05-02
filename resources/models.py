from django.db import models

from city_engine import models as ce_models
from player.models import Profile
from company_engine.models import FoodCompany


class Market(models.Model):
    profile = models.OneToOneField(Profile, on_delete=True)


class Resource(models.Model):
    name = models.CharField(default="Surowiec", max_length=8)
    size = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=20)

    class Meta:
        abstract = True


class Food(Resource):
    company = models.ForeignKey(FoodCompany, on_delete=True)
    name = models.CharField(default="Jedzenie", max_length=9)
    quality = models.PositiveIntegerField(default=0)


class MarketResource(Resource):
    market = models.ForeignKey(Market, on_delete=True)
    quality = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class Mass(MarketResource):
    name = models.CharField(default="Masa", max_length=5)


class Milk(MarketResource):
    name = models.CharField(default="Mleko", max_length=5)


class Beef(MarketResource):
    name = models.CharField(default="Wołowina", max_length=8)


class Bean(MarketResource):
    name = models.CharField(default="Fasola", max_length=10)


class Potato(MarketResource):
    name = models.CharField(default="Ziemniaki", max_length=10)


class Lettuce(MarketResource):
    name = models.CharField(default="Sałata", max_length=10)


class Commodity(MarketResource):
    name = models.CharField(default="Towary", max_length=7)


class MassConventer(ce_models.BuldingsWithWorkes):
    name = models.CharField(default="Konwenter Masy", max_length=16)
    profession_type_provided = models.CharField(
        default="Pracownik konwentera masy", max_length=30
    )
    energy_required = models.PositiveIntegerField(default=5)
    water_required = models.PositiveIntegerField(default=10)
    mass_production_rate = models.PositiveIntegerField(default=100)
    build_time = models.PositiveIntegerField(default=1)
    elementary_employee_needed = models.PositiveIntegerField(default=5)

    def product_mass(self, data):
        container = data.list_of_workplaces[self]
        size_total = int(
            self.mass_production_rate * container.productivity)
        size = size_total if size_total > 1 else 1
        quality = container._get_quality()
        price = self.calculate_price_of_good(
            data.list_of_workplaces[self].workers_costs, size
        )

        if quality > 0 and len(data.list_of_workplaces[self].all_employees) >= 1:
            data.market.add_new_resource(Mass, size, quality, price, data.market.mi)


class CattleFarm(ce_models.AnimalFarm):
    name = models.CharField(default="Farma byłda", max_length=15)
    profession_type_provided = models.CharField(default="Farmer bydła.", max_length=30)
    pastures = models.PositiveIntegerField(default=1)
    cattle_breeding_rate = models.FloatField(default=0.014)
    accumulate_breding = models.FloatField(default=0)

    def buy_cattle(self, num, data):
        cattle_status = data.list_of_workplaces[self].cattle
        if cattle_status:
            cattle_status.size += num
        else:
            c = Cattle.objects.create(farm=self, size=num)
            data.list_of_workplaces[self].cattle = c

    def _cattle_farm_productivity(self, cat):
        return ((cat.size / self.pastures) ** -0.3) * 2

    def _accumulate_breeding(self, data, cattle):
        container = data.list_of_workplaces[self]
        self.accumulate_breding += self.cattle_breeding_rate * container.productivity
        if len(data.list_of_workplaces[self].all_employees) >= 1:
            cattle.resource_production(
                self.pastures,
                data,
                data.list_of_workplaces[self].workers_costs,
                container.productivity,
            )

    def _release_accumulate_breeding(self, cattle, release_breeding):
        diff = release_breeding - round(release_breeding)
        cattle.size += round(release_breeding)
        self.accumulate_breding = diff

    def _get_accumulate_breeding_rate_to_release(self, cattle):
        return (
            cattle.size
            * self.accumulate_breding
            * self._cattle_farm_productivity(cattle)
        )

    def farm_operation(self, data):
        container = data.list_of_workplaces[self]
        if container.cattle:
            self._accumulate_breeding(data, container.cattle)
            release_breeding = self._get_accumulate_breeding_rate_to_release(container.cattle)
            if release_breeding >= 1:
                self._release_accumulate_breeding(container.cattle, release_breeding)


class Cattle(Resource):
    name = models.CharField(default="Bydło", max_length=6)
    farm = models.OneToOneField(CattleFarm, on_delete=True)

    def resource_production(self, pastures, data, workers_costs, farm_productivity):
        quality = self._get_milk_quality(pastures)
        size_total = int(self._size_of_production(pastures, farm_productivity))
        size = size_total if size_total > 1 else 1
        if quality > 0:
            data.market.add_new_resource(
                resource_type=Milk,
                size=size,
                quality=quality,
                price=self._calculate_price_of_good(workers_costs, size),
                market=data.market.mi,
            )

    def _calculate_price_of_good(self, workers_costs, size_of_production):
        return round(workers_costs / size_of_production, 2)

    def _size_of_production(self, pastures, farm_productivity):
        return round(
            (self.size * (6 * self.pastures_productivity(pastures))) * farm_productivity
        )

    def _get_milk_quality(self, pastures):
        total = 100 * self.pastures_productivity(pastures)
        if total > 100:
            return 100
        else:
            return round(total)

    def pastures_productivity(self, pastures):
        return ((self.size / pastures) ** -0.3) * 2


class PotatoFarm(ce_models.Farm):
    VEG_TYPE = (Potato, "potato")
    name = models.CharField(default="Farma ziemniaków", max_length=20)
    profession_type_provided = models.CharField(
        default="Farmer ziemniaków", max_length=30
    )
    time_to_grow_from = models.PositiveIntegerField(default=2)
    time_to_grow_to = models.PositiveIntegerField(default=6)
    max_harvest = models.PositiveIntegerField(default=500)


class BeanFarm(ce_models.Farm):
    VEG_TYPE = (Bean, "bean")
    name = models.CharField(default="Farma fasoli", max_length=15)
    profession_type_provided = models.CharField(default="Farmer fasoli", max_length=30)
    time_to_grow_from = models.PositiveIntegerField(default=4)
    time_to_grow_to = models.PositiveIntegerField(default=8)
    max_harvest = models.PositiveIntegerField(default=500)


class LettuceFarm(ce_models.Farm):
    VEG_TYPE = (Lettuce, "lettuce")
    name = models.CharField(default="Farma sałaty", max_length=15)
    profession_type_provided = models.CharField(default="Farmer sałaty", max_length=30)
    time_to_grow_from = models.PositiveIntegerField(default=3)
    time_to_grow_to = models.PositiveIntegerField(default=5)
    max_harvest = models.PositiveIntegerField(default=500)

from django.apps import apps

from city_engine.temp_models import DataContainersWithEmployees
from resources import models as r_models


class MarketDataContainer:
    def __init__(self, instance):
        self.mi = instance
        self.resources = {}
        self.create_resources_in_market(instance)

    def create_resources_in_market(self, instance):
        subclasses = (
            model
            for model in apps.get_app_config("resources").get_models()
            if issubclass(model, r_models.MarketResource) and model is not r_models.MarketResource
        )
        for sub in subclasses:
            if sub.objects.filter(market=instance).exists():
                self.resources[sub] = TempResources(
                    list(sub.objects.filter(market=instance))
                )

    def save_all(self):
        for good in self.resources:
            self.resources[good].save_all()

    def _calculate_new_price(self, resource_in_market, size, price):
        return (resource_in_market.price + price) / (resource_in_market.size + size)

    def add_new_resource(self, resource_type, size, quality, price, market):
        if resource_type in self.resources:
            for resource_in_market in self.resources[resource_type].instances:
                if quality == resource_in_market.quality:
                    resource_in_market.size += size
                    resource_in_market.price = self._calculate_new_price(
                        resource_in_market, size, price
                    )
                    return
            self.resources[resource_type].instances.append(
                resource_type.objects.create(
                    size=size, quality=quality, price=price, market=market
                )
            )
        else:
            self.resources[resource_type] = TempResources(
                [resource_type.objects.create(size=size, quality=quality, price=price, market=market)]
            )


class TempResources:
    def __init__(self, instances_list):
        self.instances = instances_list
        self.total_size = self._get_total_size()
        self.avg_quality = self._get_avg_quality()
        self.avg_price = self._get_avg_price()

    def _get_total_size(self):
        return sum([x.size for x in self.instances])

    def _get_avg_quality(self):
        return sum([x.quality for x in self.instances]) / len(self.instances)

    def _get_avg_price(self):
        return sum([x.price for x in self.instances]) / len(self.instances)

    def save_all(self):
        for good in self.instances:
            if good.size > 0:
                good.save()
            elif good.id is not None and good.size == 0:
                good.delete()


class TempMassConverter(DataContainersWithEmployees):
    def __init__(self, instance, profile, market):
        super().__init__(instance, profile, market)

    def product_mass(self):
        size_total = int(
            self.instance.mass_production_rate * self._get_productivity())
        size = size_total if size_total > 1 else 1
        quality = self._get_quality()
        price = self.instance.calculate_price_of_good(
            self.workers_costs, size
        )

        if quality > 0 and len(self.all_people_in_building) >= 1:
            self.market.add_new_resource(r_models.Mass, size, quality, price, self.market.mi)
from resources import models as r_models
from resources.temp_models import TempResources
from city_engine.temp_models import DataContainersWithEmployees
from django.db.models import F


class TempCompany(DataContainersWithEmployees):
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees)
        self.market = market
        self.goods = {}

    def _get_row_col_cor(self):
        return (self.instance.trade_district.city_field.row, self.instance.trade_district.city_field.col)

    def create_goods(self):
        if self._get_productivity():
            materials = []
            self.buy_components(materials)
            if materials:
                self.make_goods_from_components(materials)

    def buy_components(self, materials):
        total_price = 0
        COMPONENTS = self.available_components
        for component_type in COMPONENTS:
            if component_type in self.market.resources:
                for component in self.market.resources[component_type].instances:
                    if self.instance.cash >= component.price:
                        temp_comp = component_type.objects.create(size=0, quality=component.quality, market=self.market.mi)
                        temp_comp.price = component.price  # To Remove
                        while self.instance.cash >= component.price and component.size > 0:
                            self.instance.cash -= component.price
                            total_price += component.price
                            temp_comp.size += 1
                            component.size -= 1

                        materials.append(temp_comp)
                        if component.size == 0:
                            component.delete()

        self.instance.cash = F("cash") - total_price
        self.instance.save(update_fields=['cash'])

    def make_goods_from_components(self, materials):
        # self_data_container = data.list_of_workplaces[self]
        GOODS_TO_PRODUCT = self.goods_to_product
        for good_type in GOODS_TO_PRODUCT:
            for material in materials:
                self.add_new_good(
                    good_type, material.size,
                    self._get_quality_of_product(material.quality),
                    material.price
                )

                material.delete()
                materials.pop(materials.index(material))

    def _get_quality_of_product(self, product_quality):
        quality = [product_quality, self._get_quality()]
        return round((sum(quality) / len(quality)) * self._get_productivity())

    def _get_quality(self):
        total = []
        e = [
            (self.elementary_employees, self.instance.elementary_employee_needed),
            (self.college_employees, self.instance.college_employee_needed),
            (self.phd_employees, self.instance.phd_employee_needed)
        ]
        for employees, needed_employees in e:
            if employees and needed_employees:
                total.append(self._get_sum_edu_effectiveness(employees) / needed_employees / 3)
        return sum(total)

    def _calculate_operation_requirements(self):
        self.water_required = len(self.all_employees) * 2
        self.energy_required = len(self.all_employees) * 4

    def save_all(self):
        for good in self.goods:
            self.goods[good].save_all()

    def _calculate_new_price(self, resource_in_company, size, price):
        return (resource_in_company.price + price) / (resource_in_company.size + size)

    def add_new_good(self, good_type, size, quality, price):
        if good_type in self.goods:
            for good_in_company in self.goods[good_type].instances:
                if good_in_company.quality == quality:
                    good_in_company.size += size
                    good_in_company.price = price
                    return
            self.goods[good_type].instances.append(
                good_type.objects.create(size=size, quality=quality, price=price, company=self.instance)
            )
        else:
            self.goods[good_type] = TempResources(
                [good_type.objects.create(size=size, quality=quality, price=price, company=self.instance)]
            )

    def create_goods_produced_by_company(self):
        for good in self.goods_to_product:
            if good.objects.filter(company=self.instance).exists():
                self.goods[good] = TempResources(
                    instances_list=list(good.objects.filter(company=self.instance))
                )


class TempFoodCompany(TempCompany):
    def __init__(self, instance, profile, employees, market):
        super().__init__(instance, profile, employees, market)
        self.available_components = [r_models.Mass]
        self.goods_to_product = [r_models.Food]
        self.create_goods_produced_by_company()
        self._calculate_operation_requirements()

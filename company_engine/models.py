from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from city_engine.models import TradeDistrict, Trash
from resources.models import Resource
import decimal


class Company(models.Model):
    trade_district = models.ForeignKey(TradeDistrict)
    name = models.CharField(max_length=20)
    cash = models.DecimalField(decimal_places=2, max_digits=20, default=0)

    trash = GenericRelation(Trash)

    profession_type_provided = models.CharField(default="", max_length=1)
    elementary_employee_needed = models.PositiveIntegerField(default=5)
    college_employee_needed = models.PositiveIntegerField(default=0)
    phd_employee_needed = models.PositiveIntegerField(default=0)
    employee = GenericRelation(
        to="citizen_engine.Citizen",
        object_id_field="workplace_object_id",
        content_type_field="workplace_content_type",
    )

    def wage_payment(self, city, data):
        import decimal

        total_payment = []
        for e in data.list_of_workplaces[self].all_employees:
            se = decimal.Decimal(data.citizens_in_city[e].salary_expectation)
            e.cash += se
            city.cash -= se
            total_payment.append(se)
        data.list_of_workplaces[self].workers_costs = sum(total_payment)

    def update_proficiency_of_profession_for_employees(self, employees):
        for employee in employees:
            employee.current_profession.update_proficiency(employee)

    def calculate_price_of_good(self, workers_costs, size_of_production):
        if workers_costs and size_of_production:
            return workers_costs / decimal.Decimal(size_of_production)
        return 0

    def create_goods(self, data):
        if self._get_productivity(data):
            materials = []
            self.buy_components(materials, data)
            if materials:
                self.make_goods_from_components(materials, data)

    def make_goods_from_components(self, materials, data):
        self_data_container = data.list_of_workplaces[self]
        GOODS_TO_PRODUCT = self_data_container.goods_to_product
        for good_type in GOODS_TO_PRODUCT:
            for material in materials:
                data.list_of_workplaces[self].add_new_good(
                    good_type,
                    material.size,
                    self._get_quality_of_product(material.quality, data),
                    material.price,
                )

                material.delete()
                materials.pop(materials.index(material))

    def buy_components(self, materials, data):
        COMPONENTS = data.list_of_workplaces[self].available_components
        for component_type in COMPONENTS:
            if component_type in data.market.resources:
                for component in data.market.resources[component_type].instances:
                    if self.cash >= component.price:
                        temp_comp = component_type.objects.create(
                            size=0, quality=component.quality, market=data.market.mi
                        )
                        temp_comp.price = component.price  # To Remove
                        while self.cash >= component.price and component.size > 0:
                            self.cash -= component.price
                            temp_comp.size += 1
                            component.size -= 1

                        materials.append(temp_comp)
                        if component.size == 0:
                            component.delete()

    def _get_quality_of_product(self, product_quality, data):
        quality = [product_quality, self._get_quality(data)]
        return round((sum(quality) / len(quality)) * self._get_productivity(data))

    def _get_productivity(self, data):
        productivity = [
            self._get_energy_productivity(data),
            self._get_water_productivity(data),
        ]
        return sum(productivity) / len(productivity)

    def _get_energy_productivity(self, data):
        self_data_container = data.list_of_workplaces[self]
        if self_data_container.water_required:
            return self_data_container.energy / self_data_container.energy_required
        else:
            return 0

    def _get_water_productivity(self, data):
        self_data_container = data.list_of_workplaces[self]
        if self_data_container.energy_required:
            return self_data_container.water / self_data_container.water_required
        else:
            return 0

    def _get_quality(self, data):
        total = []
        employee_categories = [
            "elementary_employees",
            "college_employees",
            "phd_employees",
        ]
        employee_categories_needed = [
            "elementary_employee_needed",
            "college_employee_needed",
            "phd_employee_needed",
        ]
        for e_cat, e_cat_needed in zip(employee_categories, employee_categories_needed):
            employees = self._get_employee_by_appendix(
                data.list_of_workplaces, data.citizens_in_city, e_cat
            )
            if employees:
                total.append(
                    self._get_sum_edu_effectiveness(employees)
                    / getattr(self, e_cat_needed)
                    / 3
                )
        return sum(total)

    def _get_employee_by_appendix(self, workplaces, citizens, appendix):
        return (
            [citizens[e] for e in getattr(workplaces[self], appendix)]
            if getattr(workplaces[self], appendix)
            else []
        )

    def _get_avg_all_edu_effectiveness(self, citizen):
        return sum([edu.effectiveness for edu in citizen.educations]) / len(
            [edu.effectiveness for edu in citizen.educations]
        )

    def _get_sum_edu_effectiveness(self, employee_cat):
        return sum([self._get_avg_all_edu_effectiveness(c) for c in employee_cat])

    class Meta:
        abstract = True


class FoodCompany(Company):
    elementary_employee_needed = models.PositiveIntegerField(default=5)


class Food(Resource):
    company = models.ForeignKey(FoodCompany)
    name = models.CharField(default="Jedzenie", max_length=9)
    quality = models.PositiveIntegerField(default=0)

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from city_engine import models as ce_models
import decimal
import company_engine.temp_models as ce_temp_model


class Company(models.Model):
    temp_model = ce_temp_model.TempCompany
    trade_district = models.ForeignKey(ce_models.TradeDistrict, on_delete=True)
    name = models.CharField(max_length=20)
    cash = models.DecimalField(decimal_places=2, max_digits=20, default=0)

    trash = GenericRelation(ce_models.Trash)

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
                total.append(self._get_sum_edu_effectiveness(employees) / getattr(self, e_cat_needed) / 3)
        return sum(total)

    def _get_employee_by_appendix(self, workplaces, citizens, appendix):
        return (
            [citizens[e] for e in getattr(workplaces[self], appendix)] if getattr(workplaces[self], appendix) else []
        )

    def _get_avg_all_edu_effectiveness(self, citizen):
        return sum([edu.effectiveness for edu in citizen.educations]) / len([edu.effectiveness for edu in citizen.educations])

    def _get_sum_edu_effectiveness(self, employee_cat):
        return sum([self._get_avg_all_edu_effectiveness(c) for c in employee_cat])

    class Meta:
        abstract = True


class FoodCompany(Company):
    temp_model = ce_temp_model.TempFoodCompany
    elementary_employee_needed = models.PositiveIntegerField(default=5)

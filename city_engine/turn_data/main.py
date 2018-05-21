from city_engine.main_view_data.employee_allocation import EmployeeAllocation
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.main_view_data.trash_management import TrashManagement
from city_engine.abstract import RootClass
from city_engine.models import CityField, Vehicle


class TurnCalculation(object):

    def __init__(self, city):
        self.city = city
        self.data = RootClass(self.city)

    def run(self):
        TrashManagement(self.city, self.data).run()
        EmployeeAllocation(self.city, self.data).run()
        ResourceAllocation(self.city, self.data).run()
        self.execute_maintenance()
        self.update_build_status()
        self.city.save()

    def update_build_status(self):
        for building in self.data.list_of_buildings_only:
            if building.if_under_construction is True:
                building.build_status()

    def calculate_maintenance_cost(self):
        return sum([b['maintenance_cost'] for b in self.data.list_of_building_with_values])

    def execute_maintenance(self):
        self.city.cash - self.calculate_maintenance_cost()

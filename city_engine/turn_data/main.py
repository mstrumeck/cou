from city_engine.main_view_data.employee_allocation import EmployeeAllocation
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.main_view_data.trash_management import TrashManagement
from city_engine.abstract import RootClass


class TurnCalculation(RootClass):

    def run(self):
        TrashManagement(self.city).run()
        EmployeeAllocation(self.city).run()
        ResourceAllocation(self.city).run()
        self.execute_maintenance()
        self.update_build_status()
        self.city.save()

    def update_build_status(self):
        for building in self.list_of_buildings_in_city_with_only('if_under_construction'):
            if building.if_under_construction is True:
                building.build_status()

    def calculate_maintenance_cost(self):
        return sum([b['maintenance_cost'] for b in self.list_of_buildings_in_city_with_values('maintenance_cost')])

    def execute_maintenance(self):
        self.city.cash - self.calculate_maintenance_cost()

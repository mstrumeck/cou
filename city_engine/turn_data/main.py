from city_engine.main_view_data.employee_allocation import EmployeeAllocation
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.main_view_data.trash_management import TrashManagement, CollectGarbage


class TurnCalculation(object):

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def run(self):
        TrashManagement(self.data).run()
        EmployeeAllocation(self.city, self.data).run()
        ResourceAllocation(self.city, self.data).run()
        CollectGarbage(self.city, self.data).run()
        self.execute_maintenance()
        self.update_build_status()
        # self.city.save()

    def update_build_status(self):
        for building in self.data.list_of_buildings_only:
            if building.if_under_construction is True:
                building.build_status()

    def calculate_maintenance_cost(self):
        return sum([b['maintenance_cost'] for b in self.data.list_of_building_with_values])

    def execute_maintenance(self):
        self.city.cash - self.calculate_maintenance_cost()

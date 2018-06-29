from city_engine.main_view_data.employee_allocation import EmployeeAllocation
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.main_view_data.trash_management import TrashManagement, CollectGarbage
from city_engine.models import Farm, AnimalFarm, Milk, Cattle


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
        self.update_harvest_status()
        self.update_breeding_status()

    def update_breeding_status(self):
        for farm in [b for b in self.data.list_of_buildings if isinstance(b, AnimalFarm)]:
            farm.farm_operation(self.data.user)

    def update_harvest_status(self):
        for farm in [b for b in self.data.list_of_buildings if isinstance(b, Farm)]:
            farm.update_harvest(self.data.user)

    def update_build_status(self):
        for building in self.data.list_of_buildings:
            if building.if_under_construction is True:
                building.build_status()

    def calculate_maintenance_cost(self):
        return sum([b['maintenance_cost'] for b in self.data.list_of_building_with_values])

    def execute_maintenance(self):
        self.city.cash - self.calculate_maintenance_cost()

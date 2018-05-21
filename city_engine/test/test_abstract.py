from city_engine.abstract import RootClass
from django import test
from city_engine.main_view_data.city_stats import CityStatsCenter, CityEnergyStats, CityWaterStats, CityBuildingStats, CityPopulationStats
from city_engine.main_view_data.employee_allocation import EmployeeAllocation
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import CityField, City, WindPlant, WaterTower, PowerPlant,\
    Waterworks, RopePlant, CoalPlant, Residential, ProductionBuilding, DumpingGround, DustCart
from django.db.models import Sum
from .base import TestHelper


class InheritClass(RootClass):
    pass


class TestRootClass(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.RC = InheritClass(city=City.objects.latest('id'))

    # def test_dataset_for_water_allocation(self):
    #     # print(self.RC.power_plant_buildings)
    #     self.RA = ResourceAllocation(city=City.objects.latest('id'), data=self.RC)
    #     self.RC.create_dataset_for_turn_calculation()
    #     self.RA.resource_allocation(self.RC.powerplant_resources_allocation)

    def test_get_subclasses(self):
        self.assertEqual(self.RC.get_subclasses(abstract_class=PowerPlant, app_label='city_engine'),
                         [WindPlant, RopePlant, CoalPlant])
        self.assertEqual(self.RC.get_subclasses(abstract_class=Waterworks, app_label='city_engine'),
                         [WaterTower])

    def test_get_subclasses_of_all_buildings(self):
        self.assertEqual(self.RC.get_subclasses_of_all_buildings(),
                         [Residential, ProductionBuilding, WindPlant, RopePlant, CoalPlant, WaterTower, DumpingGround])

    def test_list_of_building_in_city(self):
        self.assertEqual(self.RC.list_of_buildings,
                         [Residential.objects.latest('id'), WindPlant.objects.get(id=1), WindPlant.objects.get(id=2),
                          WaterTower.objects.get(id=1), WaterTower.objects.get(id=2), DumpingGround.objects.latest('id')])

    def test_list_of_workplaces(self):
        self.assertEqual(self.RC.list_of_workplaces(),
                         [WindPlant.objects.get(id=1), WindPlant.objects.get(id=2),WaterTower.objects.get(id=1),
                          WaterTower.objects.get(id=2), DumpingGround.objects.latest('id'), DustCart.objects.latest('id')])
        self.assertNotIn(self.RC.list_of_workplaces(), [Residential.objects.latest('id')])

    def test_list_of_buildings_in_city_with_values(self):
        self.assertEqual(self.RC.list_of_buildings_in_city_with_values('energy', 'water'),
                         [{'energy': 0, 'water': 0}, {'energy': 0, 'water': 0}, {'energy': 0, 'water': 0},
                          {'energy': 0, 'water': 0}, {'energy': 0, 'water': 0}, {'energy': 0, 'water': 0}])
        self.assertEqual(self.RC.list_of_buildings_in_city_with_values('if_under_construction'),
                         [{'if_under_construction': False}, {'if_under_construction': False},
                          {'if_under_construction': False}, {'if_under_construction': False},
                          {'if_under_construction': False}, {'if_under_construction': False}])
        self.assertEqual(self.RC.list_of_buildings_in_city_with_values('name'),
                         [{'name': 'Budynek Mieszkalny'}, {'name': 'Elektrownia wiatrowa'},
                          {'name': 'Elektrownia wiatrowa'}, {'name': 'Wieża ciśnień'}, {'name': 'Wieża ciśnień'},
                          {'name': 'Wysypisko śmieci'}])

    def test_list_of_building_in_city_with_only(self):
        test_data = self.RC.list_of_buildings_in_city_with_only('energy', 'water', 'if_under_construction', 'name')
        self.assertEqual(test_data, [Residential.objects.latest('id'), WindPlant.objects.get(id=1),
                                     WindPlant.objects.get(id=2), WaterTower.objects.get(id=1),
                                     WaterTower.objects.get(id=2), DumpingGround.objects.latest('id')])
        for item in test_data:
            self.assertEqual(item.__dict__['name'], item.name)
            self.assertEqual(item.__dict__['energy'], item.energy)
            self.assertEqual(item.__dict__['water'], item.water)
            self.assertEqual(item.__dict__['if_under_construction'], item.if_under_construction)
from city_engine.abstract import RootClass
from django import test
from city_engine.models import City, WindPlant, WaterTower, PowerPlant,\
    Waterworks, RopePlant, CoalPlant, Residential, ProductionBuilding, DumpingGround, DustCart, SewageWorks


class TestRootClass(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.RC = RootClass(city=City.objects.latest('id'))

    def test_keys_in_dataset(self):
        for x in self.RC.datasets_for_turn_calculation():
            self.assertIn('allocated_resource', x.keys())
            self.assertIn('list_of_source', x.keys())
            self.assertIn('list_without_source', x.keys())

    def test_get_subclasses(self):
        self.assertEqual(self.RC.get_subclasses(abstract_class=PowerPlant, app_label='city_engine'),
                         [WindPlant, RopePlant, CoalPlant])
        self.assertEqual(self.RC.get_subclasses(abstract_class=Waterworks, app_label='city_engine'),
                         [WaterTower])

    def test_get_subclasses_of_all_buildings(self):
        self.assertEqual(self.RC.get_subclasses_of_all_buildings(),
                         [Residential, ProductionBuilding, WindPlant, RopePlant, CoalPlant, WaterTower,
                          SewageWorks, DumpingGround])

    def test_list_of_building_in_city(self):
        self.assertEqual(self.RC.list_of_buildings,
                         [Residential.objects.latest('id'), WindPlant.objects.get(id=1), WindPlant.objects.get(id=2),
                          WaterTower.objects.get(id=1), WaterTower.objects.get(id=2), SewageWorks.objects.latest('id'),
                          DumpingGround.objects.latest('id')])

    def test_list_of_workplaces(self):
        self.assertEqual(self.RC.list_of_workplaces(),
                         [WindPlant.objects.get(id=1), WindPlant.objects.get(id=2), WaterTower.objects.get(id=1),
                          WaterTower.objects.get(id=2),  SewageWorks.objects.latest('id'),
                          DumpingGround.objects.latest('id'), DustCart.objects.latest('id')])
        self.assertNotIn(self.RC.list_of_workplaces(), [Residential.objects.latest('id')])

    def test_list_of_buildings_in_city_with_values(self):
        self.assertEqual(self.RC.list_of_buildings_in_city_with_values('energy', 'water'),
                         [{'energy': 0, 'water': 0}, {'energy': 0, 'water': 0}, {'energy': 0, 'water': 0},
                          {'energy': 0, 'water': 0}, {'energy': 0, 'water': 0}, {'energy': 0, 'water': 0},
                          {'energy': 0, 'water': 0}])
        self.assertEqual(self.RC.list_of_buildings_in_city_with_values('if_under_construction'),
                         [{'if_under_construction': False}, {'if_under_construction': False},
                          {'if_under_construction': False}, {'if_under_construction': False},
                          {'if_under_construction': False}, {'if_under_construction': False}, {'if_under_construction': False}])
        self.assertEqual(self.RC.list_of_buildings_in_city_with_values('name'),
                         [{'name': 'Budynek Mieszkalny'}, {'name': 'Elektrownia wiatrowa'},
                          {'name': 'Elektrownia wiatrowa'}, {'name': 'Wieża ciśnień'}, {'name': 'Wieża ciśnień'},
                          {'name': 'Oczyszczalnia ścieków'}, {'name': 'Wysypisko śmieci'}])
    #
    def test_list_of_building_in_city_with_only(self):
        test_data = self.RC.list_of_buildings_in_city_with_only('energy', 'water', 'if_under_construction', 'name')
        self.assertEqual(test_data, [Residential.objects.latest('id'), WindPlant.objects.get(id=1),
                                     WindPlant.objects.get(id=2), WaterTower.objects.get(id=1),
                                     WaterTower.objects.get(id=2), SewageWorks.objects.latest('id'),
                                     DumpingGround.objects.latest('id')])
        for item in test_data:
            self.assertEqual(item.__dict__['name'], item.name)
            self.assertEqual(item.__dict__['energy'], item.energy)
            self.assertEqual(item.__dict__['water'], item.water)
            self.assertEqual(item.__dict__['if_under_construction'], item.if_under_construction)
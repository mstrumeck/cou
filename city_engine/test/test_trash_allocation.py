from django import test
from city_engine.main_view_data.trash_management import TrashManagement, CollectGarbage
from city_engine.models import DumpingGround, City, DustCart, CityField, WindPlant, WaterTower, Building, list_of_workplaces
import random
from city_engine.main_view_data.global_variables import HEX_NUM_IN_ROW
from citizen_engine.models import Citizen
from citizen_engine.citizen_creation import CreateCitizen
from city_engine.test.base import TestHelper


class TestTrashAllocation(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.trash_management = TrashManagement(city=self.city)
        self.collect_garbage = CollectGarbage(city=self.city)
        self.wind_plant = WindPlant.objects.latest('id')
        self.water_tower = WaterTower.objects.latest('id')
        self.populate_city(self.city)

    def test_of_collect_garbage(self):
        DumpingGround.objects.update(current_space_for_trash=0)
        dumping_ground = DumpingGround.objects.latest('id')
        self.assertEqual(dumping_ground.current_space_for_trash, 0)
        self.trash_management.generate_trash()
        self.collect_garbage.run()
        dumping_ground = DumpingGround.objects.latest('id')
        self.assertNotEqual(self.trash_management.list_of_all_trashes_in_city(), [])
        self.assertGreater(dumping_ground.current_space_for_trash, 20)

    def test_existing_dumping_grounds_with_slots(self):
        self.assertEqual(self.collect_garbage.existing_dumping_grounds_with_slots(), [DumpingGround.objects.latest('id')])
        DumpingGround.objects.latest('id').delete()
        self.assertEqual(self.collect_garbage.existing_dumping_grounds_with_slots(), [])

    def test_existing_dust_carts(self):
        dg = DumpingGround.objects.get(id=1)
        self.assertEqual(self.collect_garbage.existing_dust_carts(dg), [DustCart.objects.latest('id')])
        DustCart.objects.latest('id').delete()
        self.assertEqual(self.collect_garbage.existing_dust_carts(dg), [])

    def test_city_field_from_corr(self):
        for z in range(30):
            x = random.randint(0, HEX_NUM_IN_ROW-1)
            y = random.randint(0, HEX_NUM_IN_ROW-1)
            self.assertEqual(self.collect_garbage.city_field_from_corr((x, y)), CityField.objects.get(row=x, col=y, city=self.city))

    def test_search_building_with_corr(self):
        self.assertEqual(self.collect_garbage.search_building_with_corr(CityField.objects.get(id=7)), self.wind_plant)
        self.assertEqual(self.collect_garbage.search_building_with_corr(CityField.objects.get(id=11)), self.water_tower)
        self.assertEqual(self.collect_garbage.search_building_with_corr(CityField.objects.get(id=1)), None)

    def delete_all_trashes(self, building):
        for trash in self.collect_garbage.list_of_trash_for_building(building):
            trash.delete()

    def test_list_of_trash_for_building(self):
        self.delete_all_trashes(WindPlant.objects.latest('id'))
        self.delete_all_trashes(WaterTower.objects.latest('id'))
        self.delete_all_trashes(DumpingGround.objects.latest('id'))
        self.assertEqual(self.collect_garbage.list_of_trash_for_building(WindPlant.objects.latest('id')), [])
        self.assertEqual(self.collect_garbage.list_of_trash_for_building(WaterTower.objects.latest('id')), [])

        self.trash_management.generate_trash()
        self.assertNotEqual(self.collect_garbage.list_of_trash_for_building(WindPlant.objects.latest('id')), [])
        self.assertNotEqual(self.collect_garbage.list_of_trash_for_building(WaterTower.objects.latest('id')), [])
        self.assertEqual(self.collect_garbage.list_of_trash_for_building(DumpingGround.objects.latest('id')), [])

    def test_collect_trash_by_dust_cart(self):
        DumpingGround.objects.update(current_space_for_trash=0)
        self.delete_all_trashes(WindPlant.objects.latest('id'))
        self.delete_all_trashes(WaterTower.objects.latest('id'))
        self.delete_all_trashes(DumpingGround.objects.latest('id'))
        self.assertEqual(self.collect_garbage.list_of_trash_for_building(WindPlant.objects.latest('id')), [])
        self.assertEqual(self.collect_garbage.list_of_trash_for_building(WaterTower.objects.latest('id')), [])
        self.trash_management.generate_trash()
        self.assertNotEqual(self.collect_garbage.list_of_trash_for_building(WindPlant.objects.latest('id')), [])
        self.assertNotEqual(self.collect_garbage.list_of_trash_for_building(WaterTower.objects.latest('id')), [])
        self.assertEqual(DumpingGround.objects.latest('id').current_space_for_trash, 0)
        self.collect_garbage.run()
        self.assertGreater(DumpingGround.objects.latest('id').current_space_for_trash, 20)

    def test_max_capacity_of_cart(self):
        self.assertEqual(DustCart.objects.latest('id').effectiveness(), 1.0)
        DustCart.objects.latest('id').employee.latest('id').delete()
        self.assertEqual(DustCart.objects.latest('id').effectiveness(), 0.6666666666666666)
        DustCart.objects.latest('id').employee.latest('id').delete()
        self.assertEqual(DustCart.objects.latest('id').effectiveness(), 0.3333333333333333)
        DustCart.objects.latest('id').employee.latest('id').delete()
        self.assertEqual(DustCart.objects.latest('id').effectiveness(), 0.0)

    def test_unload_trashes_from_cart(self):
        DumpingGround.objects.update(current_space_for_trash=0)
        self.assertEqual(DustCart.objects.latest('id').curr_capacity, 0)
        DustCart.objects.update(curr_capacity=40)
        self.assertEqual(DustCart.objects.latest('id').curr_capacity, 40)
        self.collect_garbage.unload_trashes_from_cart(dc=DustCart.objects.latest('id'), dg=DumpingGround.objects.latest('id'))
        self.assertEqual(DustCart.objects.latest('id').curr_capacity, 0)
        self.assertEqual(DumpingGround.objects.latest('id').current_space_for_trash, 40)

    def test_collect_garbage(self):
        self.assertEqual(self.collect_garbage.get_subclasses_of_all_buildings(),
                         self.collect_garbage.get_subclasses(abstract_class=Building, app_label='city_engine'))
from django import test
from city_engine.main_view_data.trash_management import TrashManagement, CollectGarbage
from city_engine.models import DumpingGround, City


class TestTrashAllocation(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def test_of_collect_garbage(self):
        city = City.objects.get(id=1)
        trash_management = TrashManagement(city=city)
        collect_garbage = CollectGarbage(city=city)
        dumping_ground = DumpingGround.objects.get(id=1)
        self.assertEqual(dumping_ground.current_space_for_trash, 0)
        trash_management.generate_trash()
        collect_garbage.collect_garbage()
        dumping_ground = DumpingGround.objects.get(id=1)
        self.assertNotEqual(trash_management.list_of_all_trashes_in_city(), [])
        self.assertGreater(dumping_ground.current_space_for_trash, 40)

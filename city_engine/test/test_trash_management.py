from django import test
from city_engine.main_view_data.trash_management import TrashManagement
from city_engine.models import City, list_of_models, Trash


class CityStatsTests(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.TM = TrashManagement(self.city)

    def print_all_building_in_the_city(self):
        result = []
        for building_type in list_of_models:
            if building_type.objects.exists_in_city(self.city):
                result += building_type.objects.filter_by_city(self.city)
        return result

    def test_generate_trash(self):
        result = []
        for building in self.print_all_building_in_the_city():
            for trash in building.trash.values():
                result.append(trash)
        self.assertEqual(len(result), 0)

        self.TM.generate_trash()

        for building in self.print_all_building_in_the_city():
            for trash in building.trash.values():
                result.append(trash)
        self.assertEqual(len(result), 4)

    def test_update_time(self):
        self.TM.generate_trash()
        for building in self.print_all_building_in_the_city():
            for trash in building.trash.values('time'):
                self.assertEqual(trash['time'], 0)
        self.TM.update_trash_time()
        for building in self.print_all_building_in_the_city():
            for trash in building.trash.values('time'):
                self.assertEqual(trash['time'], 1)

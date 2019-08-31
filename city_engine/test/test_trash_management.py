from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Profession, Education, Family
from city_engine.main_view_data.trash_management import TrashManagement
from city_engine.models import City, DumpingGround, Field
from city_engine.test.base import TestHelper
from cou.turn_data import RootClass
from resources.models import Market


class CityStatsTests(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def tearDown(self):
        Citizen.objects.all().delete()
        Profession.objects.all().delete()
        Education.objects.all().delete()
        Family.objects.all().delete()
        Market.objects.all().delete()

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, self.user).populate_city()
        self.RC = RootClass(self.city, self.user)
        self.TM = TrashManagement(self.RC)

    def test_generate_trash_except_dumping_ground(self):
        dg = DumpingGround.objects.create(
            city=self.city, city_field=Field.objects.latest('id')
        )
        result = []
        for trash in dg.trash.values():
            result.append(trash)
        self.assertEqual(result, [])

        self.TM.generate_trash()

        for trash in dg.trash.values():
            result.append(trash)
        self.assertEqual(result, [])

    def test_generate_trash(self):
        self.assertEqual(sum([len(b.temp_trash) for b in self.RC.list_of_buildings.values()]), 0)
        self.TM.generate_trash()
        self.assertEqual(sum([len(b.temp_trash) for b in self.RC.list_of_buildings.values()]), 5)

    def test_update_time(self):
        self.TM.generate_trash()
        for building in self.RC.list_of_buildings:
            for trash in building.trash.values("time"):
                self.assertEqual(trash["time"], 0)
        self.TM.update_trash_time()
        for building in self.RC.list_of_buildings:
            for trash in building.trash.values("time"):
                self.assertEqual(trash["time"], 1)


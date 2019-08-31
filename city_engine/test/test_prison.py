from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Education, Family
from citizen_engine.models import Profession
from city_engine.models import (
    City,
)
from city_engine.models import Prison, PoliceStation
from city_engine.test.base import TestHelper
from city_engine.turn_data.calculation import TurnCalculation
from cou.turn_data import RootClass
from map_engine.models import Field
from resources.models import Market


class TestTempPrison(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def tearDown(self):
        Citizen.objects.all().delete()
        Profession.objects.all().delete()
        Education.objects.all().delete()
        Family.objects.all().delete()
        Market.objects.all().delete()
        PoliceStation.objects.all().delete()
        Prison.objects.all().delete()
        Market.objects.all().delete()

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        self.prison = Prison.objects.create(city=self.city, city_field=Field.objects.latest('id'))
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, self.user).populate_city()
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings.get(self.prison)

    def _put_citizens_to_jail(self, num_of_citizen=3):
        temp_citizens = Citizen.objects.exclude(workplace_object_id=self.prison.id)[:num_of_citizen]
        for c in temp_citizens:
            temp_citizen = self.rc.citizens_in_city[c]
            temp_citizen.change_citizen_into_criminal()
            temp_citizen.current_profession.proficiency = 0.25
            temp_citizen.current_profession.save()
            self.temp_prison.put_criminal_to_jail(temp_citizen)

    def test_is_temp_prison_exist(self):
        self.assertEqual(Prison.objects.count(), 1)
        self.assertTrue(self.rc.list_of_buildings.get(self.prison))

    def test_is_temp_prison_has_staff(self):
        self.assertEqual(self.temp_prison.prison_capacity, 15)
        self.assertEqual(self.temp_prison.water_required, 10)
        self.assertEqual(self.temp_prison.energy_required, 20)
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)
        self.assertEqual(len(self.temp_prison.elementary_employees), 10)
        self.assertEqual(len(self.temp_prison.college_employees), 5)

    def test_is_temp_prison_register_prison(self):
        self._put_citizens_to_jail(num_of_citizen=1)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        temp_prison = self.rc.list_of_buildings.get(self.prison)
        self.assertEqual(temp_prison.prison_capacity, 14)
        self.assertEqual(temp_prison.water_required, 13)
        self.assertEqual(temp_prison.energy_required, 23)
        self.assertEqual(temp_prison.num_of_prisoners, 1)

    def test_is_has_place_positive(self):
        self._put_citizens_to_jail(num_of_citizen=1)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        temp_prison = self.rc.list_of_buildings.get(self.prison)
        self.assertTrue(temp_prison.is_has_place())

    def test_is_has_place_negative(self):
        self._put_citizens_to_jail(num_of_citizen=16)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        temp_prison = self.rc.list_of_buildings.get(self.prison)
        self.assertFalse(temp_prison.is_has_place())

    def test_put_criminal_to_jail(self):
        temp_citizen = self.rc.citizens_in_city[Citizen.objects.latest('id')]
        self.assertEqual(Citizen.objects.filter(jail=self.temp_prison.instance).count(), 0)
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)
        self.temp_prison.put_criminal_to_jail(temp_citizen)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings.get(self.prison)
        self.assertEqual(Citizen.objects.filter(jail=self.temp_prison.instance).count(), 1)
        self.assertEqual(self.temp_prison.num_of_prisoners, 1)

    def test_if_rc_take_only_non_prisoner_citizen(self):
        self.assertEqual(len(self.rc.citizens_in_city), 43)
        self._put_citizens_to_jail(num_of_citizen=3)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(self.rc.citizens_in_city), 40)

    def test_conduct_rehabilitation(self):
        self._put_citizens_to_jail(num_of_citizen=3)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison.conduct_rehabilitation()
        for c in self.temp_prison.prisoners:
            temp_citizen = self.rc.citizens_in_city[c]
            self.assertLess(temp_citizen.current_profession.proficiency, 25)

    def test_release_criminal(self):
        self._put_citizens_to_jail(num_of_citizen=1)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(self.rc.citizens_in_city), 42)
        self.assertEqual(Citizen.objects.filter(jail__isnull=True).count(), 42)
        self.temp_prison = self.rc.list_of_buildings.get(self.prison)
        criminal = self.temp_prison.prisoners.pop()
        self.temp_prison.release_criminal(criminal)
        self.assertIsNone(criminal.instance.jail)
        self.assertIsNone(criminal.current_profession)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings.get(self.prison)
        self.assertEqual(Citizen.objects.filter(jail__isnull=True).count(), 43)
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)
        self.assertEqual(len(self.rc.citizens_in_city), 43)
        self.assertIsNone(criminal.current_profession)
        self.assertEqual(criminal.instance.jail, None)


class TestTempPrisonInTurnCalculation(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        last_field_id = Field.objects.latest('id').id
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        self.prison = Prison.objects.create(
            city=self.city,
            city_field=Field.objects.get(id=last_field_id-1),
            if_under_construction=False
        )
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, self.user).populate_city()
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings[self.prison]

    def tearDown(self):
        Citizen.objects.all().delete()
        Profession.objects.all().delete()
        Education.objects.all().delete()
        Family.objects.all().delete()
        Market.objects.all().delete()
        PoliceStation.objects.all().delete()
        Prison.objects.all().delete()
        Market.objects.all().delete()

    def test_temp_prison_in_turn_calculation(self):
        temp_citizens = Citizen.objects.all()[:3]
        temp_prison = self.rc.list_of_buildings.get(self.prison)
        for c in temp_citizens:
            temp_citizen = self.rc.citizens_in_city[c]
            temp_citizen.change_citizen_into_criminal()
            temp_citizen.current_profession.proficiency = 0.25
            temp_citizen.current_profession.save()
            temp_prison.put_criminal_to_jail(temp_citizen)

        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings[self.prison]

        self.assertEqual(self.temp_prison.water_required, 19)
        self.assertEqual(self.temp_prison.energy_required, 29)
        self.assertEqual(self.temp_prison.num_of_prisoners, 3)
        total_proficiency_before = (sum([x.current_profession.proficiency for x in self.temp_prison.prisoners]))
        TurnCalculation(self.city, self.rc, self.user.profile).run()
        self.assertLess(sum([x.current_profession.proficiency for x in self.temp_prison.prisoners]),
                        total_proficiency_before)
        self.assertGreater(self.temp_prison.energy, 0)
        self.assertEqual(self.temp_prison.num_of_prisoners, 3)

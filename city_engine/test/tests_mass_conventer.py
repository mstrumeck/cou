from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Education, Profession
from city_engine.models import City
from city_engine.test.base import TestHelper
from cou.abstract import RootClass
from map_engine.models import Field
from resources.models import Market, Mass, MassConventer


class TestMassConventer(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.mass_conventer = MassConventer.objects.create(
            city_id=1, city_field=Field.objects.latest('id'), if_under_construction=False
        )
        self.user = User.objects.latest('id')
        self.m = Market.objects.create(profile=self.user.profile)

    def tearDown(self):
        self.mass_conventer.college_employee_needed = 0
        self.mass_conventer.elementary_employee_needed = 0
        self.mass_conventer.phd_employee_needed = 0
        self.mass_conventer.save()
        Citizen.objects.all().delete()
        Education.objects.all().delete()
        Profession.objects.all().delete()

    def test_product_mass_with_standard_settings(self):
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.assertEqual(list(Mass.objects.all()), [])
        RC = RootClass(self.city, User.objects.latest("id"))
        mc = RC.list_of_workplaces[MassConventer.objects.latest('id')]
        mc.wage_payment(self.city)
        self.mass_conventer.product_mass(RC)
        self.assertNotEqual(list(Mass.objects.all()), [])
        self.assertEqual(float("{0:.2f}".format(Mass.objects.latest("id").quality)), 33)
        self.assertEqual(Mass.objects.latest("id").size, 33)
        self.assertEqual(Mass.objects.latest("id").name, "Masa")
        self.mass_conventer.product_mass(RC)
        RC.market.save_all()
        self.assertEqual(Mass.objects.all().count(), 1)
        self.assertEqual(Mass.objects.latest("id").size, 66)
        self.assertEqual(float(Mass.objects.latest("id").price), 0.49)

    def test_product_mass_failed(self):
        self.assertEqual(list(Mass.objects.all()), [])
        RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            len(RC.list_of_workplaces[self.mass_conventer].all_employees), 0
        )
        self.assertEqual(self.mass_conventer.employee.all().count(), 0)
        self.assertEqual(Mass.objects.all().count(), 0)
        mc = RC.list_of_workplaces[MassConventer.objects.latest('id')]
        mc.wage_payment(self.city)
        self.mass_conventer.product_mass(RC)
        self.assertEqual(
            len(RC.list_of_workplaces[self.mass_conventer].all_employees), 0
        )
        self.assertEqual(self.mass_conventer.employee.all().count(), 0)
        self.assertEqual(Mass.objects.all().count(), 0)

    def test_if_mass_converter_produce_two_unit(self):
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.assertEqual(list(Mass.objects.all()), [])
        RC = RootClass(self.city, User.objects.latest("id"))
        mc = RC.list_of_workplaces[MassConventer.objects.latest('id')]
        mc.wage_payment(self.city)
        self.mass_conventer.product_mass(RC)
        self.assertNotEqual(list(Mass.objects.all()), [])
        self.assertEqual(float("{0:.2f}".format(Mass.objects.latest("id").quality)), 33)
        self.assertEqual(Mass.objects.latest("id").size, 33)
        self.assertEqual(Mass.objects.latest("id").name, "Masa")
        self.assertEqual(self.mass_conventer.employee.all().count(), 5)
        RC.list_of_workplaces[self.mass_conventer].elementary_employees.pop()
        Citizen.objects.latest('id').delete()
        self.assertEqual(self.mass_conventer.employee.all().count(), 4)
        self.mass_conventer.product_mass(RC)
        [x.save() for x in RC.to_save]
        self.assertEqual(Mass.objects.all().count(), 2)
        self.assertEqual(Mass.objects.latest("id").size, 33)
        self.assertEqual(float("{0:.2f}".format(Mass.objects.latest("id").quality)), 27)
        self.assertEqual(float(Mass.objects.latest("id").price), 24.48)

    def test_quality_with_random_number_of_elementary_employee(self):
        import random

        self.mass_conventer.elementary_employee_needed = random.randrange(1, 20)
        self.mass_conventer.save()
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.assertEqual(list(self.m.mass_set.all()), [])
        RC = RootClass(self.city, User.objects.latest("id"))
        mc = RC.list_of_workplaces[MassConventer.objects.latest('id')]
        mc.wage_payment(self.city)
        self.mass_conventer.product_mass(RC)
        self.assertNotEqual(list(self.m.mass_set.all()), [])
        self.assertEqual(float("{0:.2f}".format(Mass.objects.latest("id").quality)), 33)

    def test_mass_quality_with_college_employee(self):
        import random

        self.mass_conventer.elementary_employee_needed = random.randrange(1, 20)
        self.mass_conventer.college_employee_needed = random.randrange(1, 20)
        self.mass_conventer.save()
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.assertEqual(list(Mass.objects.all()), [])
        RC = RootClass(self.city, User.objects.latest("id"))
        mc = RC.list_of_workplaces[MassConventer.objects.latest('id')]
        mc.wage_payment(self.city)
        self.mass_conventer.product_mass(RC)
        self.assertNotEqual(list(Mass.objects.all()), [])
        self.assertEqual(float("{0:.2f}".format(Mass.objects.latest("id").quality)), 67)

    def test_quality_with_all_employee_categories(self):
        import random

        self.mass_conventer.elementary_employee_needed = random.randrange(1, 20)
        self.mass_conventer.college_employee_needed = random.randrange(1, 20)
        self.mass_conventer.phd_employee_needed = random.randrange(1, 20)
        self.mass_conventer.save()
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.assertEqual(list(Mass.objects.all()), [])
        RC = RootClass(self.city, User.objects.latest("id"))
        mc = RC.list_of_workplaces[MassConventer.objects.latest('id')]
        mc.wage_payment(self.city)
        self.mass_conventer.product_mass(RC)
        self.assertNotEqual(list(Mass.objects.all()), [])
        self.assertEqual(Mass.objects.latest("id").quality, 100)

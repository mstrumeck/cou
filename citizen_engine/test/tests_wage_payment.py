from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import City, WindPlant, CityField, PrimarySchool,\
    DustCart, DumpingGround, WaterTower, StandardLevelResidentialZone
from citizen_engine.models import Citizen, Profession, Education
from citizen_engine.citizen_creation import CreateCitizen
import random, string
from cou.abstract import RootClass
from player.models import Profile
from cou.global_var import MALE, FEMALE, ELEMENTARY, COLLEGE, PHD, TRAINEE, JUNIOR, REGULAR, MASTER, PROFESSIONAL
from citizen_engine.work_engine import CitizenWorkEngine
from resources.models import Market


class WagePaymentTest(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.user = User.objects.latest('id')
        self.profile = Profile.objects.latest('id')
        Market.objects.create(profile=self.profile)
        self.r1 = StandardLevelResidentialZone.objects.latest('id')
        self.school = PrimarySchool.objects.create(
                city=self.city,
                city_field=CityField.objects.latest('id')
            )
        self.s = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            edu_title=COLLEGE,
            resident_object=self.r1,
            workplace_object=self.school
        )

    def test_wage_payment_for_one_person_pass_with_two_education(self):
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=self.s, proficiency=0.4, name='Nauczyciel', education=COLLEGE)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(self.city.cash, 9480)
        self.assertEqual(RC.citizens_in_city[self.s].ci.cash, 100)
        self.assertEqual(RC.list_of_workplaces[self.school].workers_costs, 0)
        CitizenWorkEngine(RC, self.city).wage_payment_in_all_workplaces()
        self.assertEqual(round(RC.list_of_workplaces[self.school].workers_costs), 226)
        self.assertEqual(int(self.city.cash), 9253)
        self.assertEqual(int(RC.citizens_in_city[self.s].ci.cash), 326)

    def test_wage_payment_for_person_pass_with_one_education(self):
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=self.s, proficiency=0.4, name='Nauczyciel', education=ELEMENTARY)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(self.city.cash, 9480)
        self.assertEqual(RC.citizens_in_city[self.s].ci.cash, 100)
        self.assertEqual(RC.list_of_workplaces[self.school].workers_costs, 0)
        CitizenWorkEngine(RC, self.city).wage_payment_in_all_workplaces()
        self.assertEqual(round(RC.list_of_workplaces[self.school].workers_costs), 113)
        self.assertEqual(int(self.city.cash), 9366)
        self.assertEqual(int(RC.citizens_in_city[self.s].ci.cash), 213)

    def test_wage_payment_for_person_pass_with_three_educations(self):
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.s, name=PHD, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=self.s, proficiency=0.5, name='Nauczyciel', education=PHD)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(self.city.cash, 9480)
        self.assertEqual(RC.citizens_in_city[self.s].ci.cash, 100)
        self.assertEqual(RC.list_of_workplaces[self.school].workers_costs, 0)
        CitizenWorkEngine(RC, self.city).wage_payment_in_all_workplaces()
        self.assertEqual(round(RC.list_of_workplaces[self.school].workers_costs), 364)
        self.assertEqual(int(self.city.cash), 9116)
        self.assertEqual(int(RC.citizens_in_city[self.s].ci.cash), 463)

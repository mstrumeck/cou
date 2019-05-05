from django.contrib.auth.models import User
from django.test import TestCase

from citizen_engine.models import Citizen, Profession, Education
from city_engine.models import City, StandardLevelResidentialZone
from cou.abstract import RootClass
from cou.global_var import (
    FEMALE,
    ELEMENTARY,
    COLLEGE,
    TRAINEE,
    JUNIOR,
    REGULAR,
    MASTER,
    PROFESSIONAL,
)
from resources.models import Market


class ProfessionUpdateLevelTests(TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.user = User.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.s = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=COLLEGE,
            resident_object=self.r1,
        )

    def test_train_to_junior(self):
        Education.objects.create(
            citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False
        )
        Profession.objects.create(citizen=self.s, proficiency=0.0, name="Nauczyciel")
        RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0)
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.job_grade, TRAINEE
        )
        for x in range(6):
            RC.citizens_in_city[self.s].current_profession.update_proficiency(
                RC.citizens_in_city[self.s]
            )
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.proficiency,
            0.12000000000000001,
        )
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.job_grade, JUNIOR
        )

    def test_train_to_regular(self):
        Education.objects.create(
            citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False
        )
        Profession.objects.create(citizen=self.s, proficiency=0.0, name="Nauczyciel")
        RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0)
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.job_grade, TRAINEE
        )
        for x in range(24):
            RC.citizens_in_city[self.s].current_profession.update_proficiency(
                RC.citizens_in_city[self.s]
            )
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.proficiency,
            0.4515789473684213,
        )
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.job_grade, REGULAR
        )

    def test_train_to_professional(self):
        Education.objects.create(
            citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False
        )
        Profession.objects.create(citizen=self.s, proficiency=0.0, name="Nauczyciel")
        RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0)
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.job_grade, TRAINEE
        )
        for x in range(60):
            RC.citizens_in_city[self.s].current_profession.update_proficiency(
                RC.citizens_in_city[self.s]
            )
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.proficiency,
            0.6625438596491233,
        )
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.job_grade, PROFESSIONAL
        )

    def test_train_to_master(self):
        Education.objects.create(
            citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False
        )
        Profession.objects.create(citizen=self.s, proficiency=0.0, name="Nauczyciel")
        RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0)
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.job_grade, TRAINEE
        )
        for x in range(108):
            RC.citizens_in_city[self.s].current_profession.update_proficiency(
                RC.citizens_in_city[self.s]
            )
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.proficiency,
            1.0187938596491228,
        )
        self.assertEqual(
            RC.citizens_in_city[self.s].current_profession.job_grade, MASTER
        )

from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Profession, Education
from citizen_engine.work_engine import CitizenWorkEngine
from city_engine.models import (
    StandardLevelResidentialZone,
    City,
    WindPlant,
    Field,
    PrimarySchool,
    DustCart,
    DumpingGround,
    WaterTower,
)
from cou.abstract import RootClass
from cou.global_var import MALE, FEMALE, ELEMENTARY, COLLEGE
from resources.models import Market
from .base import SocialTestHelper


class TestFindWork(SocialTestHelper):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="1",
            surname="",
            sex=FEMALE,
            resident_object=self.r1,
            edu_title=ELEMENTARY,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="2",
            surname="",
            sex=MALE,
            resident_object=self.r1,
            edu_title=ELEMENTARY,
        )
        self.s = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="3",
            surname="",
            sex=MALE,
            resident_object=self.r1,
            edu_title=COLLEGE,
        )
        Education.objects.create(
            citizen=self.f, name=ELEMENTARY, effectiveness=0.5, if_current=False
        )
        Education.objects.create(
            citizen=self.m, name=ELEMENTARY, effectiveness=0.5, if_current=False
        )
        Education.objects.create(
            citizen=self.s, name=ELEMENTARY, effectiveness=0.5, if_current=False
        )
        Education.objects.create(
            citizen=self.s, name=COLLEGE, effectiveness=0.5, if_current=False
        )

    def test_for_find_better_job(self):
        RC = RootClass(self.city, User.objects.latest("id"))
        citizen = [x for x in RC.citizens_in_city].pop()
        self.assertEqual(citizen.workplace_object, None)
        CitizenWorkEngine(RC, self.city).human_resources_allocation()
        for c in RC.citizens_in_city:
            c.save()
        cwo = citizen.workplace_object
        elementary_vacancies_before = RC.list_of_workplaces[cwo].elementary_vacancies
        self.assertEqual(Profession.objects.all().count(), 3)
        self.assertEqual(Profession.objects.filter(if_current=True).count(), 3)
        self.assertNotEqual(citizen.workplace_object, None)
        school = PrimarySchool.objects.create(
            city=self.city,
            city_field=Field.objects.latest("id"),
            if_under_construction=False,
        )
        RC = RootClass(self.city, User.objects.latest("id"))
        CitizenWorkEngine(RC, self.city).human_resources_allocation()
        self.assertEqual(
            RC.list_of_workplaces[cwo].elementary_vacancies,
            elementary_vacancies_before + 1,
        )
        for c in RC.citizens_in_city:
            c.save()
            [p.save() for p in RC.citizens_in_city[c].professions]
        self.assertEqual(Profession.objects.all().count(), 4)
        self.assertEqual(Profession.objects.filter(if_current=True).count(), 3)
        self.assertEqual(Profession.objects.filter(if_current=False).count(), 1)
        citizen = [x for x in RC.citizens_in_city].pop()
        self.assertEqual(citizen.workplace_object, school)

    def test_work_engine_for_specific_degree(self):
        school = PrimarySchool.objects.create(
            city=self.city,
            city_field=Field.objects.latest("id"),
            if_under_construction=False,
        )
        self.assertEqual(school.employee.count(), 0)
        self.assertEqual(Profession.objects.all().count(), 0)
        self.assertEqual(self.s.workplace_object, None)
        self.assertEqual(self.f.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
        RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(RC.list_of_workplaces[school].all_employees), 0)
        self.assertEqual(
            RC.list_of_workplaces[school].college_vacancies,
            school.college_employee_needed,
        )
        CitizenWorkEngine(RC, self.city).human_resources_allocation()
        self.save_all_ob_from(RC.citizens_in_city)
        self.s = Citizen.objects.get(id=self.s.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.m = Citizen.objects.get(id=self.m.id)
        self.assertEqual(self.s.workplace_object, school)
        self.assertEqual(school.employee.count(), 1)
        self.assertEqual(school.employee.last(), self.s)
        self.assertEqual(Profession.objects.all().count(), 3)
        self.assertNotEqual(self.m.workplace_object, None)
        self.assertNotEqual(self.f.workplace_object, None)
        RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(RC.list_of_workplaces[school].all_employees), 1)
        self.assertEqual(
            RC.list_of_workplaces[school].college_vacancies,
            school.college_employee_needed - 1,
        )

    def test_failed_scenario(self):
        self.f.resident_object = None
        self.m.resident_object = None
        self.s.resident_object = None
        RC = RootClass(self.city, User.objects.latest("id"))
        self.save_all_ob_from(RC.citizens_in_city)
        self.assertEqual(self.f.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
        self.assertEqual(self.s.workplace_object, None)
        RC = RootClass(self.city, User.objects.latest("id"))
        CitizenWorkEngine(RC, self.city).human_resources_allocation()
        self.save_all_ob_from(RC.citizens_in_city)
        self.assertEqual(self.f.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
        self.assertEqual(self.s.workplace_object, None)

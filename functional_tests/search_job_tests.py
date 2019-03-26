from django.contrib.auth.models import User
from django.test import override_settings
from selenium import webdriver

from citizen_engine.models import Citizen, Education, Profession
from city_engine.models import (
    City,
    StandardLevelResidentialZone,
    Field,
    PrimarySchool,
)
from cou.abstract import RootClass
from cou.global_var import FEMALE, ELEMENTARY, COLLEGE, MALE
from functional_tests.page_objects import MainView, LoginPage, Homepage
from player.models import Profile
from resources.models import Market
from .legacy.base import BaseTestOfficial


@override_settings(DEBUG=True)
class SearchJobTest(BaseTestOfficial):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.city = City.objects.latest("id")
        self.user = User.objects.latest("id")
        self.profile = Profile.objects.latest("id")
        self.market = Market.objects.create(profile=self.profile)
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="WORKER",
            surname="HE",
            sex=MALE,
            resident_object=self.r1,
            edu_title=ELEMENTARY,
        )
        self.employee = Citizen.objects.create(
            city=self.city,
            age=34,
            month_of_birth=2,
            cash=100,
            health=5,
            name="TEACHER",
            surname="SHE",
            sex=FEMALE,
            resident_object=self.r1,
            edu_title=COLLEGE,
        )
        Education.objects.create(
            citizen=self.employee, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=self.employee, name=COLLEGE, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=self.m, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        self.profile.if_social_enabled = True
        self.profile.save()

    def test_choose_better_workplace(self):
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)

        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        self.employee = Citizen.objects.get(id=self.employee.id)
        self.m = Citizen.objects.get(id=self.m.id)
        self.assertEqual(self.employee.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
        self.assertEqual(Profession.objects.all().count(), 0)

        main_view.next_turns(3)

        self.assertEqual(Profession.objects.all().count(), 2)
        RC = RootClass(self.city, self.user)
        self.employee = Citizen.objects.get(id=self.employee.id)
        self.m = Citizen.objects.get(id=self.m.id)
        self.assertNotEqual(self.employee.workplace_object, None)
        self.assertNotEqual(
            RC.citizens_in_city[self.employee].current_profession.education,
            self.employee.edu_title,
        )
        self.assertEqual(
            RC.citizens_in_city[self.m].current_profession.education, self.m.edu_title
        )

        ps = PrimarySchool.objects.create(
            city=self.city,
            city_field=Field.objects.latest("id"),
            if_under_construction=False,
        )

        main_view.next_turns(2)

        self.assertEqual(Profession.objects.all().count(), 3)
        self.employee = Citizen.objects.get(id=self.employee.id)
        self.m = Citizen.objects.get(id=self.m.id)
        RC = RootClass(self.city, self.user)
        self.assertEqual(len(RC.citizens_in_city[self.employee].professions), 2)
        self.assertEqual(
            len(
                [
                    x
                    for x in RC.citizens_in_city[self.employee].professions
                    if x.if_current is True
                ]
            ),
            1,
        )
        self.assertEqual(len(RC.citizens_in_city[self.m].professions), 1)
        self.assertEqual(self.employee.workplace_object, ps)
        self.assertNotEqual(self.m.workplace_object, ps)

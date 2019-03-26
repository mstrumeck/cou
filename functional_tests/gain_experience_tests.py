import decimal

from django.contrib.auth.models import User
from django.test import override_settings
from selenium import webdriver

from citizen_engine.models import Citizen, Education
from city_engine.models import (
    City,
    StandardLevelResidentialZone,
    Field,
    PrimarySchool,
)
from cou.abstract import RootClass
from cou.global_var import FEMALE, ELEMENTARY, COLLEGE, MALE, TRAINEE, JUNIOR
from functional_tests.page_objects import MainView, LoginPage, Homepage
from player.models import Profile
from resources.models import Market
from .legacy.base import BaseTest


@override_settings(DEBUG=True)
class CitizenBasicTests(BaseTest):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.city = City.objects.latest("id")
        self.user = User.objects.latest("id")
        self.profile = Profile.objects.latest("id")
        self.market = Market.objects.create(profile=self.profile)
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.school = PrimarySchool.objects.create(
            city=self.city,
            city_field=Field.objects.latest("id"),
            if_under_construction=False,
        )
        self.teacher = Citizen.objects.create(
            city=self.city,
            age=34,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            resident_object=self.r1,
            edu_title=COLLEGE,
        )
        self.student_one = Citizen.objects.create(
            city=self.city,
            age=self.school.age_of_start,
            month_of_birth=2,
            health=5,
            name="0",
            surname="2",
            sex=MALE,
            resident_object=self.r1,
        )
        self.student_two = Citizen.objects.create(
            city=self.city,
            age=self.school.age_of_start,
            month_of_birth=2,
            health=5,
            name="0",
            surname="3",
            sex=MALE,
            resident_object=self.r1,
        )
        Education.objects.create(
            citizen=self.teacher, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=self.teacher, name=COLLEGE, effectiveness=1, if_current=False
        )
        self.profile.if_social_enabled = True
        self.profile.save()

    def test_school_assign(self):
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.current_turn = 7
        self.profile.save()

        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 3)
        self.assertEqual(self.student_one.school_object, None)
        self.assertEqual(self.student_two.school_object, None)
        self.assertEqual(self.teacher.workplace_object, None)
        self.assertEqual(Education.objects.all().count(), 2)

        RC = RootClass(self.city, self.user)
        self.assertEqual(RC.citizens_in_city[self.student_one].current_education, None)
        self.assertEqual(RC.citizens_in_city[self.student_two].current_education, None)
        self.assertEqual(RC.citizens_in_city[self.teacher].current_education, None)
        self.assertEqual(RC.citizens_in_city[self.teacher].current_profession, None)
        self.assertEqual(len(RC.citizens_in_city[self.student_one].educations), 0)
        self.assertEqual(len(RC.citizens_in_city[self.student_two].educations), 0)
        self.assertEqual(len(RC.citizens_in_city[self.teacher].educations), 2)
        self.assertEqual(RC.citizens_in_city[self.student_one].ci.cash, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].ci.cash, 0)
        self.assertEqual(
            RC.citizens_in_city[self.teacher].ci.cash, decimal.Decimal(100.00)
        )
        self.assertEqual(City.objects.latest("id").cash, decimal.Decimal(9480.00))

        main_view.next_turns(2)
        RC = RootClass(self.city, self.user)
        self.assertNotEqual(
            RC.citizens_in_city[self.student_one].current_education, None
        )
        self.assertNotEqual(
            RC.citizens_in_city[self.student_two].current_education, None
        )
        self.assertNotEqual(RC.citizens_in_city[self.teacher].current_profession, None)
        self.teacher = Citizen.objects.get(id=self.teacher.id)
        self.assertEqual(self.teacher.workplace_object, self.school)
        self.assertEqual(self.student_one.workplace_object, None)
        self.assertEqual(self.student_two.workplace_object, None)

        self.assertEqual(RC.citizens_in_city[self.teacher].salary_expectation, 164.83)
        self.assertEqual(RC.citizens_in_city[self.student_one].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].salary_expectation, 0)

        self.assertEqual(
            RC.citizens_in_city[self.student_one].current_education.effectiveness, 0
        )
        self.assertEqual(
            RC.citizens_in_city[self.student_two].current_education.effectiveness, 0
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.proficiency, 0.02
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.job_grade, TRAINEE
        )
        self.assertEqual(RC.citizens_in_city[self.student_one].ci.cash, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].ci.cash, 0)
        self.assertEqual(float(RC.citizens_in_city[self.teacher].ci.cash), 261.60)
        self.assertEqual(float(City.objects.latest("id").cash), 9318.40)

        self.profile.current_turn = 1
        self.profile.save()

        main_view.next_turns(1)
        RC = RootClass(self.city, self.user)
        self.assertEqual(
            RC.citizens_in_city[self.student_one].current_education.effectiveness,
            0.000416,
        )
        self.assertEqual(
            RC.citizens_in_city[self.student_two].current_education.effectiveness,
            0.000416,
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.proficiency, 0.04
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.job_grade, TRAINEE
        )
        self.assertEqual(RC.citizens_in_city[self.teacher].salary_expectation, 168.06)
        self.assertEqual(RC.citizens_in_city[self.student_one].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_one].ci.cash, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].ci.cash, 0)
        self.assertEqual(float(RC.citizens_in_city[self.teacher].ci.cash), 426.43)
        self.assertEqual(float(City.objects.latest("id").cash), 9153.57)

        main_view.next_turns(1)
        RC = RootClass(self.city, self.user)
        self.assertEqual(
            RC.citizens_in_city[self.student_one].current_education.effectiveness,
            0.00104,
        )
        self.assertEqual(
            RC.citizens_in_city[self.student_two].current_education.effectiveness,
            0.00104,
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.proficiency, 0.06
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.job_grade, TRAINEE
        )
        self.assertEqual(RC.citizens_in_city[self.teacher].salary_expectation, 171.3)
        self.assertEqual(RC.citizens_in_city[self.student_one].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_one].ci.cash, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].ci.cash, 0)
        self.assertEqual(float(RC.citizens_in_city[self.teacher].ci.cash), 594.49)
        self.assertEqual(float(City.objects.latest("id").cash), 8985.51)

        main_view.next_turns(1)
        RC = RootClass(self.city, self.user)
        self.assertEqual(
            RC.citizens_in_city[self.student_one].current_education.effectiveness,
            0.001872,
        )
        self.assertEqual(
            RC.citizens_in_city[self.student_two].current_education.effectiveness,
            0.001872,
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.proficiency, 0.08
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.job_grade, TRAINEE
        )
        self.assertEqual(RC.citizens_in_city[self.teacher].salary_expectation, 174.53)
        self.assertEqual(RC.citizens_in_city[self.student_one].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_one].ci.cash, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].ci.cash, 0)
        self.assertEqual(float(RC.citizens_in_city[self.teacher].ci.cash), 765.79)
        self.assertEqual(float(City.objects.latest("id").cash), 8814.21)

        main_view.next_turns(1)
        RC = RootClass(self.city, self.user)
        self.assertEqual(
            RC.citizens_in_city[self.student_one].current_education.effectiveness,
            0.002912,
        )
        self.assertEqual(
            RC.citizens_in_city[self.student_two].current_education.effectiveness,
            0.002912,
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.proficiency, 0.1
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.job_grade, TRAINEE
        )
        self.assertEqual(RC.citizens_in_city[self.teacher].salary_expectation, 177.76)
        self.assertEqual(RC.citizens_in_city[self.student_one].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_one].ci.cash, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].ci.cash, 0)
        self.assertEqual(float(RC.citizens_in_city[self.teacher].ci.cash), 940.32)
        self.assertEqual(float(City.objects.latest("id").cash), 8639.68)

        main_view.next_turns(1)
        RC = RootClass(self.city, self.user)
        self.assertEqual(
            RC.citizens_in_city[self.student_one].current_education.effectiveness,
            0.00416,
        )
        self.assertEqual(
            RC.citizens_in_city[self.student_two].current_education.effectiveness,
            0.00416,
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.proficiency, 0.12
        )
        self.assertEqual(
            RC.citizens_in_city[self.teacher].current_profession.job_grade, JUNIOR
        )
        self.assertEqual(RC.citizens_in_city[self.teacher].salary_expectation, 180.99)
        self.assertEqual(RC.citizens_in_city[self.student_one].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].salary_expectation, 0)
        self.assertEqual(RC.citizens_in_city[self.student_one].ci.cash, 0)
        self.assertEqual(RC.citizens_in_city[self.student_two].ci.cash, 0)
        self.assertEqual(float(RC.citizens_in_city[self.teacher].ci.cash), 1118.08)
        self.assertEqual(float(City.objects.latest("id").cash), 8461.92)

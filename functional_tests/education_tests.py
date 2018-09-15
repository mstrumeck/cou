from functional_tests.page_objects import MainView, LoginPage, Homepage
from city_engine.models import City, Residential, CityField, PrimarySchool
from .legacy.base import BaseTest
from django.contrib.auth.models import User
from selenium import webdriver
from player.models import Profile
from citizen_engine.models import Citizen, Education
from cou.global_var import FEMALE, ELEMENTARY
from django.test import override_settings
from cou.abstract import RootClass


@override_settings(DEBUG=True)
class CitizenBasicTests(BaseTest):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.city = City.objects.latest('id')
        self.user = User.objects.latest('id')
        self.browser.implicitly_wait(3)
        self.profile = Profile.objects.latest('id')
        self.r1 = Residential.objects.latest('id')
        self.f = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
            resident_object=self.r1,
        )
        self.school = PrimarySchool.objects.create(
            city=self.city,
            city_field=CityField.objects.latest('id')
        )
        self.profile.if_social_enabled = True
        self.profile.save()

    def test_school_assign(self):
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate('/main/')
        self.assertIn('Login', self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest('id').is_authenticated)
        self.assertIn('Miasto {}'.format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.current_turn = 6
        self.profile.save()
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 1)
        self.assertEqual(self.f.school_object, None)
        self.assertEqual(Education.objects.all().count(), 0)
        RC = RootClass(self.city,self.user)
        self.assertEqual(RC.citizens_in_city[self.f]['current_education'], None)
        main_view.next_turns(4)
        e = Education.objects.latest('id')
        RC = RootClass(self.city,self.user)
        self.assertEqual(RC.citizens_in_city[self.f]['current_education'], e)
        self.assertEqual(e.cur_year_of_learning, 0)
        self.assertEqual(e.max_year_of_learning, 8)
        self.assertEqual(Education.objects.all().count(), 1)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.f.school_object, self.school)

    def test_school_update_year(self):
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate('/main/')
        self.assertIn('Login', self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest('id').is_authenticated)
        self.assertIn('Miasto {}'.format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        e = Education.objects.create(cur_year_of_learning=0, max_year_of_learning=8, citizen=self.f, name=ELEMENTARY)
        self.f.school_object = self.school
        self.f.save()
        self.profile.current_turn = 6
        self.profile.save()
        RC = RootClass(self.city, self.user)
        self.assertEqual(RC.citizens_in_city[self.f]['current_education'], e)
        main_view.next_turns(4)
        self.assertEqual(Education.objects.all().count(), 1)
        self.f = Citizen.objects.get(id=self.f.id)
        e = Education.objects.get(id=e.id)
        RC = RootClass(self.city, self.user)
        self.assertEqual(RC.citizens_in_city[self.f]['current_education'], e)
        self.assertEqual(e.cur_year_of_learning, 1)
        self.assertEqual(e.max_year_of_learning, 8)

    def test_student_graduation(self):
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate('/main/')
        self.assertIn('Login', self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest('id').is_authenticated)
        self.assertIn('Miasto {}'.format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        e = Education.objects.create(cur_year_of_learning=7, max_year_of_learning=8, citizen=self.f, name=ELEMENTARY)
        self.f.school_object = self.school
        self.f.save()
        self.profile.current_turn = 6
        self.profile.save()
        RC = RootClass(self.city, self.user)
        self.assertEqual(RC.citizens_in_city[self.f]['current_education'], e)
        main_view.next_turns(4)
        self.assertEqual(Education.objects.all().count(), 1)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.f.school_object, None)
        self.assertEqual(self.f.edu_title, self.school.education_type_provided)
        e = Education.objects.get(id=e.id)
        self.assertEqual(e.if_current, False)
        self.profile.current_turn = 6
        self.profile.save()
        main_view.next_turns(4)
        e = Education.objects.get(id=e.id)
        self.assertEqual(e.if_current, False)
        self.assertEqual(self.f.school_object, None)
        self.assertEqual(self.f.edu_title, self.school.education_type_provided)
        self.assertEqual(Education.objects.all().count(), 1)
        self.assertEqual(self.school.student.all().count(), 0)

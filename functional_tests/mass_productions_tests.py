from django.contrib.auth.models import User

from citizen_engine.models import Education
from city_engine.models import CityField
from cou.abstract import RootClass
from functional_tests.page_objects import MainView, LoginPage, Homepage
from resources.models import Mass
from resources.models import MassConventer
from .legacy.base import BaseTestOfficial


class MassCollectorTest(BaseTestOfficial):
    fixtures = ["basic_basic_fixture.json"]

    def test_mass_collector(self):
        MassConventer.objects.create(
            city=self.city,
            city_field=CityField.objects.latest("id"),
            if_under_construction=False,
        )
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.assertEqual(MassConventer.objects.all().count(), 1)
        rc = RootClass(self.city, self.user)
        self.assertEqual(rc.market.resources.get(Mass), None)

        main_view.next_turns(3)
        for x in Education.objects.all():
            x.effectiveness = 0.1
            x.save()

        main_view.next_turns(3)
        for x in Education.objects.all():
            x.effectiveness = 0.9
            x.save()
        main_view.next_turns(3)

        mc = MassConventer.objects.latest("id")
        self.assertEqual(mc.employee.all().count(), mc.elementary_employee_needed)
        self.assertEqual(Mass.objects.count(), 3)
        rc = RootClass(self.city, self.user)
        self.assertEqual(len(rc.market.resources[Mass].instances), 3)
        self.assertEqual(rc.market.resources[Mass].total_size, 9)
        self.assertEqual(round(rc.market.resources[Mass].avg_quality), 17)
        self.assertEqual(round(rc.market.resources[Mass].avg_price), 164)

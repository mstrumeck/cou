from city_engine.main_view_data.board import HEX_NUM
from city_engine.models import City, CityField
from functional_tests.page_objects import Homepage, SignupPage, MainView
from .base import BaseTest


class SignupAndLoginTests(BaseTest):
    def test_signup_two_players(self):
        home_page = Homepage(self.browser, self.live_server_url)
        home_page.navigate("")
        self.assertIn("Strona główna", self.browser.title)
        home_page.click_registration_button()
        self.assertIn("Rejestracja", self.browser.title)
        signup_page = SignupPage(self.browser, self.live_server_url)
        signup_page.create_account(
            city_name=self.city_one_name,
            username=self.player_one,
            password=self.password_one,
        )
        self.assertIn("Miasto {}".format(self.city_one_name), self.browser.title)
        self.assertEqual(
            CityField.objects.filter(
                city=City.objects.get(name=self.city_one_name)
            ).count(),
            HEX_NUM,
        )

        main_view = MainView(self.browser, self.live_server_url)
        main_view.logout()
        self.assertIn("Strona główna", self.browser.title)
        home_page = Homepage(self.browser, self.live_server_url)
        home_page.click_registration_button()
        self.assertIn("Rejestracja", self.browser.title)
        signup_page.create_account(
            city_name=self.city_two_name,
            username=self.player_two,
            password=self.password_two,
        )
        self.assertIn("Miasto {}".format(self.city_two_name), self.browser.title)
        self.assertEqual(
            CityField.objects.filter(
                city=City.objects.get(name=self.city_two_name)
            ).count(),
            HEX_NUM,
        )

    def test_singup_form_validation(self):
        home_page = Homepage(self.browser, self.live_server_url)
        home_page.navigate("")
        self.assertIn("Strona główna", self.browser.title)
        home_page.click_registration_button()
        self.assertIn("Rejestracja", self.browser.title)
        signup_page = SignupPage(self.browser, self.live_server_url)
        signup_page.create_fake_account(
            city_name=self.city_one_name,
            username=self.player_one,
            password=self.password_one,
        )
        self.assertTrue(signup_page.if_error_displayed())

    def test_doubled_city_name(self):
        self.create_first_user()
        home_page = Homepage(self.browser, self.live_server_url)
        home_page.navigate("")
        self.assertIn("Strona główna", self.browser.title)
        home_page.click_registration_button()
        self.assertIn("Rejestracja", self.browser.title)
        signup_page = SignupPage(self.browser, self.live_server_url)
        signup_page.create_fake_account(
            city_name=self.city_one_name,
            username=self.player_one,
            password=self.password_one,
        )
        self.assertTrue(signup_page.if_error_displayed())

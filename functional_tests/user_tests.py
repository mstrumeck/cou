from city_engine.models import City, CityField
from django.contrib.auth.models import User
import time
from .base import BaseTest
from city_engine.board import HEX_NUM


class SignupAndLoginTest(BaseTest):

    def test_signup(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Rejestracja').click()
        self.assertIn('Rejestracja', self.browser.title)
        username_field = self.browser.find_element_by_id('id_username')
        password_field1 = self.browser.find_element_by_id('id_password1')
        password_field2 = self.browser.find_element_by_id('id_password2')
        username_field.send_keys('test_username')
        password_field1.send_keys('michal12345')
        password_field2.send_keys('michal12345')
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Tworzenie miasta', self.browser.title)
        city_name_field = self.browser.find_element_by_id('id_name')
        city_name_field.send_keys('Wrocław')
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format('Wrocław'), self.browser.title)
        self.assertEqual(CityField.objects.all().count(), HEX_NUM)

    def test_login_with_provided_account_info(self):
        username = 'test_username'
        password = 'michal12345'
        user = User.objects.create_user(username=username, password=password)
        City.objects.create(name='Wrocław', user=user)
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Zaloguj').click()
        time.sleep(1)
        username_field = self.browser.find_element_by_id('id_username')
        password_field = self.browser.find_element_by_id('id_password')
        username_field.send_keys(username)
        password_field.send_keys(password)
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format('Wrocław'), self.browser.title)



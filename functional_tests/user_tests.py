from city_engine.models import City, CityField
from django.contrib.auth.models import User
import time
from .base import BaseTest
from city_engine.board import HEX_NUM
import random
import string


class SignupAndLoginTest(BaseTest):

    def test_signup_two_players(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Rejestracja').click()
        self.assertIn('Rejestracja', self.browser.title)
        username_field = self.browser.find_element_by_id('id_username')
        password_field1 = self.browser.find_element_by_id('id_password1')
        password_field2 = self.browser.find_element_by_id('id_password2')
        city_name_field = self.browser.find_element_by_id('id_name')
        username_field.send_keys('test_username')
        password_field1.send_keys('michal12345')
        password_field2.send_keys('michal12345')
        city_name_field.send_keys('Wrocław')
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format('Wrocław'), self.browser.title)
        city1 = City.objects.get(name='Wrocław')
        self.assertEqual(CityField.objects.filter(city=city1).count(), HEX_NUM)

        self.browser.find_element_by_link_text('Wyloguj').click()
        self.browser.find_element_by_link_text('Rejestracja').click()
        self.assertIn('Rejestracja', self.browser.title)
        username_field = self.browser.find_element_by_id('id_username')
        password_field1 = self.browser.find_element_by_id('id_password1')
        password_field2 = self.browser.find_element_by_id('id_password2')
        city_name_field = self.browser.find_element_by_id('id_name')
        username_field.send_keys('test_username2')
        password_field1.send_keys('alicja12345')
        password_field2.send_keys('alicja12345')
        city_name_field.send_keys('Oleśnica')
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        city2 = City.objects.get(name='Oleśnica')
        self.assertEqual(CityField.objects.filter(city=city2).count(), HEX_NUM)

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

    def test_singup_form_validation(self):
        password1 = 'michal12345'
        password2 = ''

        for letter in range(len(password1)):
            password2 += random.choice(string.ascii_letters)

        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Rejestracja').click()
        time.sleep(1)
        username_field = self.browser.find_element_by_id('id_username')
        password_field1 = self.browser.find_element_by_id('id_password1')
        password_field2 = self.browser.find_element_by_id('id_password2')
        city_name_field = self.browser.find_element_by_id('id_name')
        username_field.send_keys('test_username')
        password_field1.send_keys(password1)
        password_field2.send_keys(password2)
        city_name_field.send_keys('Wrocław')
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        error = self.browser.find_element_by_class_name('errorlist')
        self.assertTrue(error.is_displayed())

    def test_doubled_city_name(self):
        password = 'michal12345'
        user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        City.objects.create(name='Wrocław', user=user, cash=100)
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Rejestracja').click()
        time.sleep(1)
        username_field = self.browser.find_element_by_id('id_username')
        password_field1 = self.browser.find_element_by_id('id_password1')
        password_field2 = self.browser.find_element_by_id('id_password2')
        city_name_field = self.browser.find_element_by_id('id_name')
        username_field.send_keys('test_username')
        password_field1.send_keys(password)
        password_field2.send_keys(password)
        city_name_field.send_keys('Wrocław')
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        error = self.browser.find_element_by_class_name('errorlist')
        self.assertTrue(error.is_displayed())





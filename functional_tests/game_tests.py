from .base import BaseTest
from city_engine.models import City
from django.contrib.auth.models import User
import time


class CreateBuildingsTest(BaseTest):

    def test_create_power_plant(self):
        response = self.client.get('/main_view/')
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
        self.assertIn('Miasto {}'.format(City.objects.get(name='Wrocław').name), self.browser.title)
        self.browser.find_element_by_id('buildPowerPlant').click()
        time.sleep(3)
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken')
        time.sleep(2)
        self.assertTrue(response, 'Elektrownia wiatrowa')
        self.assertTrue(response, 'Budowa')
        self.assertTrue(response, 'Czas')
        self.assertTrue(response, '0/3')
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(3)
        self.assertTrue(response, '1/3')
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(3)
        self.assertTrue(response, '2/3')
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(3)
        self.assertTrue(response, '3/3')
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(3)
        self.assertFalse(response, 'Budowa')
        self.assertFalse(response, 'Czas')


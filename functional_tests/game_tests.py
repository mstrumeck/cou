import time
from django.contrib.auth.models import User
from django.test import override_settings
from city_engine.main_view_data.board import assign_city_fields_to_board
from city_engine.models import City,\
    WindPlant, CoalPlant, RopePlant, \
    WaterTower
from .base import BaseTest


@override_settings(DEBUG=True)
class CreateBuildingsTest(BaseTest):

    def test_create_buildings(self):
        response = self.client.get('/main_view/')
        username = 'test_username'
        password = 'michal12345'
        user = User.objects.create_user(username=username, password=password)
        city = City.objects.create(name='Wrocław', user=user)
        assign_city_fields_to_board(city)

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
        self.browser.find_element_by_name('Budynki_elektryczne').click()
        self.browser.find_element_by_name('WindPlant').click()
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()

        self.browser.find_element_by_name('Budynki_elektryczne').click()
        time.sleep(1)
        self.browser.find_element_by_name('CoalPlant').click()
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()

        self.browser.find_element_by_name('Budynki_elektryczne').click()
        time.sleep(1)
        self.browser.find_element_by_name('RopePlant').click()
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()

        self.browser.find_element_by_name('Wodociagi').click()
        time.sleep(1)
        self.browser.find_element_by_name('WaterTower').click()
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()

        wind_plant = WindPlant.objects.get()
        rope_plant = RopePlant.objects.get()
        coal_plant = CoalPlant.objects.get()
        water_tower = WaterTower.objects.get()

        self.assertTrue(response, 'Elektrownia wiatrowa')
        self.assertTrue(response, 'Wieża Ciśnień')
        self.assertTrue(response, 'Elektrownia węglowa')
        self.assertTrue(response, 'Elektrownia na ropę')
        self.assertTrue(response, 'Budowa')
        self.assertTrue(response, 'Czas')
        self.assertTrue(response, '1/3')

        all_build_costs = wind_plant.build_cost + rope_plant.build_cost + coal_plant.build_cost + water_tower.build_cost
        all_maintenance_cost = wind_plant.maintenance_cost + rope_plant.maintenance_cost + coal_plant.maintenance_cost + water_tower.maintenance_cost
        self.assertTrue(response, '{}'.format(city.cash - (all_maintenance_cost + all_build_costs)))
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.assertTrue(response, '2/3')
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.assertTrue(response, '3/3')

    @override_settings(DEBUG=True)
    def test_create_power_plants_for_various_players(self):
        response = self.client.get('/main_view/')
        first_username = 'test_username'
        first_password = 'michal12345'

        second_username = 'test_username_2'
        second_password = '54321michal'

        first_user = User.objects.create_user(username=first_username, password=first_password)
        second_user = User.objects.create_user(username=second_username, password=second_password)

        first_city = City.objects.create(name='Wrocław', user=first_user)
        assign_city_fields_to_board(first_city)

        second_city = City.objects.create(name='Łódź', user=second_user)
        assign_city_fields_to_board(second_city)

        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Zaloguj').click()
        time.sleep(1)
        first_username_field = self.browser.find_element_by_id('id_username')
        first_password_field = self.browser.find_element_by_id('id_password')
        first_username_field.send_keys(first_username)
        first_password_field.send_keys(first_password)
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format(City.objects.get(name='Wrocław').name), self.browser.title)
        self.browser.find_element_by_name('Budynki_elektryczne').click()
        self.browser.find_element_by_name('WindPlant').click()
        time.sleep(3)
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
        time.sleep(2)
        self.assertTrue(response, 'Elektrownia wiatrowa')
        self.assertTrue(response, 'Budowa')
        self.assertTrue(response, 'Czas')
        self.assertTrue(response, '1/3')
        self.assertTrue(WindPlant.objects.filter(city=first_city).count(), 1)

        self.browser.find_element_by_link_text('Wyloguj').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Zaloguj').click()
        time.sleep(1)
        second_username_field = self.browser.find_element_by_id('id_username')
        second_password_field = self.browser.find_element_by_id('id_password')
        second_username_field.send_keys(second_username)
        second_password_field.send_keys(second_password)
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format(City.objects.get(name='Łódź').name), self.browser.title)
        self.browser.find_element_by_name('Budynki_elektryczne').click()
        self.browser.find_element_by_name('WindPlant').click()
        time.sleep(3)
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
        time.sleep(2)
        self.assertTrue(response, 'Elektrownia wiatrowa')
        self.assertTrue(response, 'Budowa')
        self.assertTrue(response, 'Czas')
        self.assertTrue(response, '1/3')
        self.assertTrue(WindPlant.objects.filter(city=second_city).count(), 1)


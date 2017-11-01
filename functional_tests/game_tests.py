import time
from django.test import override_settings
from city_engine.models import City,\
    WindPlant, CoalPlant, RopePlant, \
    WaterTower
from .base import BaseTestForOnePlayer, BaseTestForTwoPlayers
from city_engine.main_view_data.main import \
    calculate_energy_production_in_city, calculate_water_production_in_city, calculate_energy_usage_in_city


@override_settings(DEBUG=True)
class CreateBuildingsTestForOnePlayer(BaseTestForOnePlayer):

    # def test_create_buildings(self):
    #     self.browser.get(self.live_server_url)
    #     self.browser.find_element_by_link_text('Zaloguj').click()
    #     time.sleep(1)
    #     username_field = self.browser.find_element_by_id('id_username')
    #     password_field = self.browser.find_element_by_id('id_password')
    #     username_field.send_keys(self.username)
    #     password_field.send_keys(self.password)
    #     self.browser.find_element_by_tag_name('button').click()
    #     time.sleep(1)
    #     self.assertIn('Miasto {}'.format(City.objects.get(name='Wrocław').name), self.browser.title)
    #     self.browser.find_element_by_name('Budynki_elektryczne').click()
    #     self.browser.find_element_by_name('WindPlant').click()
    #     self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
    #
    #     self.browser.find_element_by_name('Budynki_elektryczne').click()
    #     time.sleep(1)
    #     self.browser.find_element_by_name('CoalPlant').click()
    #     self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
    #
    #     self.browser.find_element_by_name('Budynki_elektryczne').click()
    #     time.sleep(1)
    #     self.browser.find_element_by_name('RopePlant').click()
    #     self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
    #
    #     self.browser.find_element_by_name('Wodociagi').click()
    #     time.sleep(1)
    #     self.browser.find_element_by_name('WaterTower').click()
    #     self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
    #
    #     time.sleep(1)
    #     self.browser.find_element_by_name('detailEnergy').is_displayed()
    #     self.browser.find_element_by_name('detailWater').is_displayed()
    #
    #     self.browser.find_element_by_link_text('Kolejna tura').click()
    #     time.sleep(1)
    #     self.browser.find_element_by_link_text('Kolejna tura').click()
    #     time.sleep(1)
    #     self.browser.find_element_by_link_text('Kolejna tura').click()
    #     time.sleep(1)
    #     self.browser.find_element_by_link_text('Kolejna tura').click()
    #     time.sleep(1)
    #     self.browser.find_element_by_link_text('Kolejna tura').click()
    #     time.sleep(1)
    #
    #     City.energy_production = calculate_energy_production_in_city(self.city)
    #     City.energy_used = calculate_energy_usage_in_city(self.city)
    #     city_energy_bilans = City.energy_production - City.energy_used
    #
    #     self.assertEqual(city_energy_bilans, 2)
    #     # self.assertContains(self.client.get('/main_view/'), 'Energia: {}'.format(city_energy_bilans))
    #     # self.assertContains(self.client.get('/main_view/'), 'Woda: {}'.format(calculate_water_production(self.city)))
    #
    #     self.assertEqual(WindPlant.objects.filter(city=self.city).count(), 1)
    #     self.assertEqual(CoalPlant.objects.filter(city=self.city).count(), 1)
    #     self.assertEqual(RopePlant.objects.filter(city=self.city).count(), 1)
    #     self.assertEqual(WaterTower.objects.filter(city=self.city).count(), 1)

    def test_energy_allocation(self):

        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Zaloguj').click()
        time.sleep(1)
        username_field = self.browser.find_element_by_id('id_username')
        password_field = self.browser.find_element_by_id('id_password')
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format(City.objects.get(name='Wrocław').name), self.browser.title)

        self.browser.find_element_by_name('Wodociagi').click()
        self.browser.find_element_by_name('WaterTower').click()
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()

        self.browser.find_element_by_name('Budynki_elektryczne').click()
        self.browser.find_element_by_name('WindPlant').click()
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()

        self.browser.find_element_by_name('Wodociagi').click()
        self.browser.find_element_by_name('WaterTower').click()
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()

        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)

        self.assertEqual(WindPlant.objects.filter(city=self.city).count(), 1)
        self.assertEqual(WaterTower.objects.filter(city=self.city).count(), 2)

        self.browser.find_element_by_xpath('//div[@id="1" and @class="hexagon build"]').click()
        self.browser.find_element_by_xpath('//p[contains(., "Energia: 2/3")]').is_displayed()

        self.browser.find_element_by_xpath('//div[@id="3" and @class="hexagon build"]').click()
        self.browser.find_element_by_xpath('//p[contains(., "Energia: 3/3")]').is_displayed()


# class CreateBuildingForManyPlayers(BaseTestForTwoPlayers):
#
#     def test_create_power_plants_for_various_players(self):
#
#         self.browser.get(self.live_server_url)
#         self.browser.find_element_by_link_text('Zaloguj').click()
#         time.sleep(1)
#         first_username_field = self.browser.find_element_by_id('id_username')
#         first_password_field = self.browser.find_element_by_id('id_password')
#         first_username_field.send_keys(self.first_username)
#         first_password_field.send_keys(self.first_password)
#         self.browser.find_element_by_tag_name('button').click()
#         time.sleep(1)
#         self.assertIn('Miasto {}'.format(City.objects.get(name='Wrocław').name), self.browser.title)
#         self.browser.find_element_by_name('Budynki_elektryczne').click()
#         self.browser.find_element_by_name('WindPlant').click()
#         time.sleep(3)
#         self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
#         time.sleep(2)
#
#         self.browser.find_element_by_name('detailEnergy').is_displayed()
#
#         self.assertEqual(WindPlant.objects.filter(city=self.first_city).count(), 1)
#
#         self.browser.find_element_by_link_text('Wyloguj').click()
#         time.sleep(1)
#         self.browser.find_element_by_link_text('Zaloguj').click()
#         time.sleep(1)
#         second_username_field = self.browser.find_element_by_id('id_username')
#         second_password_field = self.browser.find_element_by_id('id_password')
#         second_username_field.send_keys(self.second_username)
#         second_password_field.send_keys(self.second_password)
#         self.browser.find_element_by_tag_name('button').click()
#         time.sleep(1)
#         self.assertIn('Miasto {}'.format(City.objects.get(name='Łódź').name), self.browser.title)
#         self.browser.find_element_by_name('Budynki_elektryczne').click()
#         self.browser.find_element_by_name('WindPlant').click()
#         time.sleep(3)
#         self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
#         time.sleep(2)
#
#         self.browser.find_element_by_name('detailEnergy').is_displayed()
#
#         self.assertEqual(WindPlant.objects.filter(city=self.second_city).count(), 1)
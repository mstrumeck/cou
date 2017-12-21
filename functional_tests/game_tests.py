import time
from django.db.models import Sum
from django.test import override_settings
from city_engine.models import City,CityField, \
    WindPlant, CoalPlant, RopePlant, \
    WaterTower
from .base import BaseTestForOnePlayer, BaseTestForTwoPlayers
from city_engine.main_view_data.main import \
    calculate_energy_production_in_city, calculate_water_production_in_city, calculate_energy_usage_in_city


@override_settings(DEBUG=True)
class CreateBuildingsTestForOnePlayer(BaseTestForOnePlayer):

    def test_create_buildings(self):
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

        time.sleep(1)
        self.browser.find_element_by_name('detailEnergy').is_displayed()
        self.browser.find_element_by_name('detailWater').is_displayed()

        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)

        City.energy_production = calculate_energy_production_in_city(self.city)
        City.energy_used = calculate_energy_usage_in_city(self.city)
        city_energy_bilans = City.energy_production - City.energy_used

        self.assertEqual(city_energy_bilans, -1)
        # self.assertContains(self.client.get('/main_view/'), 'Energia: {}'.format(city_energy_bilans))
        # self.assertContains(self.client.get('/main_view/'), 'Woda: {}'.format(calculate_water_production_in_city(self.city)))

        self.assertEqual(WindPlant.objects.filter(city=self.city).count(), 1)
        self.assertEqual(CoalPlant.objects.filter(city=self.city).count(), 1)
        self.assertEqual(RopePlant.objects.filter(city=self.city).count(), 1)
        self.assertEqual(WaterTower.objects.filter(city=self.city).count(), 1)

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
        self.browser.find_element_by_xpath('//div[@id="00" and @class="hexagon isHexTaken"]').click()

        self.browser.find_element_by_name('Budynki_elektryczne').click()
        self.browser.find_element_by_name('WindPlant').click()
        self.browser.find_element_by_xpath('//div[@id="01" and @class="hexagon isHexTaken"]').click()

        self.browser.find_element_by_name('Wodociagi').click()
        self.browser.find_element_by_name('WaterTower').click()
        self.browser.find_element_by_xpath('//div[@id="02" and @class="hexagon isHexTaken"]').click()

        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)

        self.assertEqual(WindPlant.objects.filter(city=self.city).count(), 1)
        self.assertEqual(WaterTower.objects.filter(city=self.city).count(), 2)

        self.assertEqual(WindPlant.objects.get(city=self.city).energy_allocated,
                         WaterTower.objects.filter(city=self.city).aggregate(Sum('energy'))['energy__sum'])

        self.browser.find_element_by_xpath('//div[@id="00" and @class="hexagon build"]').click()
        city_field_1 = CityField.objects.get(city=self.city, row=0, col=0)
        city_field_2 = CityField.objects.get(city=self.city, row=0, col=1)
        city_field_3 = CityField.objects.get(city=self.city, row=0, col=2)

        self.browser.find_element_by_xpath('//p[contains(., "Energia: {}/{}")]'.format(
            WaterTower.objects.get(city=self.city, city_field=city_field_1).energy,
            WaterTower.objects.get(city=self.city, city_field=city_field_1).energy_required
        )).is_displayed()

        self.browser.find_element_by_xpath('//p[contains(., "Woda: {}/{}")]'.format(
            WindPlant.objects.get(city=self.city, city_field=city_field_2).water,
            WindPlant.objects.get(city=self.city, city_field=city_field_2).water_required
        )).is_displayed()

        self.browser.find_element_by_xpath('//div[@id="02" and @class="hexagon build"]').click()
        self.browser.find_element_by_xpath('//p[contains(., "Energia: {}/{}")]'.format(
            WaterTower.objects.get(city=self.city, city_field=city_field_3).energy,
            WaterTower.objects.get(city=self.city, city_field=city_field_3).energy_required
        )).is_displayed()


class CreateBuildingForManyPlayers(BaseTestForTwoPlayers):

    def test_create_power_plants_for_various_players(self):

        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Zaloguj').click()
        time.sleep(1)
        first_username_field = self.browser.find_element_by_id('id_username')
        first_password_field = self.browser.find_element_by_id('id_password')
        first_username_field.send_keys(self.first_username)
        first_password_field.send_keys(self.first_password)
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format(City.objects.get(name='Wrocław').name), self.browser.title)
        self.browser.find_element_by_name('Budynki_elektryczne').click()
        self.browser.find_element_by_name('WindPlant').click()
        time.sleep(3)
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
        time.sleep(2)

        self.browser.find_element_by_name('detailEnergy').is_displayed()

        self.assertEqual(WindPlant.objects.filter(city=self.first_city).count(), 1)

        self.browser.find_element_by_link_text('Wyloguj').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Zaloguj').click()
        time.sleep(1)
        second_username_field = self.browser.find_element_by_id('id_username')
        second_password_field = self.browser.find_element_by_id('id_password')
        second_username_field.send_keys(self.second_username)
        second_password_field.send_keys(self.second_password)
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format(City.objects.get(name='Łódź').name), self.browser.title)
        self.browser.find_element_by_name('Budynki_elektryczne').click()
        self.browser.find_element_by_name('WindPlant').click()
        time.sleep(3)
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
        time.sleep(2)

        self.browser.find_element_by_name('detailEnergy').is_displayed()

        self.assertEqual(WindPlant.objects.filter(city=self.second_city).count(), 1)
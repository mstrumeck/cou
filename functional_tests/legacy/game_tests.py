import time
from django.db.models import Sum
from django.test import override_settings
from city_engine.models import City, CityField, \
    WindPlant, CoalPlant, RopePlant, \
    WaterTower
from .base import BaseTestForOnePlayer, BaseTestForTwoPlayers, BaseTest


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

        self.assertEqual(self.city_stats.energy_bilans, 0)

        self.assertEqual(WindPlant.objects.filter(city=self.city).count(), 1)
        self.assertEqual(CoalPlant.objects.filter(city=self.city).count(), 1)
        self.assertEqual(RopePlant.objects.filter(city=self.city).count(), 1)
        self.assertEqual(WaterTower.objects.filter(city=self.city).count(), 1)

        self.assertEqual([booleans['if_electricity'] for booleans in
                          WindPlant.objects.filter(city=self.city).values('if_electricity')], [True])
        self.assertEqual([booleans['if_electricity'] for booleans in
                          CoalPlant.objects.filter(city=self.city).values('if_electricity')], [True])
        self.assertEqual([booleans['if_electricity'] for booleans in
                          RopePlant.objects.filter(city=self.city).values('if_electricity')], [True])
        self.assertEqual([booleans['if_waterworks'] for booleans in
                          WaterTower.objects.filter(city=self.city).values('if_waterworks')], [True])

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


@override_settings(DEBUG=True)
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
        time.sleep(2)
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
        time.sleep(2)

        self.browser.find_element_by_name('detailEnergy').is_displayed()

        self.browser.find_element_by_name('Wodociagi').click()
        self.browser.find_element_by_name('WaterTower').click()
        time.sleep(2)
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
        time.sleep(2)

        self.browser.find_element_by_name('detailWater').is_displayed()

        self.assertEqual(WindPlant.objects.filter(city=self.first_city).count(), 1)
        self.assertEqual(WaterTower.objects.filter(city=self.first_city).count(), 1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)

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
        time.sleep(2)
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
        time.sleep(2)

        self.browser.find_element_by_name('Wodociagi').click()
        self.browser.find_element_by_name('WaterTower').click()
        time.sleep(2)
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()
        time.sleep(2)

        self.browser.find_element_by_name('detailWater').is_displayed()
        self.browser.find_element_by_name('detailEnergy').is_displayed()

        self.assertEqual(WindPlant.objects.filter(city=self.second_city).count(), 1)
        self.assertEqual(WaterTower.objects.filter(city=self.second_city).count(), 1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)
        self.browser.find_element_by_link_text('Kolejna tura').click()
        time.sleep(1)


@override_settings(DEBUG=True)
class CitizenTests(BaseTest):
    fixtures = ['basic_fixture_functional.json']

    def test_citizen_allocation(self):
        city = City.objects.get(id=1)
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Zaloguj').click()
        time.sleep(1)
        first_username_field = self.browser.find_element_by_id('id_username')
        first_password_field = self.browser.find_element_by_id('id_password')
        first_username_field.send_keys('Michał')
        first_password_field.send_keys('Zapomnij#123')
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format(city.name), self.browser.title)
        self.assertEqual(WindPlant.objects.filter(city=city).count(), 2)
        self.assertEqual(WaterTower.objects.filter(city=city).count(), 2)

        self.browser.find_element_by_name('BudynkiMieszkalne').click()
        self.browser.find_element_by_name('Residential').click()
        self.browser.find_element_by_css_selector('.hexagon.isHexTaken').click()

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

        self.assertIn(CityField.objects.filter(city=city).aggregate(Sum('pollution'))['pollution__sum'], range(6, 20))

        for wind_plant in WindPlant.objects.filter(city=city):
            assert wind_plant.current_employees <= wind_plant.max_employees

        for water_tower in WaterTower.objects.filter(city=city):
            assert water_tower.current_employees <= water_tower.max_employees

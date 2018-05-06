import time
from django.db.models import Sum
from django.test import override_settings
from city_engine.models import City, CityField, \
    WindPlant, CoalPlant, RopePlant, \
    WaterTower, DumpingGround
from .base import BaseTestForOnePlayer, BaseTestForTwoPlayers, BaseTest
from city_engine.models import list_of_buildings_in_city, Building, get_subclasses, DustCart
from functional_tests.page_objects import MainView, Homepage, LoginPage
from django.db.models import F
from django.contrib.auth.models import User


# @override_settings(DEBUG=True)
class GameTestForOnePlayer(BaseTest):

    def test_create_all_buildings(self):
        self.create_first_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        main_view.build_the_building_from_single_choice('WaterTower', '00')
        main_view.build_the_building_from_single_choice('Residential', '01')
        main_view.build_the_building_from_single_choice('DumpingGround', '02')
        main_view.build_the_building_from_single_choice('ProductionBuilding', '12')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '03')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'RopePlant', '10')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'CoalPlant', '11')

        for building_sublcass in get_subclasses(Building, 'city_engine'):
            self.assertEqual(building_sublcass.objects.filter(city=self.city_one).count(), 1)
        for building in list_of_buildings_in_city(abstract_class=Building, city=self.city_one, app_label='city_engine'):
            self.assertTrue(building.if_under_construction)
        main_view.next_turns(5)
        for building in list_of_buildings_in_city(abstract_class=Building, city=self.city_one, app_label='city_engine'):
            self.assertFalse(building.if_under_construction)

    def test_energy_allocation(self):
        self.create_first_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        cor_water_tower_one = '00'
        cor_water_tower_two = '02'
        cor_wind_plant_one = '01'
        main_view.build_the_building_from_single_choice('WaterTower', cor_water_tower_one)
        main_view.build_the_building_from_single_choice('WaterTower', cor_water_tower_two)
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', cor_wind_plant_one)
        main_view.build_the_building_from_single_choice('Residential', '11')

        main_view.next_turns(8)
        self.assertEqual(WaterTower.objects.filter(city=self.city_one).count(), 2)
        self.assertEqual(WindPlant.objects.filter(city=self.city_one).count(), 1)
        self.assertEqual(WindPlant.objects.get(city=self.city_one).energy_allocated,
                         WaterTower.objects.filter(city=self.city_one).aggregate(Sum('energy'))['energy__sum'])

        wind_plant = WindPlant.objects.get(city=self.city_one,
                                           city_field=CityField.objects.get(city=self.city_one, row=0, col=1))
        water_tower_one = WaterTower.objects.get(city=self.city_one,
                                                 city_field=CityField.objects.get(city=self.city_one, row=0, col=0))
        water_tower_two = WaterTower.objects.get(city=self.city_one,
                                                 city_field=CityField.objects.get(city=self.city_one, row=0, col=2))
        main_view.choose_hex(cor_water_tower_one)
        main_view.get_element_by_xpath('//p[contains(., "Energia: {}/{}")]'.format(
            water_tower_one.energy, water_tower_one.energy_required)).is_displayed()

        main_view.choose_hex(cor_water_tower_two)
        main_view.get_element_by_xpath('//p[contains(., "Energia: {}/{}")]'.format(
           water_tower_two.energy, water_tower_two.energy_required)).is_displayed()

        main_view.choose_hex(cor_wind_plant_one)
        main_view.get_element_by_xpath('//p[contains(., "Woda: {}/{}")]'.format(
            wind_plant.water, wind_plant.water_required)).is_displayed()


class GameTestForTwoPlayers(BaseTest):
    def test_create_building_for_two_accounts(self):
        self.create_first_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        main_view.build_the_building_from_single_choice('WaterTower', '00')
        main_view.build_the_building_from_single_choice('Residential', '01')
        main_view.build_the_building_from_single_choice('DumpingGround', '02')
        main_view.build_the_building_from_single_choice('ProductionBuilding', '12')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '03')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'RopePlant', '10')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'CoalPlant', '11')
        for building_sublcass in get_subclasses(Building, 'city_engine'):
            self.assertEqual(building_sublcass.objects.filter(city=self.city_one).count(), 1)
        for building in list_of_buildings_in_city(abstract_class=Building, city=self.city_one, app_label='city_engine'):
            self.assertTrue(building.if_under_construction)
        main_view.next_turns(5)
        for building in list_of_buildings_in_city(abstract_class=Building, city=self.city_one, app_label='city_engine'):
            self.assertFalse(building.if_under_construction)
        main_view.logout()

        self.create_second_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_two,
                                                                        username=self.player_two,
                                                                        password=self.password_two,
                                                                        city=self.city_two,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        main_view.build_the_building_from_single_choice('WaterTower', '00')
        main_view.build_the_building_from_single_choice('Residential', '01')
        main_view.build_the_building_from_single_choice('DumpingGround', '02')
        main_view.build_the_building_from_single_choice('ProductionBuilding', '12')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '03')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'RopePlant', '10')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'CoalPlant', '11')
        for building_sublcass in get_subclasses(Building, 'city_engine'):
            self.assertEqual(building_sublcass.objects.filter(city=self.city_two).count(), 1)
        for building in list_of_buildings_in_city(abstract_class=Building, city=self.city_two, app_label='city_engine'):
            self.assertTrue(building.if_under_construction)
        main_view.next_turns(5)
        for building in list_of_buildings_in_city(abstract_class=Building, city=self.city_two, app_label='city_engine'):
            self.assertFalse(building.if_under_construction)


# @override_settings(DEBUG=True)
class CitizenTests(BaseTest):

    def test_citizen_allocation(self):
        self.create_first_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        main_view.build_the_building_from_single_choice('WaterTower', '10')
        main_view.build_the_building_from_single_choice('WaterTower', '12')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '11')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '23')
        main_view.next_turns(3)
        self.assertEqual(WindPlant.objects.filter(city=self.city_one).count(), 2)
        self.assertEqual(WaterTower.objects.filter(city=self.city_one).count(), 2)
        main_view.build_the_building_from_single_choice('Residential', '00')
        main_view.next_turns(3)

        for wind_plant in WindPlant.objects.filter(city=self.city_one):
            assert wind_plant.employee.count() <= wind_plant.max_employees

        for water_tower in WaterTower.objects.filter(city=self.city_one):
            assert water_tower.employee.count() <= water_tower.max_employees
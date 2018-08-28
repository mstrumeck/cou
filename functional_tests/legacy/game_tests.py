from django.db.models import Sum
from city_engine.models import WindPlant, WaterTower, Residential
from .base import BaseTest, TestHelper
from functional_tests.page_objects import MainView, LoginPage
from cou.abstract import RootClass
from django.test import override_settings

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
        main_view.build_the_building_from_single_choice('SewageWorks', '00')
        main_view.build_the_building_from_single_choice('WaterTower', '01')
        main_view.build_the_building_from_single_choice('Residential', '02')
        main_view.build_the_building_from_single_choice('DumpingGround', '03')
        main_view.build_the_building_from_single_choice('ProductionBuilding', '10')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '11')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'RopePlant', '12')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'CoalPlant', '13')
        main_view.build_the_building_from_multiple_choice('Farmy', 'PotatoFarm', '20')
        main_view.build_the_building_from_multiple_choice('Farmy', 'LettuceFarm', '21')
        main_view.build_the_building_from_multiple_choice('Farmy', 'BeanFarm', '22')
        main_view.build_the_building_from_multiple_choice('Farmy', 'CattleFarm', '23')
        main_view.build_the_building_from_single_choice('MassConventer', '30')
        main_view.build_the_building_from_single_choice('TradeDistrict', '31')

        for building_sublcass in RootClass(self.city_one, self.user_one).get_subclasses_of_all_buildings():
            self.assertEqual(building_sublcass.objects.filter(city=self.city_one).count(), 1)
        for building in RootClass(self.city_one, self.user_one).list_of_buildings:
            self.assertTrue(building.if_under_construction)
        main_view.next_turns(5)
        for building in RootClass(self.city_one, self.user_one).list_of_buildings:
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
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '20')
        main_view.build_the_building_from_single_choice('SewageWorks', '13')
        main_view.build_the_building_from_single_choice('Residential', '11')

        main_view.next_turns(8)
        th = TestHelper(self.city_one, self.user_one)
        self.assertEqual(WaterTower.objects.filter(city=self.city_one).count(), 2)
        self.assertEqual(WindPlant.objects.filter(city=self.city_one).count(), 2)
        # self.assertEqual(WindPlant.objects.get(city=self.city_one).energy_allocated, sum([b.energy for b in th.list_of_buildings]))
        self.assertEqual(sum([x.energy_allocated for x in WindPlant.objects.all()]), sum([b.energy for b in th.list_of_buildings]))
        self.assertEqual(WaterTower.objects.filter(city=self.city_one).aggregate(Sum('energy'))['energy__sum'], 7)
        self.assertEqual(Residential.objects.latest('id').energy, 5)


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
        main_view.build_the_building_from_single_choice('SewageWorks', '00')
        main_view.build_the_building_from_single_choice('WaterTower', '01')
        main_view.build_the_building_from_single_choice('Residential', '02')
        main_view.build_the_building_from_single_choice('DumpingGround', '03')
        main_view.build_the_building_from_single_choice('ProductionBuilding', '10')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '11')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'RopePlant', '12')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'CoalPlant', '13')
        main_view.build_the_building_from_multiple_choice('Farmy', 'PotatoFarm', '20')
        main_view.build_the_building_from_multiple_choice('Farmy', 'LettuceFarm', '21')
        main_view.build_the_building_from_multiple_choice('Farmy', 'BeanFarm', '22')
        main_view.build_the_building_from_multiple_choice('Farmy', 'CattleFarm', '23')
        main_view.build_the_building_from_single_choice('MassConventer', '30')
        main_view.build_the_building_from_single_choice('TradeDistrict', '31')

        for building_sublcass in RootClass(self.city_one, self.user_one).get_subclasses_of_all_buildings():
            self.assertEqual(building_sublcass.objects.filter(city=self.city_one).count(), 1)
        for building in RootClass(self.city_one, self.user_one).list_of_buildings:
            self.assertTrue(building.if_under_construction)
        main_view.next_turns(5)
        for building in RootClass(self.city_one, self.user_one).list_of_buildings:
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
        main_view.build_the_building_from_single_choice('SewageWorks', '00')
        main_view.build_the_building_from_single_choice('WaterTower', '01')
        main_view.build_the_building_from_single_choice('Residential', '02')
        main_view.build_the_building_from_single_choice('DumpingGround', '03')
        main_view.build_the_building_from_single_choice('ProductionBuilding', '10')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '11')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'RopePlant', '12')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'CoalPlant', '13')
        main_view.build_the_building_from_multiple_choice('Farmy', 'PotatoFarm', '20')
        main_view.build_the_building_from_multiple_choice('Farmy', 'LettuceFarm', '21')
        main_view.build_the_building_from_multiple_choice('Farmy', 'BeanFarm', '22')
        main_view.build_the_building_from_multiple_choice('Farmy', 'CattleFarm', '23')
        main_view.build_the_building_from_single_choice('MassConventer', '30')
        main_view.build_the_building_from_single_choice('TradeDistrict', '31')

        for building_sublcass in RootClass(self.city_two, self.user_two).get_subclasses_of_all_buildings():
            self.assertEqual(building_sublcass.objects.filter(city=self.city_two).count(), 1)
        for building in RootClass(self.city_two, self.user_two).list_of_buildings:
            self.assertTrue(building.if_under_construction)
        main_view.next_turns(5)
        for building in RootClass(self.city_two, self.user_two).list_of_buildings:
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
from functional_tests.page_objects import MainView, LoginPage
from city_engine.models import CityField, \
    WindPlant, DumpingGround, DustCart, list_of_buildings_in_city
from .legacy.base import BaseTest
from django.db.models import Sum


class TrashCollectorTest(BaseTest):

    def test_trashcollector_build(self):
        self.create_first_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        main_view.build_the_building_from_single_choice('DumpingGround', '11')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '10')
        self.assertEquals(WindPlant.objects.filter(city=self.city_one).count(), 1)
        self.assertEquals(DumpingGround.objects.filter(city=self.city_one).count(), 1)

    def list_of_all_trashes_in_city(self):
        result = []
        for building in list_of_buildings_in_city(city=self.city_one):
            for trash in building.trash.all():
                result.append(trash)
        return result

    def test_garbage_management(self):
        self.create_first_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        corr_water_tower_one = '21'
        corr_water_tower_two = '23'
        corr_wind_plant_one = '22'
        corr_wind_plant_two = '32'
        corr_residential_one = '00'
        corr_residential_two = '02'
        corr_dumping_ground = '01'
        main_view.build_the_building_from_single_choice('WaterTower', corr_water_tower_one)
        main_view.build_the_building_from_single_choice('WaterTower', corr_water_tower_two)
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', corr_wind_plant_one)
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', corr_wind_plant_two)
        main_view.build_the_building_from_single_choice('Residential', corr_residential_one)
        main_view.build_the_building_from_single_choice('Residential', corr_residential_two)
        main_view.build_the_building_from_single_choice('DumpingGround', corr_dumping_ground)

        main_view.next_turns(2)
        dumping_ground = DumpingGround.objects.latest('id')
        dust_cart = DustCart.objects.latest('id')
        self.assertEqual(dumping_ground.current_space_for_trash, 0)
        self.assertEqual(dumping_ground.employee.count(), 0)
        self.assertEqual(dust_cart.employee.count(), 0)
        self.assertEqual(sum([trash['size'] for trash in self.list_of_all_trashes_in_city()]), 0)
        main_view.next_turns(7)
        dumping_ground = DumpingGround.objects.latest('id')
        dust_cart = DustCart.objects.latest('id')
        self.assertEqual(dumping_ground.employee.count(), 5)
        self.assertGreater(dumping_ground.current_space_for_trash, 100)
        self.assertEqual(dust_cart.employee.count(), 3)
        self.assertEqual(CityField.objects.filter(city=self.city_one).aggregate(Sum('pollution'))['pollution__sum'], 36)

    # def test_with_various_number_of_drivers(self):
    #     self.create_first_user()
    #     LoginPage(self.browser,
    #               self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
    #                                                                     username=self.player_one,
    #                                                                     password=self.password_one,
    #                                                                     city=self.city_one,
    #                                                                     assertIn=self.assertIn,
    #                                                                     assertTrue=self.assertTrue)
    #     main_view = MainView(self.browser, self.live_server_url)
        #Napisz test z rożną skutecznością kierowców
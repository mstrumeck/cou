from functional_tests.page_objects import MainView, LoginPage, ResourcePage
from city_engine.models import CityField, City, SewageWorks, WindPlant, WaterTower
from .legacy.base import BaseTest
from city_engine.abstract import ResourcesData
from django.db.models import Sum
import time


class ResourceAllocationTest(BaseTest):

    def test_resources_view_for_two_players(self):
        self.create_first_user()
        self.create_second_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        main_view.build_the_building_from_multiple_choice('Farmy', 'PotatoFarm', '20')
        main_view.build_the_building_from_multiple_choice('Farmy', 'LettuceFarm', '21')
        main_view.build_the_building_from_multiple_choice('Farmy', 'BeanFarm', '22')
        main_view.build_the_building_from_multiple_choice('Farmy', 'CattleFarm', '23')
        main_view.next_turns(8)
        main_view.get_resources_view()
        resource_view = ResourcePage(self.browser, self.live_server_url)
        self.assertEqual('{}/main/resources/'.format(self.live_server_url), str(self.browser.current_url))
        self.assertIn('Surowce', self.browser.title)
        rd = ResourcesData(self.city_one, self.user_one)

        self.assertEqual('Cattle', rd.resources[0].name)
        self.assertIn(28, list(rd.resources[0].size))
        self.assertEqual(28, rd.resources[0].total_size)

        self.assertEqual('Milk', rd.resources[1].name)
        self.assertIn(24, rd.resources[1].size)
        self.assertEqual(24, rd.resources[1].total_size)

        self.assertEqual('Bean', rd.resources[2].name)
        self.assertIn(60, rd.resources[2].size)
        self.assertEqual(60, rd.resources[2].total_size)

        self.assertEqual('Potato', rd.resources[3].name)
        self.assertIn(60, rd.resources[3].size)
        self.assertEqual(60, rd.resources[3].total_size)

        self.assertEqual('Lettuce', rd.resources[4].name)
        self.assertIn(60, rd.resources[4].size)
        self.assertEqual(60, rd.resources[4].total_size)

        resource_view.navigate_to_main_view()
        main_view.logout()

        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_two,
                                                                        username=self.player_two,
                                                                        password=self.password_two,
                                                                        city=self.city_two,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)

        main_view = MainView(self.browser, self.live_server_url)
        main_view.next_turns(8)
        main_view.get_resources_view()
        self.assertEqual('{}/main/resources/'.format(self.live_server_url), str(self.browser.current_url))
        self.assertIn('Surowce', self.browser.title)
        rd = ResourcesData(self.city_two, self.user_two)
        self.assertEqual(rd.resources, [])



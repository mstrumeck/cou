from functional_tests.page_objects import Homepage, MainView, LoginPage
from city_engine.main_view_data.board import Board
from city_engine.main_view_data.city_stats import CityStatsCenter
from city_engine.models import City, CityField, \
    WindPlant, CoalPlant, RopePlant, \
    WaterTower, TrashCollector
from unittest import mock
from .legacy.base import BaseTestForOnePlayer, BaseTest


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
        main_view.build_the_building_from_single_choice('TrashCollector', '11')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '10')
        self.assertEquals(WindPlant.objects.filter(city=self.city_one).count(), 1)
        self.assertEquals(TrashCollector.objects.filter(city=self.city_one).count(), 1)

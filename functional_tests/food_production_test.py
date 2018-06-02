from functional_tests.page_objects import MainView, LoginPage
from city_engine.models import CityField, City, SewageWorks, \
    WindPlant, WaterTower, PotatoFarm, BeanFarm, LettuceFarm, Potato, Bean, Lettuce
from .legacy.base import BaseTest


class FoodProductionTest(BaseTest):

    def test_harvest(self):
        self.create_first_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        main_view.build_the_building_from_multiple_choice('Farmy', 'PotatoFarm', '20')
        main_view.build_the_building_from_multiple_choice('Farmy', 'BeanFarm', '21')
        main_view.build_the_building_from_multiple_choice('Farmy', 'LettuceFarm', '22')
        main_view.next_turn()
        pf = PotatoFarm.objects.latest('id')
        bf = BeanFarm.objects.latest('id')
        lf = LettuceFarm.objects.latest('id')
        self.assertQuerysetEqual(pf.veg.all(), pf.veg.none())
        self.assertQuerysetEqual(bf.veg.all(), bf.veg.none())
        self.assertQuerysetEqual(lf.veg.all(), lf.veg.none())
        main_view.next_turns(6)
        self.assertIn(Potato.objects.latest('id'), pf.veg.all())
        self.assertIn(Bean.objects.latest('id'), bf.veg.all())
        self.assertIn(Lettuce.objects.latest('id'), lf.veg.all())

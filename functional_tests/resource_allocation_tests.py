from functional_tests.page_objects import MainView, LoginPage
from city_engine.models import CityField, City, SewageWorks, WindPlant, WaterTower
from .legacy.base import BaseTest
from django.db.models import Sum


class ResourceAllocationTest(BaseTest):

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
        main_view.build_the_building_from_single_choice('SewageWorks', '13')
        main_view.build_the_building_from_single_choice('WaterTower', '00')
        main_view.build_the_building_from_single_choice('Residential', '01')
        main_view.build_the_building_from_single_choice('DumpingGround', '02')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '03')
        main_view.build_the_building_from_multiple_choice('BudynkiElektryczne', 'WindPlant', '10')

        self.assertEqual(WindPlant.objects.filter(city=self.city_one).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], 0)
        self.assertEqual(WaterTower.objects.filter(city=self.city_one).aggregate(Sum('raw_water_allocated'))['raw_water_allocated__sum'], 0)
        self.assertEqual(SewageWorks.objects.filter(city=self.city_one).aggregate(Sum('clean_water_allocated'))['clean_water_allocated__sum'], 0)
        main_view.next_turns(5)
        self.assertNotEqual(WindPlant.objects.filter(city=self.city_one).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], 0)
        self.assertNotEqual(WaterTower.objects.filter(city=self.city_one).aggregate(Sum('raw_water_allocated'))['raw_water_allocated__sum'], 0)
        self.assertNotEqual(SewageWorks.objects.filter(city=self.city_one).aggregate(Sum('clean_water_allocated'))['clean_water_allocated__sum'], 0)

from functional_tests.page_objects import MainView, LoginPage
from city_engine.models import SewageWorks, WindPlant, WaterTower, StandardLevelResidentialZone, CityField, DumpingGround, City
from .legacy.base import BaseTest
from django.db.models import Sum


class ResourceAllocationTest(BaseTest):

    def test_resource_allocation(self):
        self.create_first_user()
        self.city = City.objects.latest('id')
        self.city.cash = 1000000
        self.city.save()
        cf_id = CityField.objects.latest('id').id
        SewageWorks.objects.create(city=self.city, city_field=CityField.objects.get(id=cf_id))
        WaterTower.objects.create(city=self.city, city_field=CityField.objects.get(id=cf_id-1))
        StandardLevelResidentialZone.objects.create(city=self.city, city_field=CityField.objects.get(id=cf_id-2), max_population=30)
        DumpingGround.objects.create(city=self.city, city_field=CityField.objects.get(id=cf_id-3))
        WindPlant.objects.create(city=self.city, city_field=CityField.objects.get(id=cf_id-4))
        WindPlant.objects.create(city=self.city, city_field=CityField.objects.get(id=cf_id-5))
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)

        self.assertEqual(WindPlant.objects.filter(city=self.city_one).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], 0)
        self.assertEqual(WaterTower.objects.filter(city=self.city_one).aggregate(Sum('raw_water_allocated'))['raw_water_allocated__sum'], 0)
        self.assertEqual(SewageWorks.objects.filter(city=self.city_one).aggregate(Sum('clean_water_allocated'))['clean_water_allocated__sum'], 0)
        main_view.next_turns(5)
        self.assertNotEqual(WindPlant.objects.filter(city=self.city_one).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], 0)
        self.assertNotEqual(WaterTower.objects.filter(city=self.city_one).aggregate(Sum('raw_water_allocated'))['raw_water_allocated__sum'], 0)
        self.assertNotEqual(SewageWorks.objects.filter(city=self.city_one).aggregate(Sum('clean_water_allocated'))['clean_water_allocated__sum'], 0)

from functional_tests.page_objects import MainView, LoginPage, ResourcePage
from .legacy.base import BaseTest
from cou.abstract import ResourcesData
from city_engine.models import SewageWorks, WindPlant, WaterTower, StandardLevelResidentialZone, \
    CityField, PotatoFarm, BeanFarm, LettuceFarm, CattleFarm


class ResourceAllocationTest(BaseTest):

    def test_resources_view_for_two_players(self):
        self.create_first_user()
        cf_id = CityField.objects.latest('id').id
        SewageWorks.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id))
        WaterTower.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-1))
        StandardLevelResidentialZone.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-2), max_population=30)
        StandardLevelResidentialZone.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-3), max_population=30)
        WaterTower.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-4))
        WindPlant.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-5))
        WindPlant.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-6))
        WindPlant.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-7))
        PotatoFarm.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-8))
        LettuceFarm.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-9))
        BeanFarm.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-10))
        CattleFarm.objects.create(city=self.city_one, city_field=CityField.objects.get(id=cf_id-11))

        self.create_second_user()
        LoginPage(self.browser,
                  self.live_server_url).navigate_to_main_throught_login(user=self.user_one,
                                                                        username=self.player_one,
                                                                        password=self.password_one,
                                                                        city=self.city_one,
                                                                        assertIn=self.assertIn,
                                                                        assertTrue=self.assertTrue)
        main_view = MainView(self.browser, self.live_server_url)
        main_view.next_turns(8)
        main_view.get_resources_view()
        resource_view = ResourcePage(self.browser, self.live_server_url)
        self.assertEqual('{}/main/resources/'.format(self.live_server_url), str(self.browser.current_url))
        self.assertIn('Surowce', self.browser.title)
        rd = ResourcesData(self.city_one, self.user_one)

        self.assertEqual('Bydło', rd.resources['Cattle'][0][0].name)
        self.assertEqual(10, rd.resources['Cattle'][0][0].size)
        self.assertEqual(10, rd.resources['Cattle'][1])

        self.assertEqual('Mleko', rd.resources['Milk'][0][0].name)
        self.assertGreater(rd.resources['Milk'][0][0].size, 359)
        self.assertGreater(rd.resources['Milk'][1], 359)

        self.assertEqual('Fasola', rd.resources['Bean'][0][0].name)
        self.assertIn(rd.resources['Bean'][0][0].size, [x for x in range(2, 16)])
        self.assertIn(rd.resources['Bean'][1], [x for x in range(2, 16)])

        self.assertEqual('Ziemniaki', rd.resources['Potato'][0][0].name)
        self.assertIn(rd.resources['Potato'][0][0].size, [x for x in range(2, 16)])
        self.assertIn(rd.resources['Potato'][1], [x for x in range(2, 16)])

        self.assertEqual('Sałata', rd.resources['Lettuce'][0][0].name)
        self.assertIn(rd.resources['Lettuce'][0][0].size, [x for x in range(2, 16)])
        self.assertIn(rd.resources['Lettuce'][1], [x for x in range(2, 16)])

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
        self.assertEqual(rd.resources, {})



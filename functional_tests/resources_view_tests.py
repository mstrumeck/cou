from django.contrib.auth.models import User

from city_engine.models import (
    SewageWorks,
    WindPlant,
    WaterTower,
    StandardLevelResidentialZone,
    CityField,
)
from city_engine.test.base import TestHelper
from cou.abstract import RootClass
from functional_tests.page_objects import MainView, LoginPage
from resources.models import Bean, Potato, Lettuce, Milk, Cattle
from resources.models import PotatoFarm, LettuceFarm, BeanFarm, CattleFarm
from .legacy.base import BaseTest


class ResourceAllocationTest(BaseTest):
    def test_resources_view_for_two_players(self):
        self.create_first_user()
        cf_id = CityField.objects.latest("id").id
        SewageWorks.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id)
        )
        WaterTower.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id - 1)
        )
        s1 = StandardLevelResidentialZone.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id - 2),
            max_population=30,
        )
        s2 = StandardLevelResidentialZone.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id - 3),
            max_population=30,
        )
        WaterTower.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id - 4)
        )
        WindPlant.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id - 5)
        )
        WindPlant.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id - 6)
        )
        WindPlant.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id - 7)
        )
        PotatoFarm.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id - 8)
        )
        LettuceFarm.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id - 9)
        )
        BeanFarm.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id - 10)
        )
        f = CattleFarm.objects.create(
            city=self.city_one, city_field=CityField.objects.get(id=cf_id - 11)
        )
        Cattle.objects.create(farm=f, size=30, price=20)

        s1.self__init(30)
        s2.self__init(30)
        s1.save()
        s2.save()

        self.create_second_user()
        TestHelper(self.city_one, User.objects.latest("id")).populate_city()
        LoginPage(self.browser, self.live_server_url).navigate_to_main_throught_login(
            user=self.user_one,
            username=self.player_one,
            password=self.password_one,
            city=self.city_one,
            assertIn=self.assertIn,
            assertTrue=self.assertTrue,
        )
        main_view = MainView(self.browser, self.live_server_url)

        main_view.next_turns(8)

        bean = Bean.objects.latest("id")
        potato = Potato.objects.latest("id")
        lettuce = Lettuce.objects.latest("id")
        rc = RootClass(self.city_one, self.user_one)
        resources = rc.market.resources

        self.assertEqual(Bean.objects.count(), 1)
        self.assertEqual(bean.size, 705)
        self.assertEqual(int(bean.price), 36)
        self.assertEqual(bean.quality, 33)
        self.assertEqual(len(resources[Bean].instances), 1)
        self.assertEqual(resources[Bean].total_size, 705)
        self.assertEqual(resources[Bean].avg_quality, 33)
        self.assertEqual(int(resources[Bean].avg_price), 36)

        self.assertEqual(Lettuce.objects.count(), 1)
        self.assertEqual(lettuce.size, 349)
        self.assertEqual(int(lettuce.price), 18)
        self.assertEqual(lettuce.quality, 33)
        self.assertEqual(len(resources[Lettuce].instances), 1)
        self.assertEqual(resources[Lettuce].total_size, 349)
        self.assertEqual(resources[Lettuce].avg_quality, 33)
        self.assertEqual(int(resources[Lettuce].avg_price), 18)

        self.assertEqual(Potato.objects.count(), 1)
        self.assertEqual(potato.size, 695)
        self.assertEqual(int(potato.price), 37)
        self.assertEqual(potato.quality, 33)
        self.assertEqual(len(resources[Potato].instances), 1)
        self.assertEqual(resources[Potato].total_size, 695)
        self.assertEqual(resources[Potato].avg_quality, 33)
        self.assertEqual(int(resources[Potato].avg_price), 37)

        self.assertEqual(Milk.objects.count(), 1)

        main_view.logout()

        LoginPage(self.browser, self.live_server_url).navigate_to_main_throught_login(
            user=self.user_two,
            username=self.player_two,
            password=self.password_two,
            city=self.city_two,
            assertIn=self.assertIn,
            assertTrue=self.assertTrue,
        )

        main_view = MainView(self.browser, self.live_server_url)
        main_view.next_turns(8)
        main_view.get_resources_view()
        self.assertEqual(
            "{}/main/resources/".format(self.live_server_url),
            str(self.browser.current_url),
        )
        self.assertIn("Surowce", self.browser.title)
        rc2 = RootClass(self.city_two, self.user_two)
        self.assertEqual(Bean.objects.filter(market=self.market_two).count(), 0)
        self.assertEqual(Potato.objects.filter(market=self.market_two).count(), 0)
        self.assertEqual(Lettuce.objects.filter(market=self.market_two).count(), 0)
        self.assertEqual(rc2.market.resources.get(Potato), None)
        self.assertEqual(rc2.market.resources.get(Bean), None)
        self.assertEqual(rc2.market.resources.get(Lettuce), None)

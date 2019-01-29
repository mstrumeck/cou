from django.contrib.auth.models import User
from django.db.models import Sum

from city_engine.models import (
    CityField,
    City,
    WindPlant,
    DumpingGround,
    DustCart,
    StandardLevelResidentialZone,
    SewageWorks,
    WaterTower,
)
from city_engine.test.base import TestHelper
from cou.abstract import RootClass
from functional_tests.page_objects import MainView, LoginPage
from .legacy.base import BaseTest


class TrashCollectorTest(BaseTest):
    def test_trashcollector_build(self):
        self.create_first_user()
        LoginPage(self.browser, self.live_server_url).navigate_to_main_throught_login(
            user=self.user_one,
            username=self.player_one,
            password=self.password_one,
            city=self.city_one,
            assertIn=self.assertIn,
            assertTrue=self.assertTrue,
        )
        main_view = MainView(self.browser, self.live_server_url)
        main_view.build_the_building_from_single_choice("DumpingGround", "11")
        main_view.build_the_building_from_single_choice("WindPlant", "10")
        self.assertEquals(WindPlant.objects.filter(city=self.city_one).count(), 1)
        self.assertEquals(DumpingGround.objects.filter(city=self.city_one).count(), 1)

    def list_of_all_trashes_in_city(self):
        result = []
        for building in RootClass(
            city=City.objects.latest("id"), user=User.objects.latest("id")
        ).list_of_buildings:
            for trash in building.trash.all():
                result.append(trash)
        return result

    def test_garbage_management(self):
        self.create_first_user()
        LoginPage(self.browser, self.live_server_url).navigate_to_main_throught_login(
            user=self.user_one,
            username=self.player_one,
            password=self.password_one,
            city=self.city_one,
            assertIn=self.assertIn,
            assertTrue=self.assertTrue,
        )
        main_view = MainView(self.browser, self.live_server_url)
        cf_id = CityField.objects.latest("id").id
        SewageWorks.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id),
            if_under_construction=False,
        )
        WaterTower.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id - 1),
            if_under_construction=False,
        )
        WaterTower.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id - 2),
            if_under_construction=False,
        )
        WindPlant.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id - 3),
            if_under_construction=False,
        )
        WindPlant.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id - 4),
            if_under_construction=False,
        )
        dg = DumpingGround.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id - 5),
            if_under_construction=False,
        )
        DustCart.objects.create(dumping_ground=dg)
        StandardLevelResidentialZone.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id - 6),
            max_population=30,
            if_under_construction=False,
        )
        StandardLevelResidentialZone.objects.create(
            city=self.city_one,
            city_field=CityField.objects.get(id=cf_id - 7),
            max_population=30,
            if_under_construction=False,
        )

        TestHelper(city=self.city_one, user=User.objects.latest("id")).populate_city()
        dumping_ground = DumpingGround.objects.latest("id")
        dust_cart = DustCart.objects.latest("id")
        self.assertEqual(dumping_ground.current_space_for_trash, 0)
        self.assertEqual(dumping_ground.employee.count(), 5)
        self.assertEqual(dust_cart.employee.count(), 3)
        # self.assertGreater(sum([trash.size for trash in self.list_of_all_trashes_in_city()]), 18)
        main_view.next_turns(7)
        dumping_ground = DumpingGround.objects.latest("id")
        dust_cart = DustCart.objects.latest("id")
        self.assertEqual(dumping_ground.employee.count(), 5)
        self.assertGreater(dumping_ground.current_space_for_trash, 100)
        self.assertEqual(dust_cart.employee.count(), 3)
        self.assertGreater(
            CityField.objects.filter(city=self.city_one).aggregate(Sum("pollution"))[
                "pollution__sum"
            ],
            36,
        )

from django import test
from city_engine.models import City
from city_engine.models import TradeDistrict
from city_engine.test.base import TestHelper
from django.contrib.auth.models import User
from city_engine.turn_data.main import TurnCalculation
from cou.abstract import RootClass
from player.models import Profile


class TestTradeDistrict(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def test_trade_district_create_goods(self):
        trade_district = TradeDistrict.objects.create(city_id=1,
                                                      city_field_id=1,
                                                      if_under_construction=False,
                                                      energy=20,
                                                      water=30)
        TestHelper(City.objects.latest('id'), User.objects.latest('id')).populate_city()
        city = City.objects.latest('id')
        self.assertEqual(trade_district.cash, 100)
        self.assertEqual(trade_district.resources_stored, 0)
        self.assertEqual(trade_district.goods_stored, 0)
        self.assertEqual(float(city.cash), 9480.0)
        self.assertEqual(city.mass, 1000)
        RC = RootClass(city, User.objects.latest('id'))
        trade_district.creating_goods(city, RC.list_of_buildings, RC.citizens_in_city)
        trade_district.product_goods(RC.list_of_buildings, RC.citizens_in_city)
        TurnCalculation(city=city, data=RC, profile=Profile.objects.latest('id')).save_all()
        city = City.objects.latest('id')
        self.assertEqual(trade_district.cash, 2)
        self.assertEqual(trade_district.resources_stored, 1)
        self.assertEqual(trade_district.goods_stored, 39)
        self.assertEqual(float(city.cash), 9578.0)
        self.assertEqual(city.mass, 960)

    def test_trade_dictrict_buy_resources_not_active(self):
        trade_district = TradeDistrict.objects.create(city_id=1,
                                                      city_field_id=1,
                                                      resources_stored=90,
                                                      if_under_construction=False,
                                                      energy=20,
                                                      water=30)
        city = City.objects.latest('id')
        TestHelper(city, User.objects.latest('id')).populate_city()
        self.assertEqual(trade_district.resources_stored, 90)
        RC = RootClass(city, User.objects.latest('id'))
        trade_district.buy_resources(city, RC.list_of_buildings, RC.citizens_in_city)
        self.assertEqual(trade_district.resources_stored, 90)

    def test_trade_district_buy_resources(self):
        trade_district = TradeDistrict.objects.create(city_id=1,
                                                      city_field_id=1,
                                                      if_under_construction=False,
                                                      energy=20,
                                                      water=30)
        city = City.objects.latest('id')
        TestHelper(city, User.objects.latest('id')).populate_city()
        self.assertEqual(trade_district.resources_stored, 0)
        RC = RootClass(city, User.objects.latest('id'))
        trade_district.buy_resources(city, RC.list_of_buildings, RC.citizens_in_city)
        self.assertEqual(trade_district.resources_stored, 40)

    def test_trade_district_product_goods(self):
        trade_district = TradeDistrict.objects.create(city_id=1,
                                                      city_field_id=1,
                                                      resources_stored=90,
                                                      if_under_construction=False,
                                                      energy=20,
                                                      water=30)
        city = City.objects.latest('id')
        TestHelper(city, User.objects.latest('id')).populate_city()
        self.assertEqual(trade_district.resources_stored, 90)
        self.assertEqual(trade_district.goods_stored, 0)
        RC = RootClass(city, User.objects.latest('id'))
        trade_district.product_goods(RC.list_of_buildings, RC.citizens_in_city)
        self.assertEqual(trade_district.resources_stored, 1)
        self.assertEqual(trade_district.goods_stored, 89)

    def test_trade_district_product_goods_not_active(self):
        trade_district = TradeDistrict.objects.create(city_id=1,
                                                      city_field_id=1,
                                                      resources_stored=90,
                                                      goods_stored=60,
                                                      if_under_construction=False,
                                                      energy=20,
                                                      water=30)
        city = City.objects.latest('id')
        TestHelper(city, User.objects.latest('id')).populate_city()
        self.assertEqual(trade_district.resources_stored, 90)
        self.assertEqual(trade_district.goods_stored, 60)
        RC = RootClass(city, User.objects.latest('id'))
        trade_district.product_goods(RC.list_of_buildings, RC.citizens_in_city)
        self.assertEqual(trade_district.resources_stored, 90)
        self.assertEqual(trade_district.goods_stored, 60)

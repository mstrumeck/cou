from django.contrib.auth.models import User
from django.test import TestCase

from citizen_engine.models import Citizen
from city_engine.models import TradeDistrict, City, Field
from city_engine.test.base import TestHelper
from cou.abstract import RootClass
from cou.data_containers.data_containers import BuildingDataContainer
from player.models import Profile
from resources.models import Market, Mass
from .models import FoodCompany, Food
from cou.data_containers.buildings_semafor import BuildingSemafor


class CompanyTest(TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.user = User.objects.latest("id")
        self.city = City.objects.latest("id")
        self.market = Market.objects.create(profile=self.user.profile)
        self.td = TradeDistrict.objects.create(
            city=self.city, city_field=Field.objects.latest("id")
        )
        self.fc = FoodCompany.objects.create(cash=10, trade_district=self.td)
        TestHelper(city=self.city, user=self.user).populate_city()

    def test_energy_productivity(self):
        rc = RootClass(city=self.city, user=self.user)
        company_in_container = rc.list_of_workplaces[self.fc]
        company_in_container.energy = 8
        self.assertEqual(self.fc._get_energy_productivity(rc), 0.4)

    def test_water_productivity(self):
        rc = RootClass(city=self.city, user=self.user)
        company_in_container = rc.list_of_workplaces[self.fc]
        company_in_container.water = 8
        self.assertEqual(self.fc._get_water_productivity(rc), 0.8)

    def test_calculate_operation_requirements(self):
        rc = RootClass(city=self.city, user=self.user)
        company_in_container = rc.list_of_workplaces[self.fc]
        self.assertEqual(company_in_container.water_required, 10)
        self.assertEqual(company_in_container.energy_required, 20)

    def test_buy_mass_with_rest(self):
        mass_on_market = Mass.objects.create(
            size=20, quality=20, market=self.market, price=1.5
        )
        materials = []
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(mass_on_market.size, 20)
        self.assertEqual(mass_on_market.quality, 20)
        self.assertEqual(materials, [])
        self.assertEqual(self.fc.cash, 10)
        self.assertEqual(Mass.objects.all().count(), 1)
        self.fc.buy_components(materials, rc)
        rc.market.save_all()
        rc.list_of_workplaces[self.fc].save_all()
        self.assertEqual(Mass.objects.all().count(), 2)
        self.assertEqual(self.fc.cash, 1)
        mass_on_market = Mass.objects.get(id=mass_on_market.id)
        self.assertEqual(mass_on_market.size, 14)
        self.assertEqual(mass_on_market.quality, 20)
        self.assertNotEqual(materials, [])
        for mass in materials:
            self.assertNotEqual(mass_on_market, mass)
            self.assertEqual(mass.size, 6)
            self.assertEqual(mass.quality, 20)

    def test_buy_mass_none_left(self):
        mass_on_market = Mass.objects.create(
            size=5, quality=20, market=self.market, price=1.5
        )
        materials = []
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(mass_on_market.size, 5)
        self.assertEqual(mass_on_market.quality, 20)
        self.assertEqual(materials, [])
        self.assertEqual(self.fc.cash, 10)
        self.assertEqual(Mass.objects.all().count(), 1)
        self.fc.buy_components(materials, rc)
        rc.market.save_all()
        rc.list_of_workplaces[self.fc].save_all()
        self.assertEqual(Mass.objects.all().count(), 1)
        self.assertEqual(self.fc.cash, 2.5)
        self.assertEqual(list(Mass.objects.filter(id=mass_on_market.id)), [])
        self.assertNotEqual(materials, [])
        for mass in materials:
            self.assertNotEqual(mass_on_market, mass)
            self.assertEqual(mass.size, 5)
            self.assertEqual(mass.quality, 20)

    def test_buy_with_not_many_money(self):
        mass_on_market = Mass.objects.create(
            size=10, quality=20, market=self.market, price=1.5
        )
        self.fc.cash = 5
        self.fc.save()
        materials = []
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(mass_on_market.size, 10)
        self.assertEqual(mass_on_market.quality, 20)
        self.assertEqual(materials, [])
        self.assertEqual(self.fc.cash, 5)
        self.assertEqual(Mass.objects.all().count(), 1)
        self.fc.buy_components(materials, rc)
        rc.market.save_all()
        rc.list_of_workplaces[self.fc].save_all()
        self.assertEqual(Mass.objects.all().count(), 2)
        self.assertEqual(self.fc.cash, 0.50)
        mass_on_market = Mass.objects.get(id=mass_on_market.id)
        self.assertEqual(mass_on_market.size, 7)
        self.assertEqual(mass_on_market.quality, 20)
        self.assertNotEqual(materials, [])
        self.assertNotEqual(mass_on_market, materials[-1])
        self.assertEqual(materials[-1].size, 3)
        self.assertEqual(materials[-1].quality, 20)

    def set_resources_for_company(self, company, rc):
        company_in_container = rc.list_of_workplaces[company]
        company_in_container.water = 8
        company_in_container.energy = 10

    def test_goods_from_components(self):
        mass_on_market = Mass.objects.create(
            size=20, quality=20, market=self.market, price=1.5
        )
        materials = [mass_on_market]
        rc = RootClass(city=self.city, user=self.user)
        self.set_resources_for_company(self.fc, rc)
        self.assertEqual(mass_on_market.size, 20)
        self.assertEqual(mass_on_market.quality, 20)
        self.assertNotEqual(materials, [])
        self.assertEqual(self.fc.cash, 10)
        self.assertEqual(Mass.objects.all().count(), 1)
        self.fc.make_goods_from_components(materials, rc)
        rc.market.save_all()
        rc.list_of_workplaces[self.fc].save_all()
        self.assertEqual(Food.objects.all().count(), 1)
        food = Food.objects.latest("id")
        self.assertEqual(food.size, 20)
        self.assertEqual(food.quality, 7)
        self.assertEqual(food.company, self.fc)

    def test_create_goods_half_production(self):
        mass = Mass.objects.create(size=20, quality=20, market=self.market, price=1.5)
        rc = RootClass(city=self.city, user=self.user)
        self.set_resources_for_company(self.fc, rc)
        self.assertEqual(mass.size, 20)
        self.assertEqual(mass.quality, 20)
        self.assertEqual(self.fc.cash, 10)
        self.assertEqual(Mass.objects.all().count(), 1)
        self.fc.create_goods(rc)
        rc.market.save_all()
        rc.list_of_workplaces[self.fc].save_all()
        self.assertEqual(Mass.objects.all().count(), 1)
        mass = Mass.objects.get(id=mass.id)
        self.assertEqual(rc.market.resources[Mass].instances[-1].size, 14)
        self.assertEqual(mass.size, 14)
        self.assertEqual(mass.quality, 20)
        self.assertEqual(mass.market, self.market)
        self.assertEqual(Food.objects.all().count(), 1)
        food = Food.objects.latest("id")
        self.assertEqual(food.size, 6)
        self.assertEqual(food.quality, 7)
        self.assertEqual(food.company, self.fc)

    def test_create_goods_all_production(self):
        mass = Mass.objects.create(size=20, quality=20, market=self.market, price=1.5)
        self.fc.cash = 50
        self.fc.save()
        rc = RootClass(city=self.city, user=self.user)
        self.set_resources_for_company(self.fc, rc)
        self.assertEqual(mass.size, 20)
        self.assertEqual(mass.quality, 20)
        self.assertEqual(self.fc.cash, 50)
        self.assertEqual(len(rc.market.resources[Mass].instances), 1)
        self.fc.create_goods(rc)
        rc.market.save_all()
        rc.list_of_workplaces[self.fc].save_all()
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(rc.market.resources.get(Mass), None)
        self.assertEqual(Food.objects.all().count(), 1)
        food = Food.objects.latest("id")
        self.assertEqual(food.size, 20)
        self.assertEqual(food.quality, 7)
        self.assertEqual(food.company, self.fc)

    def test_create_data_for_trade_district(self):
        rc = RootClass(city=self.city, user=self.user)
        b = BuildingDataContainer(
            instance=self.td,
            citizens=Citizen.objects.filter(city=self.city),
            profile=self.user.profile,
            citizens_data=rc.citizens_in_city,
            vehicles=rc.vehicles,
            semafor=BuildingSemafor()
        )
        self.assertEqual(b.people_in_charge, 5)

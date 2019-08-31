from django import test
from django.contrib.auth.models import User

from city_engine.models import City, Field
from city_engine.test.base import TestHelper
from city_engine.turn_data.calculation import TurnCalculation
from cou.turn_data import RootClass
from resources.models import (
    Potato,
    Bean,
    Lettuce,
    Cattle,
    Milk,
    CattleFarm,
    Market,
    PotatoFarm,
    LettuceFarm,
    BeanFarm,
)


class FarmInstancesTests(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.user = User.objects.latest("id")
        self.city = City.objects.latest("id")
        self.market = Market.objects.create(profile=self.user.profile)
        self.cf = CattleFarm.objects.create(
            city=self.city, city_field=Field.objects.latest("id")
        )
        TestHelper(city=self.city, user=self.user).populate_city()

    def test_potato_creation(self):
        pf = PotatoFarm.objects.create(
            city=self.city, city_field=Field.objects.latest("id")
        )
        pf.max_harvest = 1000
        pf.save()
        TestHelper(city=self.city, user=self.user).populate_city()
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(rc.market.resources.get(Potato), None)
        self.assertEqual(Potato.objects.count(), 0)
        for turn in range(pf.time_to_grow_from, pf.time_to_grow_to + 1):
            rc.list_of_workplaces[pf].wage_payment(self.city)
            pf.update_harvest(turn, rc)
        self.assertEqual(Potato.objects.count(), 1)
        self.assertEqual(len(rc.market.resources[Potato].instances), 1)
        self.assertEqual(rc.market.resources[Potato].instances[-1].size, 1333)
        self.assertEqual(rc.market.resources[Potato].instances[-1].quality, 33)
        self.assertEqual(int(rc.market.resources[Potato].instances[-1].price), 19)
        self.assertEqual(pf.accumulate_harvest, 0)
        self.assertEqual(pf.accumulate_harvest_costs, 0)

    def test_bean_update_harvest(self):
        bf = BeanFarm.objects.create(
            city=self.city, city_field=Field.objects.latest("id")
        )
        bf.max_harvest = 1000
        bf.save()
        TestHelper(city=self.city, user=self.user).populate_city()
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(rc.market.resources.get(Bean), None)
        self.assertEqual(Bean.objects.count(), 0)
        for turn in range(bf.time_to_grow_from, bf.time_to_grow_to + 1):
            rc.list_of_workplaces[bf].wage_payment(self.city)
            bf.update_harvest(turn, rc)
        self.assertEqual(Bean.objects.count(), 1)
        self.assertEqual(len(rc.market.resources[Bean].instances), 1)
        self.assertEqual(rc.market.resources[Bean].instances[-1].size, 1333)
        self.assertEqual(rc.market.resources[Bean].instances[-1].quality, 33)
        self.assertEqual(float(rc.market.resources[Bean].instances[-1].price), 19.39)
        self.assertEqual(bf.accumulate_harvest, 0)
        self.assertEqual(bf.accumulate_harvest_costs, 0)

    def test_lettuce_update_harvest(self):
        lf = LettuceFarm.objects.create(
            city=self.city, city_field=Field.objects.latest("id")
        )
        lf.max_harvest = 1000
        lf.save()
        TestHelper(city=self.city, user=self.user).populate_city()
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(rc.market.resources.get(Lettuce), None)
        self.assertEqual(Lettuce.objects.count(), 0)
        for turn in range(lf.time_to_grow_from, lf.time_to_grow_to + 1):
            rc.list_of_workplaces[lf].wage_payment(self.city)
            lf.update_harvest(turn, rc)
        self.assertEqual(Lettuce.objects.count(), 1)
        self.assertEqual(len(rc.market.resources[Lettuce].instances), 1)
        self.assertEqual(rc.market.resources[Lettuce].instances[-1].size, 666)
        self.assertEqual(rc.market.resources[Lettuce].instances[-1].quality, 33)
        self.assertEqual(float(rc.market.resources[Lettuce].instances[-1].price), 9.70)
        self.assertEqual(lf.accumulate_harvest, 0)
        self.assertEqual(lf.accumulate_harvest_costs, 0)

    def test_breed_update(self):
        data = RootClass(city=self.city, user=self.user)
        tc = TurnCalculation(
            city=self.city, data=data, profile=self.user.profile
        )

        self.assertEqual(Cattle.objects.all().count(), 0)
        self.assertEqual(Milk.objects.all().count(), 0)
        self.cf.buy_cattle(20, data)
        self.assertEqual(Milk.objects.count(), 0)
        self.assertEqual(Cattle.objects.count(), 1)
        data.list_of_workplaces[self.cf].wage_payment(self.city)

        tc.update_breeding_status()
        tc.save_all()
        self.assertEqual(len(data.market.resources[Milk].instances), 1)
        self.assertEqual(Milk.objects.count(), 1)
        self.assertEqual(Milk.objects.latest("id").size, 33)
        self.assertEqual(data.market.resources[Milk].instances[-1].size, 33)
        self.assertEqual(data.market.resources[Milk].instances[-1].quality, 81)
        self.assertEqual(Milk.objects.latest("id").quality, 81)
        self.assertEqual(Cattle.objects.count(), 1)

        tc.update_breeding_status()
        tc.save_all()
        self.assertEqual(Cattle.objects.count(), 1)
        self.assertEqual(Milk.objects.latest("id").size, 66)
        self.assertEqual(Milk.objects.latest("id").quality, 81)
        self.assertEqual(Milk.objects.count(), 1)
        self.assertEqual(len(data.market.resources[Milk].instances), 1)
        self.assertEqual(data.market.resources[Milk].instances[-1].size, 66)
        self.assertEqual(data.market.resources[Milk].instances[-1].quality, 81)

        tc.update_breeding_status()
        tc.save_all()
        self.assertEqual(Cattle.objects.count(), 1)
        self.assertEqual(Milk.objects.latest("id").size, 99)
        self.assertEqual(Milk.objects.latest("id").quality, 81)
        self.assertEqual(Milk.objects.count(), 1)
        self.assertEqual(len(data.market.resources[Milk].instances), 1)
        self.assertEqual(data.market.resources[Milk].instances[-1].size, 99)
        self.assertEqual(data.market.resources[Milk].instances[-1].quality, 81)

    def test_farm_operation(self):
        Cattle.objects.create(farm=self.cf, size=20)
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(Milk.objects.all().count(), 0)
        rc.list_of_workplaces[self.cf].wage_payment(self.city)
        self.cf.farm_operation(rc)
        self.assertEqual(len(rc.market.resources[Milk].instances), 1)
        self.assertEqual(Milk.objects.all().count(), 1)
        self.assertEqual(self.cf.accumulate_breding, 0.004666666666666666)

    def test_release_accumulate_breeding(self):
        c = Cattle.objects.create(farm=self.cf, size=20)
        self.cf.accumulate_breding = 1.1
        self.cf._release_accumulate_breeding(c, self.cf.accumulate_breding)
        c.save()
        self.assertEqual(c.size, 21)
        self.assertEqual(Cattle.objects.latest("id").size, 21)
        self.assertEqual(self.cf.accumulate_breding, 0.10000000000000009)

    def test_accumulate_breeding(self):
        rc = RootClass(city=self.city, user=self.user)
        c = Cattle.objects.create(farm=self.cf, size=20)
        self.assertEqual(self.cf.accumulate_breding, 0)
        rc.list_of_workplaces[self.cf].wage_payment(self.city)
        self.cf._accumulate_breeding(rc, c)
        self.assertEqual(self.cf.accumulate_breding, 0.004666666666666666)
        self.assertEqual(Milk.objects.all().count(), 1)

    def test_cattle_farm_productivity(self):
        c = Cattle.objects.create(farm=self.cf, size=20)
        self.assertEqual(self.cf._cattle_farm_productivity(c), 0.8141810630738088)

    def test_buy_cattle_with_existing_one(self):
        Cattle.objects.create(farm=self.cf, size=20)
        rc = RootClass(city=self.city, user=self.user)
        self.assertNotEqual(rc.list_of_workplaces[self.cf].cattle, [])
        self.assertEqual(rc.list_of_workplaces[self.cf].cattle.size, 20)
        self.assertEqual(Cattle.objects.all().count(), 1)
        self.assertEqual(Cattle.objects.latest("id").size, 20)
        self.cf.buy_cattle(20, rc)
        self.assertNotEqual(rc.list_of_workplaces[self.cf].cattle, [])
        rc.list_of_workplaces[self.cf].cattle.save()
        self.assertEqual(Cattle.objects.all().count(), 1)
        self.assertEqual(Cattle.objects.latest("id").size, 40)
        self.assertEqual(rc.list_of_workplaces[self.cf].cattle.size, 40)

    def test_buy_cattle(self):
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(Cattle.objects.all().count(), 0)
        self.assertIsNone(rc.list_of_workplaces[self.cf].cattle)
        self.cf.buy_cattle(20, rc)
        self.assertEqual(Cattle.objects.all().count(), 1)
        self.assertEqual(Cattle.objects.latest("id").size, 20)
        self.assertNotEqual(rc.list_of_workplaces[self.cf].cattle, [])
        self.assertEqual(rc.list_of_workplaces[self.cf].cattle.size, 20)

    def test_cattle_resources_production(self):
        self.assertEqual(Milk.objects.all().count(), 0)
        c = Cattle.objects.create(farm=self.cf, size=20)
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(rc.market.resources.get(Milk), None)
        rc.list_of_workplaces[self.cf].wage_payment(self.city)
        c.resource_production(
            1,
            rc,
            rc.list_of_workplaces[self.cf].workers_costs,
            rc.list_of_workplaces[self.cf]._get_productivity(),
        )
        self.assertEqual(Milk.objects.all().count(), 1, rc)
        self.assertEqual(len(rc.market.resources[Milk].instances), 1)
        m = Milk.objects.latest("id")
        self.assertEqual(m.size, 33)
        self.assertEqual(m.quality, 81)
        self.assertEqual(float(m.price), 24.48)

    def test_cattle_resoucre_production_with_existing_one(self):
        self.assertEqual(Milk.objects.all().count(), 0)
        c = Cattle.objects.create(farm=self.cf, size=20)
        Milk.objects.create(size=20, quality=81, market=self.market, price=8.24)
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(len(rc.market.resources[Milk].instances), 1)
        rc.list_of_workplaces[self.cf].wage_payment(self.city)
        c.resource_production(
            1,
            rc,
            rc.list_of_workplaces[self.cf].workers_costs,
            rc.list_of_workplaces[self.cf]._get_productivity(),
        )
        for x in rc.market.resources[Milk].instances:
            x.save()
        self.assertEqual(len(rc.market.resources[Milk].instances), 1)
        self.assertEqual(Milk.objects.all().count(), 1)
        m = Milk.objects.latest("id")
        self.assertEqual(m.size, 53)
        self.assertEqual(m.quality, 81)
        self.assertEqual(float(m.price), 0.38)
        rc_m = rc.market.resources[Milk].instances[-1]
        self.assertEqual(rc_m.size, 53)
        self.assertEqual(rc_m.quality, 81)
        self.assertEqual(float(round(rc_m.price, 2)), 0.38)

    def test_cattle_resoure_production_with_existing_diffrent(self):
        self.assertEqual(Milk.objects.all().count(), 0)
        c = Cattle.objects.create(farm=self.cf, size=20, price=8.24)
        m1 = Milk.objects.create(size=20, quality=20, market=self.market)
        rc = RootClass(city=self.city, user=self.user)
        self.assertEqual(len(rc.market.resources[Milk].instances), 1)
        self.assertEqual(Milk.objects.all().count(), 1)
        rc.list_of_workplaces[self.cf].wage_payment(self.city)
        c.resource_production(
            1,
            rc,
            rc.list_of_workplaces[self.cf].workers_costs,
            rc.list_of_workplaces[self.cf]._get_productivity(),
        )
        self.assertEqual(len(rc.market.resources[Milk].instances), 2)
        self.assertEqual(Milk.objects.all().count(), 2)
        m = Milk.objects.latest("id")
        self.assertEqual(m.size, 33)
        self.assertEqual(m.quality, 81)
        self.assertEqual(float(m.price), 24.48)
        self.assertEqual(m1.size, 20)
        self.assertEqual(m1.quality, 20)
        self.assertEqual(float(m.price), 24.48)
        rc_m = rc.market.resources[Milk].instances[-1]
        self.assertEqual(rc_m.size, 33)
        self.assertEqual(rc_m.quality, 81)
        self.assertEqual(float(rc_m.price), 24.48)

    def test_get_milk_quality_with_small_size(self):
        c = Cattle.objects.create(farm=self.cf, size=5)
        self.assertEqual(c._get_milk_quality(1), 100)

    def test_get_milk_quality_with_big_size(self):
        c = Cattle.objects.create(farm=self.cf, size=30)
        self.assertEqual(c._get_milk_quality(1), 72)

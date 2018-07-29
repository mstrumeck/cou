from django import test
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import CityField, City, WindPlant, WaterTower, SewageWorks
from django.db.models import Sum
from city_engine.turn_data.main import TurnCalculation
from city_engine.test.base import TestHelper
from cou.abstract import RootClass
from django.contrib.auth.models import User
from player.models import Profile


class ResourcesAllocationsTests(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.RA = ResourceAllocation(city=self.city, data=self.RC)
        self.populate_city()

    def test_pollution_cleaning(self):
        self.RA.pollution_allocation()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 29)
        self.RA.clean_allocation_data()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 0)

    def test_pollution_allocation(self):
        self.RA.clean_allocation_data()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 0)
        self.RA.pollution_allocation()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 29)

    def test_resources_allocation(self):
        WindPlant.objects.update(energy_allocated=0)
        WaterTower.objects.update(raw_water_allocated=0)
        SewageWorks.objects.update(clean_water_allocated=0)

        self.assertEqual(WindPlant.objects.filter(city=self.city).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], 0)
        self.assertEqual(WaterTower.objects.filter(city=self.city).aggregate(Sum('raw_water_allocated'))['raw_water_allocated__sum'], 0)
        self.assertEqual(SewageWorks.objects.filter(city=self.city).aggregate(Sum('clean_water_allocated'))['clean_water_allocated__sum'], 0)

        for x in range(3):
            TurnCalculation(city=self.city, data=self.RC, profile=Profile.objects.latest('id')).run()

        self.assertIn(WindPlant.objects.filter(city=self.city).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], range(5, 25))
        self.assertIn(WaterTower.objects.filter(city=self.city).aggregate(Sum('raw_water_allocated'))['raw_water_allocated__sum'], range(5, 50))
        self.assertIn(SewageWorks.objects.filter(city=self.city).aggregate(Sum('clean_water_allocated'))['clean_water_allocated__sum'], range(5, 40))

        self.assertNotEqual(sum([b.energy for b in self.RC.list_of_buildings]), 0)
        self.assertNotEqual(sum([b.water for b in self.RC.list_of_buildings]), 0)

# python manage.py dumpdata citizen_engine city_engine auth.user --indent=2 --output=city_engine/fixtures/fixture_natural_resources.json

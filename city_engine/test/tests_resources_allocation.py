from django import test
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import CityField, City, WindPlant, WaterTower, Residential, DumpingGround
from django.db.models import Sum
from city_engine.turn_data.main import TurnCalculation
from city_engine.test.base import TestHelper
from city_engine.abstract import RootClass


class ResourcesAllocationsTests(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.RC = RootClass(self.city)
        self.RA = ResourceAllocation(city=self.city, data=self.RC)
        self.populate_city()

    def test_pollution_cleaning(self):
        self.RA.pollution_allocation()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 18)
        self.RA.clean_city_field_data()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 0)

    def test_pollution_allocation(self):
        self.RA.clean_city_field_data()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 0)
        self.RA.pollution_allocation()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 18)

    def test_update_attr(self):
        ob = WindPlant.objects.latest('id')
        self.assertEqual(ob.water, 0)
        self.RA.update_attr(ob, 'water', 5)
        self.assertEqual(ob.water, 5)

    def test_resources_allocation(self):
        for building in WindPlant.objects.filter(city=self.city):
            building.resources_allocation_reset()

        for building in WaterTower.objects.filter(city=self.city):
            building.resources_allocation_reset()

        self.assertEqual(WindPlant.objects.filter(city=self.city).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], 0)
        self.assertEqual(WaterTower.objects.filter(city=self.city).aggregate(Sum('water_allocated'))['water_allocated__sum'], 0)

        for x in range(3):
            TurnCalculation(city=self.city).run()

        self.assertIn(WindPlant.objects.filter(city=self.city).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], range(5, 25))
        self.assertIn(WaterTower.objects.filter(city=self.city).aggregate(Sum('water_allocated'))['water_allocated__sum'], range(5, 25))


# python manage.py dumpdata citizen_engine city_engine auth.user --indent=2 --output=city_engine/fixtures/basic_fixture_resources_and_employees2.json

from django import test
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import CityField, City, WindPlant, WaterTower
from django.db.models import Sum
from city_engine.turn_data.main import TurnCalculation
from city_engine.test.base import TestHelper


class ResourcesAllocationsTests(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.RA = ResourceAllocation(city=self.city)
        self.populate_city()

    def test_check_if_resources_allocation_is_needed(self):
        self.assertEqual(self.RA.check_if_energy_allocation_is_needed(), 7)

    def test_data_cleaning(self):
        self.RA.clean_resource_data()
        self.assertEqual(WindPlant.objects.filter(city=self.city).aggregate(Sum('water'))['water__sum'], 0)
        self.assertEqual(WaterTower.objects.filter(city=self.city).aggregate(Sum('energy'))['energy__sum'], 0)

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

    def test_water_allocation(self):
        for building in WindPlant.objects.filter(city=self.city):
            building.resources_allocation_reset()

        for building in WaterTower.objects.filter(city=self.city):
            building.resources_allocation_reset()

        self.assertNotEqual(WaterTower.objects.latest('id').total_production(), 0)
        self.assertEqual(WaterTower.objects.latest('id').water_allocated, 0)
        self.assertEqual(WindPlant.objects.latest('id').water, 0)
        self.RA.water_allocation(WaterTower.objects.latest('id'), WaterTower.objects.latest('id').total_production(), WindPlant.objects.latest('id'))
        self.assertEqual(WaterTower.objects.latest('id').water_allocated, WindPlant.objects.latest('id').water_required)
        self.assertEqual(WindPlant.objects.latest('id').water, WindPlant.objects.latest('id').water_required)

    def test_energy_allocation(self):
        for building in WindPlant.objects.filter(city=self.city):
            building.resources_allocation_reset()

        for building in WaterTower.objects.filter(city=self.city):
            building.resources_allocation_reset()

        self.assertNotEqual(WindPlant.objects.latest('id').total_production(), 0)
        self.assertEqual(WindPlant.objects.latest('id').energy_allocated, 0)
        self.assertEqual(WaterTower.objects.latest('id').energy, 0)
        self.RA.energy_allocation(WindPlant.objects.latest('id'), WindPlant.objects.latest('id').total_production(), WaterTower.objects.latest('id'))
        self.assertEqual(WindPlant.objects.latest('id').energy_allocated, WaterTower.objects.latest('id').energy_required)
        self.assertEqual(WaterTower.objects.latest('id').energy, WaterTower.objects.latest('id').energy_required)

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

from django import test
from city_engine.main_view_data.main import CityStatsCenter
from city_engine.models import City


class CityStatsTests(test.TestCase):
    fixtures = ['basic_fixture.json']

    def test_city_stats_center_methods(self):
        city = City.objects.get(id=1)
        self.city_stats = CityStatsCenter(city=city)

        self.assertEqual(self.city_stats.energy_bilans, 6)
        self.assertEqual(self.city_stats.energy_allocation, 4)
        self.assertEqual(self.city_stats.energy_production, 10)
        self.assertEqual(self.city_stats.water_bilans, 12)
        self.assertEqual(self.city_stats.water_allocation, 20)
        self.assertEqual(self.city_stats.water_production, 32)
        self.assertEqual(self.city_stats.list_of_buildings,
                         ['Elektrownia wiatrowa', 'Elektrownia wiatrowa', 'Wieża ciśnień', 'Wieża ciśnień'])
        self.assertEqual(self.city_stats.building_under_construction, None)
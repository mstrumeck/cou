from django import test
from city_engine.models import CityField, City, WindPlant, WaterTower
from django.db.models import Sum
from city_engine.turn_data.main import TurnCalculation
from city_engine.main_view_data.allocation_pattern import AllocationPattern
import random


class TestAllocationPattern(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.AP = AllocationPattern()

    def test_of_create_allocation_pattern(self):
        generator = self.AP.create_allocation_pattern(2, 3)
        test_list_one = [(1, 3), (2, 2), (3, 3), (2, 4), (3, 4), (1, 4)]
        test_list_two = [(3, 4), (3, 2), (1, 4), (1, 2)]
        test_list_three = [(4, 3), (0, 5), (0, 3), (2, 5), (2, 1), (4, 5)]
        test_list_four = [(0, 4), (0, 2), (4, 4), (4, 2)]
        test_list_five = [(-1, 6), (2, 0), (5, 3), (-1, 3), (2, 6), (5, 6)]
        test_list_six = [(-1, 4), (5, 4), (5, 2), (-1, 2)]
        list_of_test_data = [test_list_one, test_list_two, test_list_three, test_list_four, test_list_five, test_list_six]
        for test_lists in list_of_test_data:
            generator_data = next(generator)
            for test_corr in test_lists:
                self.assertIn(test_corr, generator_data)

    def test_return_next_alloc(self):
        for corr in self.AP.return_next_alloc(hex_in_row=0, col=2, row=2, wave=1):
            self.assertIn(corr, [(2, 1), (2, 1), (2, 3), (2, 3)])
        for corr in self.AP.return_next_alloc(hex_in_row=0, col=4, row=4, wave=1):
            self.assertIn(corr, [(4, 3), (4, 5), (4, 5), (4, 3)])
        for corr in self.AP.return_next_alloc(hex_in_row=3, col=4, row=1, wave=4):
            self.assertIn(corr, [(4, 5), (-2, 5), (-2, 3), (4, 3)])
        for corr in self.AP.return_next_alloc(hex_in_row=4, col=2, row=2, wave=5):
            self.assertIn(corr, [(6, 1), (-2, 1), (6, 3), (-2, 3)])
        for corr in self.AP.return_next_alloc(hex_in_row=1, col=0, row=2, wave=2):
            self.assertIn(corr, [(1, 1), (1, -1), (3, 1), (3, -1)])

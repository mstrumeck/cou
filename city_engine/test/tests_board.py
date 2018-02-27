from django.contrib.auth.models import User
from city_engine.models import City
from django.test import TestCase
from city_engine.main_view_data.board import Board, ResourceAllocation, WindPlant,\
    assign_city_fields_to_board, CityField, WaterTower
import numpy as np


class BoardTest(TestCase):

    def setUp(self):
        first_user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.city = City.objects.create(name='Wrocław', user=first_user, cash=10000)

    def test_of_resource_allocation_pattern(self):
        pattern = ResourceAllocation(self.city)
        generator = pattern.create_allocation_pattern(2, 3)
        test_list_one = [(2, 4), (1, 3), (2, 2), (1, 4), (3, 4), (1, 2), (3, 3), (3, 2)]
        test_list_two = [(1, 2), (1, 4), (3, 4), (3, 2)]
        test_list_three = [(4, 3), (4, 5), (2, 1), (0, 1), (0, 5), (2, 5), (0, 3), (4, 1)]
        test_list_four = [(0, 4), (0, 2), (4, 4), (4, 2)]
        test_list_five = [(5, 3), (-1, 0), (5, 0), (-1, 3), (-1, 6), (5, 6), (2, 6), (2, 0)]
        test_list_six = [(-1, 4), (5, 4), (5, 2), (-1, 2)]
        list_of_test_data = [test_list_one, test_list_two, test_list_three, test_list_four, test_list_five, test_list_six]
        for test_lists in list_of_test_data:
            generator_data = next(generator)
            for test_corr in test_lists:
                assert test_corr in generator_data



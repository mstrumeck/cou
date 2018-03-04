from city_engine.models import City
from django.test import TestCase
from city_engine.main_view_data.board import ResourceAllocation


class BoardTest(TestCase):
    fixtures = ['basic_fixture.json']

    def test_of_resource_allocation_pattern(self):
        city = City.objects.get(id=1)
        pattern = ResourceAllocation(city)
        generator = pattern.create_allocation_pattern(2, 3)
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
                assert test_corr in generator_data



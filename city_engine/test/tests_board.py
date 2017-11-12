from django.contrib.auth.models import User
from city_engine.models import City
from django.test import TestCase
from city_engine.main_view_data.board import Board, ResourceAllocation


class BoardTest(TestCase):

    def test_of_resource_allocation(self):
        first_user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        city = City.objects.create(name='Wrocław', user=first_user, cash=10000)
        test_value = 6
        pattern = ResourceAllocation(city).create_allocation_pattern(test_value)
        tested_ids = []
        for x in range(int((Board.HEX_NUM_IN_ROW+1))):
            current_pattern = next(pattern)
            for item in current_pattern:
                if item in tested_ids or item < 0:
                    pass
                else:
                    tested_ids.append(item)

        assert test_value + 1 in tested_ids
        assert test_value - 1 in tested_ids
        assert test_value - Board.HEX_NUM_IN_ROW in tested_ids
        assert test_value + Board.HEX_NUM_IN_ROW in tested_ids

        assert test_value + 2 in tested_ids
        assert test_value - 2 in tested_ids
        assert test_value + (2 * Board.HEX_NUM_IN_ROW) in tested_ids

        assert test_value + 3 in tested_ids
        assert test_value - 3 in tested_ids

        assert test_value + 4 in tested_ids
        assert test_value - 4 in tested_ids

        for field_id in range(1, int(Board.HEX_NUM+1)):
            if field_id is test_value:
                pass
            else:
                assert field_id in tested_ids
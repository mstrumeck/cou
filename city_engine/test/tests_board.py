from django import test
from city_engine.main_view_data.trash_management import TrashManagement
from city_engine.main_view_data.employee_allocation import EmployeeAllocation
from city_engine.models import City, list_of_models, Trash, \
    list_of_buildings_in_city, WindPlant, WaterTower, DumpingGround, CityField, Building, BuldingsWithWorkes, Residential
from django.apps import apps
from .base import TestHelper
from city_engine.main_view_data.board import Board, HexDetail


# class BoardTests(test.TestCase, TestHelper):
#     fixtures = ['basic_fixture_resources_and_employees2.json']
#
#     def test_board(self):
#         nb = Board(city=City.objects.latest('id'))
#         print(nb.list_of_building_in_city_excluding(DumpingGround))
#         print({(b.city_field.row, b.city_field.col): b for b in nb.list_of_buildings_in_city()})
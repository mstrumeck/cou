from django import test
from django.contrib.auth.models import User

from city_engine.models import (
    City,
    WindPlant,
    WaterTower,
    PowerPlant,
    Waterworks,
    RopePlant,
    CoalPlant
)
from cou.turn_data import RootClass
from resources.models import Market


class TestRootClass(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        self.RC = RootClass(
            city=City.objects.latest("id"), user=self.user
        )

    def test_keys_in_dataset(self):
        for x in self.RC.datasets_for_turn_calculation():
            self.assertIn("allocated_resource", x.keys())
            self.assertIn("list_of_source", x.keys())
            self.assertIn("list_without_source", x.keys())

    def test_get_subclasses(self):
        self.assertEqual(
            self.RC.get_subclasses(abstract_class=PowerPlant, app_label="city_engine"),
            [WindPlant, RopePlant, CoalPlant],
        )
        self.assertEqual(
            self.RC.get_subclasses(abstract_class=Waterworks, app_label="city_engine"),
            [WaterTower],
        )

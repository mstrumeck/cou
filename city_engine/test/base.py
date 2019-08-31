from django import test
from django.contrib.auth.models import User

from citizen_engine.citizen_creation import CreateCitizen
from city_engine.models import (
    City,
)
from cou.global_var import ELEMENTARY, COLLEGE, PHD
from cou.turn_data import RootClass
from player.models import Profile
from resources.models import Market


class TestHelper(RootClass):
    def populate_city(self):
        for workplace in self.list_of_workplaces.keys():
            for el in range(workplace.elementary_employee_needed):
                CreateCitizen(self.city, self).create_with_workplace(
                    workplace, ELEMENTARY
                )
            for el in range(workplace.college_employee_needed):
                CreateCitizen(self.city, self).create_with_workplace(workplace, COLLEGE)
            for el in range(workplace.phd_employee_needed):
                CreateCitizen(self.city, self).create_with_workplace(workplace, PHD)


class BaseFixture(test.TestCase):
    def setUp(self):
        self.profile = Profile.objects.latest("id")
        self.user = User.objects.latest("id")
        self.city = City.objects.latest("id")
        Market.objects.create(profile=self.profile)

from django import test
from city_engine.main_view_data.city_stats import CityStatsCenter, CityEnergyStats, CityRawWaterStats, CityBuildingStats, CityPopulationStats
from city_engine.models import City, ProductionBuilding, TradeDistrict, WindPlant, DumpingGround, StandardLevelResidentialZone
from .base import TestHelper
from cou.abstract import RootClass
from django.contrib.auth.models import User
from citizen_engine.models import Citizen, Profession, Education
from cou.global_var import COLLEGE, FEMALE, ELEMENTARY, PHD


class DataContainersTests(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.latest('id')

    def test_valid_field_for_building_with_worker(self):
        dg = DumpingGround.objects.latest('id')
        wp = WindPlant.objects.latest('id')
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.list_of_buildings[dg].elementary_vacancies, 5)
        self.assertEqual(RC.list_of_buildings[dg].college_vacancies, 0)
        self.assertEqual(RC.list_of_buildings[dg].phd_vacancies, 0)

        self.assertEqual(RC.list_of_buildings[wp].elementary_vacancies, 5)
        self.assertEqual(RC.list_of_buildings[wp].college_vacancies, 0)
        self.assertEqual(RC.list_of_buildings[wp].phd_vacancies, 0)

    def test_salary_expectation_calculation_without_education(self):
        sr = StandardLevelResidentialZone.objects.latest('id')
        s = Citizen.objects.create(
            city=self.city,
            age=18,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            resident_object=sr,
        )
        Profession.objects.create(citizen=s, proficiency=0.5, name='Nauczyciel')
        rc = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(rc.citizens_in_city[s].salary_expectation, 0)

    def test_salary_expectation_calculation_without_profession(self):
        sr = StandardLevelResidentialZone.objects.latest('id')
        s = Citizen.objects.create(
            city=self.city,
            age=18,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=COLLEGE,
            resident_object=sr,
        )
        Education.objects.create(citizen=s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=s, name=COLLEGE, effectiveness=1, if_current=False)
        rc = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(rc.citizens_in_city[s].salary_expectation, 0)

    def test_salary_expectation_calculation_without_residential_object(self):
        s = Citizen.objects.create(
            city=self.city,
            age=18,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=COLLEGE,
        )
        Education.objects.create(citizen=s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=s, name=COLLEGE, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=s, proficiency=0.5, name='Nauczyciel')
        rc = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(rc.citizens_in_city[s].salary_expectation, 0)

    def test_valid_field_for_citizen_pass(self):
        sr = StandardLevelResidentialZone.objects.latest('id')
        s = Citizen.objects.create(
            city=self.city,
            age=18,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=COLLEGE,
            resident_object=sr,
        )
        Education.objects.create(citizen=s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=s, name=COLLEGE, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=s, proficiency=0.5, name='Nauczyciel')
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=ELEMENTARY,
            resident_object=sr,
        )
        Education.objects.create(citizen=m, name=ELEMENTARY, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=m, proficiency=0.2, name='Spawacz')
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=PHD,
            resident_object=sr,
        )
        Education.objects.create(citizen=p, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=p, name=COLLEGE, effectiveness=1, if_current=False)
        Education.objects.create(citizen=p, name=PHD, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=p, proficiency=0.8, name='Nauczyciel Akademicki')
        rc = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(rc.citizens_in_city[s].salary_expectation, 600)
        self.assertEqual(rc.citizens_in_city[m].salary_expectation, 240)
        self.assertEqual(rc.citizens_in_city[p].salary_expectation, 1080)

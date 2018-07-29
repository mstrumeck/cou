from django import test
from django.contrib.auth.models import User
from city_engine.main_view_data.board import assign_city_fields_to_board
from city_engine.main_view_data.city_stats import CityStatsCenter
from citizen_engine.citizen_creation import CreateCitizen
from cou.abstract import RootClass
from city_engine.models import City, CityField, \
    Residential, \
    ProductionBuilding, \
    WindPlant, CoalPlant, RopePlant, \
    WaterTower


class TestHelper(RootClass):

    def populate_city(self):
        for workplace in self.list_of_workplaces():
            for employ in range(workplace.max_employees):
                CreateCitizen().create_with_workplace(city=self.city, workplace=workplace)


class BaseFixture(test.TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Michał', password='12345', email='random@wp.pl')
        self.client.login(username='Michał', password='12345', email='random@wp.pl')
        self.city = City.objects.create(name='Wrocław', user=self.user)
        assign_city_fields_to_board(self.city)

        self.field_one = CityField.objects.get(row=0, col=1, city=self.city)
        self.field_two = CityField.objects.get(row=0, col=2, city=self.city)
        field_three = CityField.objects.get(row=1, col=1, city=self.city)
        field_four = CityField.objects.get(row=1, col=1, city=self.city)

        self.data = RootClass(self.city, user=self.user)


class CityFixture(test.TestCase):
    def setUp(self):
        first_user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.client.login(username='test_username', password='12345', email='random@wp.pl')
        self.city = City.objects.create(name='Wrocław', user=first_user, cash=10000)
        self.data = RootClass(self.city, user=first_user)
        self.city_stats = CityStatsCenter(self.city, self.data)

        second_user = User.objects.create_user(username='test_username_2', password='54321', email='random2@wp.pl')
        second_city = City.objects.create(name='Łódź', user=second_user, cash=10000)

        assign_city_fields_to_board(self.city)
        assign_city_fields_to_board(second_city)

        CityField.objects.get(row=0, col=0, city=self.city).if_production = True
        CityField.objects.get(row=0, col=1, city=self.city).if_residential = True
        CityField.objects.get(row=0, col=2, city=self.city).if_electricity = True
        CityField.objects.get(row=0, col=0, city=self.city).save()
        CityField.objects.get(row=0, col=1, city=self.city).save()
        CityField.objects.get(row=0, col=2, city=self.city).save()

        CityField.objects.get(row=0, col=0, city=second_city).if_production = True
        CityField.objects.get(row=0, col=1, city=second_city).if_residential = True
        CityField.objects.get(row=0, col=2, city=second_city).if_electricity = True
        CityField.objects.get(row=0, col=0, city=second_city).save()
        CityField.objects.get(row=0, col=1, city=second_city).save()
        CityField.objects.get(row=0, col=2, city=second_city).save()

        first_factory = ProductionBuilding()
        first_factory.max_employees = 20
        first_factory.current_employees = 0
        first_factory.production_level = 0
        first_factory.build_time = 3
        first_factory.city = self.city
        first_factory.if_under_construction = False
        first_factory.city_field = CityField.objects.get(row=0, col=0, city=self.city)
        first_factory.save()

        second_factory = ProductionBuilding()
        second_factory.max_employees = 20
        second_factory.current_employees = 0
        second_factory.production_level = 0
        second_factory.build_time = 3
        second_factory.city = second_city
        second_factory.if_under_construction = False
        second_factory.city_field = CityField.objects.get(row=0, col=0, city=second_city)
        second_factory.save()

        first_residential = Residential()
        first_residential.max_population = 20
        first_residential.current_population = 4
        first_residential.residential_level = 0
        first_residential.build_time = 3
        first_residential.city = self.city
        first_residential.if_under_construction = False
        first_residential.city_field = CityField.objects.get(row=0, col=1, city=self.city)
        first_residential.save()

        second_residential = Residential()
        second_residential.max_population = 20
        second_residential.current_population = 4
        second_residential.residential_level = 0
        second_residential.build_time = 3
        second_residential.city = second_city
        second_residential.if_under_construction = False
        second_residential.city_field = CityField.objects.get(row=0, col=1, city=second_city)
        second_residential.save()

        first_power_plant = WindPlant()
        first_power_plant.max_employees = 5
        first_power_plant.build_time = 3
        first_power_plant.power_nodes = 1
        first_power_plant.max_power_nodes = 10
        first_power_plant.energy_production = 5
        first_power_plant.city = self.city
        first_power_plant.if_under_construction = True
        first_power_plant.city_field = CityField.objects.get(row=0, col=2, city=self.city)
        first_power_plant.save()

        second_power_plant = WindPlant()
        second_power_plant.max_employees = 10
        second_power_plant.build_time = 3
        second_power_plant.power_nodes = 1
        second_power_plant.max_power_nodes = 10
        second_power_plant.energy_production = 5
        second_power_plant.city = second_city
        second_power_plant.if_under_construction = False
        second_power_plant.city_field = CityField.objects.get(row=0, col=2, city=second_city)
        second_power_plant.save()

        third_power_plant = RopePlant()
        third_power_plant.max_employees = 10
        third_power_plant.build_time = 4
        third_power_plant.power_nodes = 1
        third_power_plant.max_power_nodes = 4
        third_power_plant.energy_production = 30
        third_power_plant.city = self.city
        third_power_plant.if_under_construction = False
        third_power_plant.city_field = CityField.objects.get(row=0, col=3, city=self.city)
        third_power_plant.save()

        fourth_power_plant = CoalPlant()
        fourth_power_plant.max_employees = 15
        fourth_power_plant.build_time = 5
        fourth_power_plant.power_nodes = 1
        fourth_power_plant.max_power_nodes = 4
        fourth_power_plant.energy_production = 30
        fourth_power_plant.city = self.city
        fourth_power_plant.if_under_construction = False
        fourth_power_plant.city_field = CityField.objects.get(row=1, col=0, city=self.city)
        fourth_power_plant.save()

        waterwork = WaterTower()
        waterwork.max_employees = 5
        waterwork.build_time = 1
        waterwork.water_production = 20
        waterwork.city = self.city
        waterwork.if_under_construction = False
        waterwork.city_field = CityField.objects.get(row=1, col=1, city=self.city)
        waterwork.save()

        self.city_stats = CityStatsCenter(self.city, self.data)
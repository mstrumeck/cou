from django.test import TestCase
from .models import Citizen
from city_engine.models import ProductionBuilding, Residential
from city_engine.models import City
from django.contrib.auth.models import User


class NewCitizenTest(TestCase):

    def setUp(self):
        user = User.objects.create()
        city = City.objects.create(name='Wrocław', user=user, cash=1000)
        fabric = ProductionBuilding.objects.create(max_employees=20,
                                                   current_employees=0,
                                                   production_level=0,
                                                   city=city,
                                                   trash=0,
                                                   health=0,
                                                   energy=0,
                                                   water=0,
                                                   crime=0,
                                                   pollution=0,
                                                   recycling=0,
                                                   city_communication=0)
        residential1 = Residential.objects.create(max_population=20,
                                                  current_population=0,
                                                  residential_level=0,
                                                  city=city,
                                                  trash=0,
                                                  health=0,
                                                  energy=0,
                                                  water=0,
                                                  crime=0,
                                                  pollution=0,
                                                  recycling=0,
                                                  city_communication=0
                                                  )
        citizen1 = Citizen.objects.create(age=40,
                                          health=25,
                                          income=10,
                                          city=city,
                                          residential_id=residential1.id,
                                          production_building_id=fabric.id)

    def test_if_citizen_exist(self):
        city = City.objects.get(name='Wrocław')
        self.assertTrue(Citizen.objects.filter(age=40,
                                               health=25,
                                               city=city))


class CreateCitizensTest(TestCase):

    def setUp(self):
        user = User.objects.create()
        city = City.objects.create(name='Łódź', user=user, cash=1000)
        fabric = ProductionBuilding.objects.create(max_employees=20,
                                                   current_employees=0,
                                                   production_level=0,
                                                   city=city,
                                                   trash=0,
                                                   health=0,
                                                   energy=0,
                                                   water=0,
                                                   crime=0,
                                                   pollution=0,
                                                   recycling=0,
                                                   city_communication=0)
        residential1 = Residential.objects.create(max_population=20,
                                                  current_population=0,
                                                  residential_level=0,
                                                  city=city,
                                                  trash=0,
                                                  health=0,
                                                  energy=0,
                                                  water=0,
                                                  crime=0,
                                                  pollution=0,
                                                  recycling=0,
                                                  city_communication=0
                                                  )

    def test_saving_and_retreving_citizens(self):
        city = City.objects.get(name='Łódź')
        residential = Residential.objects.get(city=city)
        production = ProductionBuilding.objects.get(city=city)
        first_citizen = Citizen()
        first_citizen.age = 22
        first_citizen.health = 20
        first_citizen.city = city
        first_citizen.income = 100
        first_citizen.residential = residential
        first_citizen.production_building = production
        first_citizen.save()

        second_citizen = Citizen()
        second_citizen.age = 60
        second_citizen.health = 10
        second_citizen.city = city
        second_citizen.income = 100
        second_citizen.residential = residential
        second_citizen.production_building = production
        second_citizen.save()

        saved_citizen = Citizen.objects.all()
        self.assertEqual(saved_citizen.count(), 2)

        first_saved_citizen = saved_citizen[0]
        second_saved_citizen = saved_citizen[1]

        self.assertEqual(first_saved_citizen.age, 22)
        self.assertEqual(second_saved_citizen.age, 60)
        self.assertEqual(first_saved_citizen.health, 20)
        self.assertEqual(second_saved_citizen.health, 10)
        self.assertEqual(first_saved_citizen.city, city)
        self.assertEqual(second_saved_citizen.city, city)
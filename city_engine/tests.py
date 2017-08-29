from django.test import TestCase
from city_engine.models import City, Residential, ProductionBuilding
from django.contrib.auth.models import User
from citizen_engine.models import Citizen
from django.db.models import Sum
from player.models import Profile
from django.urls import reverse, resolve
from django.http import HttpRequest
from .views import main_view


class CityViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        city = City.objects.create(name='Wrocław', user=user, cash=100)
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
        citizen2 = Citizen.objects.create(age=25,
                                          health=35,
                                          city=city,
                                          income=10,
                                          residential_id=residential1.id,
                                          production_building_id=fabric.id
                                          )
        citizen3 = Citizen.objects.create(age=15,
                                          health=45,
                                          city=city,
                                          income=10,
                                          residential_id=residential1.id,
                                          production_building_id=fabric.id
                                          )

    def test_city_view(self):
        self.client.login(username='test_username', password='12345')
        city = City.objects.get(name='Wrocław')
        response = self.client.get('main_view/')
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, city.name)
        self.assertContains(response, 'Pieniądze: {}'.format(city.cash))
        self.assertContains(response, 'Domy: {}'.format(Residential.objects.filter(city_id=city.id).count()))
        self.assertContains(response, 'Mieszkańcy: {}/{}'.format(
            Citizen.objects.filter(city_id=city.id).count(),
            Residential.objects.filter(city_id=city.id).aggregate(Sum('max_population'))['max_population__sum']))
        self.assertContains(response, 'Dochody: {}'.format(
            Citizen.objects.filter(city_id=city.id).aggregate(Sum('income'))['income__sum']))


class CityPerformanceTests(TestCase):
    def setUp(self):
        user = User.objects.create()
        city = City.objects.create(name='Wrocław', user=user, cash=100)
        citizens = [Citizen() for i in range(1000)]


# class TurnSystemTests(TestCase):
#     def setUp(self):
#         user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
#         city = City.objects.create(name='Wrocław', user=user, cash=100)
#         # profile = Profile.objects.create(user=user)
#
#     def test_turn_view(self):
#         login = self.client.login(username='test_username', password='12345')
#         city = City.objects.get(name='Wrocław')
#         # profile = Profile.objects.get()
#         response = self.client.get('main_view')
#         self.assertTemplateUsed(response, 'main_view.html')
#         # self.assertContains(response, '{}/12'.format(profile.current_turn))
#         self.assertContains(response, 'Kolejna tura')
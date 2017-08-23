from django.test import TestCase
from city_engine.models import City, TurnSystem
from django.contrib.auth.models import User
from citizen_engine.models import Citizen
from django.urls import reverse, resolve
from django.http import HttpRequest
from .views import main_view


class CityViewTests(TestCase):
    def setUp(self):
        user = User.objects.create()
        city = City.objects.create(name='Wrocław', user=user, cash=100)
        turns = TurnSystem.objects.create(city_id=city.id)
        citizen1 = Citizen.objects.create(name='Jan', surname='Strumecki', age=40, health=25, city=city)
        citizen2 = Citizen.objects.create(name='Ola', surname='Strumecki', age=25, health=35, city=city)
        citizen3 = Citizen.objects.create(name='Kacper', surname='Strumecki', age=15, health=45, city=city)

    def test_city_view(self):
        city = City.objects.get(name='Wrocław')
        response = self.client.get('/{}/main_view/'.format(city.id))
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, city.name)
        self.assertContains(response, 'Liczba mieszkańców: {}'.format(Citizen.objects.filter(city_id=city.id).count()))
        self.assertContains(response, 'Pieniądze: {}'.format(city.cash))


class CityPerformanceTests(TestCase):
    def setUp(self):
        user = User.objects.create()
        city = City.objects.create(name='Wrocław', user=user, cash=100)
        citizens = [Citizen() for i in range(1000)]


class TurnSystemTests(TestCase):
    def setUp(self):
        user = User.objects.create()
        city = City.objects.create(name='Wrocław', user=user, cash=100)
        TurnSystem.objects.create(city=city)

    def test_turn_view(self):
        city = City.objects.get(name='Wrocław')
        turns = TurnSystem.objects.get(city_id=city.id)
        response = self.client.get('/{}/main_view/'.format(city.id))
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, '{}/{}'.format(turns.current_turn, turns.max_turn))
        self.assertContains(response, 'Kolejna tura')
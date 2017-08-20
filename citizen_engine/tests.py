from django.test import TestCase
from .models import Citizen
from city_engine.models import City


class NewCitizenTest(TestCase):

    def setUp(self):
        city = City.objects.create(name='Wrocław')
        global city
        citizen = Citizen.objects.create(name='Jan', surname='Strumecki', age=40, health=25, city=city)
        Citizen.objects.create(name='Michał', surname='Strumecki', age=40, health=55, city=city)

    def test_if_citizen_exist(self):
        self.assertTrue(Citizen.objects.filter(name='Jan',
                                               surname='Strumecki',
                                               age=40,
                                               health=25,
                                               city=city.id))


class CreateCitizensTest(TestCase):

    def setUp(self):
        city = City.objects.create(name='Łódź')
        global city

    def test_saving_and_retreving_citizens(self):
        first_citizen = Citizen()
        first_citizen.name = 'Daniel'
        first_citizen.surname = 'Grzebelec'
        first_citizen.age = 22
        first_citizen.health = 20
        first_citizen.city = city
        first_citizen.save()

        second_citizen = Citizen()
        second_citizen.name = 'Anna'
        second_citizen.surname = 'Gierasimowicz'
        second_citizen.age = 60
        second_citizen.health = 10
        second_citizen.city = city
        second_citizen.save()

        saved_citizen = Citizen.objects.all()
        self.assertEqual(saved_citizen.count(), 2)

        first_saved_citizen = saved_citizen[0]
        second_saved_citizen = saved_citizen[1]

        self.assertEqual(first_saved_citizen.name, 'Daniel')
        self.assertEqual(second_saved_citizen.name, 'Anna')
        self.assertEqual(first_saved_citizen.surname, 'Grzebelec')
        self.assertEqual(second_saved_citizen.surname, 'Gierasimowicz')
        self.assertEqual(first_saved_citizen.age, 22)
        self.assertEqual(second_saved_citizen.age, 60)
        self.assertEqual(first_saved_citizen.health, 20)
        self.assertEqual(second_saved_citizen.health, 10)
        self.assertEqual(first_saved_citizen.city, city)
        self.assertEqual(second_saved_citizen.city, city)
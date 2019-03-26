from random import choice, randrange

import names
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

from citizen_engine.models import Citizen, Family
from citizen_engine.models import Education
from city_engine.main_view_data.board import assign_city_fields_to_board
from city_engine.models import (
    City,
    Field,
    StandardLevelResidentialZone,
)
from city_engine.test.base import TestHelper
from cou.global_var import ELEMENTARY
from map_engine.models import Map
from player.models import Profile
from resources.models import Market


class BaseTestOfficial(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.city = City.objects.latest("id")
        self.user = User.objects.latest("id")
        self.browser.implicitly_wait(3)
        self.profile = Profile.objects.latest("id")
        self.m = Market.objects.create(profile=self.profile)
        sex = choice(Citizen.SEX)[0]
        surname = names.get_last_name()
        f = Family.objects.create(surname=surname, city=self.city)
        c = Citizen.objects.create(
            city=self.city,
            age=randrange(18, 24),
            name=names.get_first_name(sex.lower()),
            surname=surname,
            health=10,
            month_of_birth=randrange(1, 12),
            sex=sex,
            family=f,
            cash=500,
        )

        for x in range(13):
            sex = choice(Citizen.SEX)[0]
            surname = names.get_last_name()
            f = Family.objects.create(surname=surname, city=self.city)
            c = Citizen.objects.create(
                city=self.city,
                age=randrange(18, 24),
                name=names.get_first_name(sex.lower()),
                surname=surname,
                health=10,
                month_of_birth=randrange(1, 12),
                sex=sex,
                family=f,
                cash=500,
                edu_title=ELEMENTARY,
            )
            Education.objects.create(citizen=c, name=ELEMENTARY, effectiveness=0.50)

        field = list(Field.objects.all())
        s = StandardLevelResidentialZone.objects.create(
            city=self.city, if_under_construction=False, city_field=field.pop()
        )
        s.self__init(20)
        s.save()
        self.city.save()
        self.profile.if_social_enabled = True
        self.profile.save()

    def tearDown(self):
        self.browser.quit()


class BaseTest(StaticLiveServerTestCase, TestHelper):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.player_one = "Michał"
        self.player_two = "Alicja"
        self.password_one = "michal#12345"
        self.password_two = "koteczki#12345"
        self.city_one_name = "Wrocław"
        self.city_two_name = "Oleśnica"
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def create_first_user(self):
        self.user_one = User.objects.create_user(
            username=self.player_one, password=self.password_one
        )
        self.city_one = City.objects.create(name=self.city_one_name, user=self.user_one)
        self.market_one = Market.objects.create(profile=Profile.objects.latest("id"))
        assign_city_fields_to_board(self.city_one)

    def create_second_user(self):
        self.user_two = User.objects.create_user(
            username=self.player_two, password=self.password_two
        )
        self.city_two = City.objects.create(name=self.city_two_name, user=self.user_two)
        self.market_two = Market.objects.create(profile=Profile.objects.latest("id"))
        assign_city_fields_to_board(self.city_two)


class BaseTestForOnePlayer(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.username = "Michał"
        self.password = "michal12345"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.city = City.objects.create(name="Wrocław", user=self.user)

    def tearDown(self):
        self.browser.quit()


class BaseTestForTwoPlayers(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.first_username = "test_username"
        self.first_password = "michal12345"

        self.second_username = "test_username_2"
        self.second_password = "54321michal"

        self.first_user = User.objects.create_user(
            username=self.first_username, password=self.first_password
        )
        self.second_user = User.objects.create_user(
            username=self.second_username, password=self.second_password
        )

        self.first_city = City.objects.create(name="Wrocław", user=self.first_user)
        assign_city_fields_to_board(self.first_city, player=self.first_user.player, map=Map.objects.latest('id'))

        self.second_city = City.objects.create(name="Łódź", user=self.second_user)
        assign_city_fields_to_board(self.second_city, player=self.second_user.player, map=Map.objects.latest('id'))

    def tearDown(self):
        self.browser.quit()

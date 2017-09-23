from selenium import webdriver
from .base import BaseTest
from city_engine.models import City
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase, LiveServerTestCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import unittest
import time
import sys


class CreateBuildingsTest(BaseTest):

    def test_create_power_plant(self):
        username = 'test_username'
        password = 'michal12345'
        user = User.objects.create_user(username=username, password=password)
        City.objects.create(name='Wrocław', user=user)
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text('Zaloguj').click()
        time.sleep(1)
        username_field = self.browser.find_element_by_id('id_username')
        password_field = self.browser.find_element_by_id('id_password')
        username_field.send_keys(username)
        password_field.send_keys(password)
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(1)
        self.assertIn('Miasto {}'.format(City.objects.get(name='Wrocław').name), self.browser.title)
        self.browser.find_element_by_id('buildPowerPlant').click()
        time.sleep(10)
        time.sleep(2)
        self.assertIn('Elektrownia wiatrowa', self.client.get('/main_view/'))

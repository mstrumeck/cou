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





# class TurnSystemTest(LiveServerTestCase):
#
#     def setUp(self):
#         self.browser = webdriver.Chrome()
#         user = User.objects.create_superuser(username='test_username', password='michal12345', email='test@wp.pl')
#         City.objects.create(name='Wrocław', user=user, cash=100)
#
#     def tearDown(self):
#         self.browser.quit()
#
#     def test_if_turn_work_correct(self):
#         # city = City.objects.get(name='Wrocław')
#         self.browser.get('http://localhost:8000/main_view')
#         self.assertIn('Login', self.browser.title)
#         username_field = self.browser.find_element_by_id('id_username')
#         password_field = self.browser.find_element_by_id('id_password')
#         username_field.send_keys('test_username')
#         password_field.send_keys('michal12345')
#         time.sleep(1)
#         self.browser.find_element_by_tag_name('button').click()
#         time.sleep(5)
#         # login_page = self.browser.get('http://localhost:8000/login')
#         # WebDriverWait(login_page, 20).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'container')))


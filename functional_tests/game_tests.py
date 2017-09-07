from selenium import webdriver
from city_engine.models import City
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase, LiveServerTestCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import unittest
import time


class SignupAndLoginTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_signup(self):
        self.browser.get('http://localhost:8000/signup')
        self.assertIn('Rejestracja', self.browser.title)
        username_field = self.browser.find_element_by_id('id_username')
        password_field1 = self.browser.find_element_by_id('id_password1')
        password_field2 = self.browser.find_element_by_id('id_password2')
        username_field.send_keys('test_username')
        password_field1.send_keys('michal12345')
        password_field2.send_keys('michal12345')
        time.sleep(1)
        self.browser.find_element_by_tag_name('button').click()
        self.browser.get('http://localhost:8000/create_city')
        time.sleep(10)
        self.assertIn('Tworzenie miasta', self.browser.title)
        city_name_field = self.browser.find_element_by_id('id_name')
        city_name_field.send_keys('Wrocław')
        self.browser.find_element_by_tag_name('button').click()
        time.sleep(10)
        self.assertIn('Miasto {}'.format('Wrocław'), self.browser.title)



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


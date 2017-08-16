from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
from django.contrib.auth.models import User
from django.test import LiveServerTestCase


class NewPlayerSetupAccount(LiveServerTestCase):
    name = 'Michał'
    last_name = 'Strumecki'
    password = '12345'
    mail = 'michal.strumecki@wp.pl'
    nick = 'Kleju_0011'

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_create_new_account(self):
        self.browser.get('http://localhost:8081/login')
        registration_form = self.browser.find_element_by_id('registration_form')

        first_name_input = self.browser.find_element_by_id('first_name_input')
        first_name_input.send_keys(self.name)

        last_name_input = self.browser.find_element_by_id('last_name_input')
        last_name_input.send_keys(self.last_name)

        nick_input = self.browser.find_element_by_id('nick')
        nick_input.send_keys(self.nick)

        mail_input = self.browser.find_element_by_id('e-mail_input')
        mail_input.send_keys(self.mail)

        password_input = self.browser.find_element_by_id('password')
        password_input.send_keys(self.password)

        registration_form.submit()

        Users = User.objects.all()
        self.assertEqual(len(Users),1)

if __name__ == '__main__':
    unittest.main()




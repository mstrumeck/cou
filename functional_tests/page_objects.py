from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
import random
import string
from selenium.webdriver.support.ui import WebDriverWait
import time
from django.contrib.auth.models import User
from city_engine.main_view_data.board import assign_city_fields_to_board
from city_engine.main_view_data.board import Board
from city_engine.main_view_data.city_stats import CityStatsCenter
from city_engine.models import City, CityField, \
    WindPlant, CoalPlant, RopePlant, \
    WaterTower


class BasePage(object):

    def __init__(self, driver, static_server):
        self.driver = driver
        self.static_server = static_server
        # self.wait = ui.WebDriverWait(self.driver, 10)

    def wait_for_element_with_name(self, name):
        WebDriverWait(self.driver, timeout=30).until(lambda b: b.find_element_by_name(name))

    def fill_form_by_css(self, form_css, value):
        elem = self.driver.find_element_by_css_selector(form_css)
        elem.send_keys(value)

    def fill_form_by_id(self, id_element, value):
        return self.driver.find_element_by_id(id_element).send_keys(value)

    def get_element_by_css(self, value):
        return self.driver.find_element_by_class_name(value)

    def get_element_by_tag_name(self, value):
        return self.driver.find_element_by_name(value)

    def get_element_by_id(self, id):
        return self.driver.find_element_by_id(id)

    def get_element_by_text(self, value):
        return self.driver.find_element_by_link_text(value)

    def get_element_by_xpath(self, root):
        return self.driver.find_element_by_xpath(root)

    def press_button_by_name(self, value):
        return self.get_element_by_tag_name(value).click()

    def navigate(self, site):
        self.driver.get(self.static_server + site)


class Homepage(BasePage):

    def getMainView(self):
        return MainView(self.driver, self.static_server)

    def getLoginPage(self):
        return LoginPage(self.driver, self.static_server)

    def click_registration_button(self):
        return self.driver.find_element_by_link_text('Rejestracja').click()


class MainView(BasePage):

    def logout(self):
        return self.get_element_by_text('Wyloguj').click()

    def choose_hex(self, hex_id):
        return self.get_element_by_id(hex_id).click()

    def choose_the_building(self, value):
        return self.get_element_by_tag_name(value).click()

    def choose_the_building_type_button(self, value):
        return self.get_element_by_tag_name(value).click()

    def build_the_building_from_single_choice(self, building_name, hex_id):
        self.choose_the_building(building_name)
        self.choose_hex(hex_id)

    def build_the_building_from_multiple_choice(self, building_type, building_name, hex_id):
        self.choose_the_building_type_button(building_type)
        time.sleep(1)
        self.choose_the_building(building_name)
        self.choose_hex(hex_id)

    # def check_if_buildings_are_under_construction(self):

    def next_turn(self):
        return self.get_element_by_text('Kolejna tura').click()

    def next_turns(self, nr_of_turns):
        for x in range(nr_of_turns):
            self.next_turn()


class LoginPage(BasePage):

    def navigate_to_main_throught_login(self, user, username, password, city, assertIn, assertTrue):
        homepage = Homepage(self.driver, self.static_server)
        homepage.navigate('/main_view')
        assertIn('Login', self.driver.title)
        login_page = LoginPage(self.driver, self.static_server)
        login_page.login(username, password)
        assertTrue(user.is_authenticated)
        assertIn('Miasto {}'.format(city.name), self.driver.title)

    def login(self, username, password):
        self.fill_username_field(username)
        self.fill_password_field(password)
        self.click_submit_button()

    def fill_username_field(self, username):
        return self.fill_form_by_id('id_username',  username)

    def fill_password_field(self, password):
        return self.fill_form_by_id('id_password', password)

    def click_submit_button(self):
        return self.press_button_by_name('submit')


class SignupPage(BasePage):

    def create_account(self, username, password, city_name):
        self.set_username(username)
        self.set_password(password)
        self.set_city_name(city_name)
        self.submit()

    def create_fake_account(self, username, password, city_name):
        self.set_username(username)
        self.set_fake_password(password)
        self.set_city_name(city_name)
        self.submit()

    def if_error_displayed(self):
        error = self.get_element_by_css('errorlist')
        return error.is_displayed()

    def login(self, first, last):
        self.fill_form_by_id("id_username", first)
        self.fill_form_by_id("id_password", last)

    def set_username(self, username):
        return self.fill_form_by_id('id_username', username)

    def set_city_name(self, city_name):
        return self.fill_form_by_id('id_name', city_name)

    def setEmail(self, email):
        self.fill_form_by_id("id_email", email)

    def set_password(self, password):
        self.fill_form_by_id("id_password1", password)
        self.fill_form_by_id("id_password2", password)

    def set_fake_password(self, password):
        self.fill_form_by_id('id_password1', password)
        self.fill_form_by_id('id_password2', "".join([random.choice(string.ascii_letters) for letter in range(7)]))

    def setProductName(self, name):
        self.fill_form_by_id("id_first_product_name", name)

    def submit(self):
        return self.press_button_by_name('submit')
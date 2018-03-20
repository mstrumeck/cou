from .models import Citizen
from random import choice, randrange
from city_engine.models import Residential, City, WaterTower, ProductionBuilding, WindPlant


class CreateCitizen(object):
    def __init__(self, city, target_production):
        self.city = city
        self.target_production = target_production
        self.citizen = Citizen()
        self.create()

    def create(self):
        self.citizen.city = self.city
        self.citizen.type_of_work = self.target_production
        self.set_place_of_work()
        self.citizen.residential = self.choose_residential()
        self.citizen.age = randrange(18, 60)
        self.citizen.income = 10
        self.citizen.health = 10
        self.citizen.save()

    def choose_residential(self):
        return choice([residential for residential in Residential.objects.filter(city=self.city) if residential.max_population >= residential.population])

    def set_place_of_work(self):
        if self.target_production == 'WP':
            building_with_vacancies = [windplant for windplant in WindPlant.objects.filter(city=self.city) if
                                             windplant.current_employees < windplant.max_employees]
            if building_with_vacancies:
                self.citizen.work_in_windplant = choice(building_with_vacancies)

        elif self.target_production == 'WT':
            building_with_vacancies = [watertower for watertower in WaterTower.objects.filter(city=self.city) if
                                         watertower.current_employees < watertower.max_employees]
            if building_with_vacancies:
                self.citizen.work_in_watertower = choice(building_with_vacancies)

        elif self.target_production == 'PB':
            building_with_vacancies = [production for production in ProductionBuilding.objects.filter(city=self.city)
                                                 if production.current_employees < production.max_employees]
            if building_with_vacancies:
                self.citizen.work_in_production = choice(building_with_vacancies)

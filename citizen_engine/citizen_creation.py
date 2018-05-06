from random import choice, randrange
from city_engine.models import Residential, City, WaterTower, ProductionBuilding, WindPlant, DustCart, DumpingGround
from citizen_engine.models import Citizen


class CreateCitizen(object):

    def create_with_workplace(self, city, workplace):
        workplace.employee.create(
            city=city,
            age=randrange(18, 60),
            income=10,
            health=10,
            resident=self.choose_residential(city)
        )

    def create_without_workplace(self, city):
        Citizen.objects.create(city=city,
                               age=randrange(18, 60),
                               income=10,
                               health=10,
                               resident=self.choose_residential(city))

    def choose_residential(self, city):
        return choice([residential for residential in Residential.objects.filter(city=city)
                       if residential.max_population >= residential.population])
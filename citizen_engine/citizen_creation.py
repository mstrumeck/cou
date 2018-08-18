from random import choice, randrange
from city_engine.models import Residential, City, WaterTower, ProductionBuilding, WindPlant, DustCart, DumpingGround
from citizen_engine.models import Citizen


class CreateCitizen:
    def __init__(self, city, data):
        self.city = city
        self.data = data

    def create_with_workplace(self, workplace):
        workplace.employee.create(
            city=self.city,
            age=randrange(18, 60),
            income=10,
            health=10,
            resident=self.choose_residential()
        )

    def create_without_workplace(self):
        Citizen.objects.create(city=self.city,
                               age=randrange(18, 60),
                               income=10,
                               health=10,
                               resident=self.choose_residential())

    def choose_residential(self):
        return choice([r for r in self.data.list_of_buildings if isinstance(r, Residential)
                       and r.max_population >= r.population])
        # return choice([residential for residential in Residential.objects.filter(city=city)
        #                if residential.max_population >= residential.population])
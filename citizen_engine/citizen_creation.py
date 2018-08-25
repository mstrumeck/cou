from random import choice, randrange
from city_engine.models import Residential, City, WaterTower, ProductionBuilding, WindPlant, DustCart, DumpingGround
from citizen_engine.models import Citizen


class CreateCitizen:
    def __init__(self, city, data):
        self.city = city
        self.data = data

    def create_with_workplace(self, workplace):
        Citizen.objects.create(
            city=self.city,
            age=randrange(18, 60),
            health=10,
            month_of_birth=randrange(1, 12),
            resident_object=self.choose_residential(),
            workplace_object=workplace,
            sex=choice(Citizen.SEX)[0],
            father_id=0,
            mother_id=0
        )

    def create_without_workplace(self):
        Citizen.objects.create(
            city=self.city,
            age=randrange(18, 60),
            health=10,
            month_of_birth=randrange(1, 12),
            resident_object=self.choose_residential(),
            sex=choice(Citizen.SEX)[0],
            father_id=0,
            mother_id=0
        )

    def choose_residential(self):
        return choice([r for r in self.data.list_of_buildings if isinstance(r, Residential)
                       and r.max_population >= r.population])
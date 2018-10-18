from random import choice, randrange
from city_engine.models import Residential, City, WaterTower, ProductionBuilding, WindPlant, DustCart, DumpingGround
from citizen_engine.models import Citizen, Profession
import random
import string


class CreateCitizen:
    def __init__(self, city, data):
        self.city = city
        self.data = data

    def create_with_workplace(self, workplace, edu_title):
        c = Citizen.objects.create(
            city=self.city,
            age=randrange(18, 60),
            name="".join([random.choice(string.ascii_letters) for x in range(5)]),
            surname="".join([random.choice(string.ascii_letters) for x in range(5)]),
            health=10,
            month_of_birth=randrange(1, 12),
            resident_object=self.choose_residential(),
            workplace_object=workplace,
            sex=choice(Citizen.SEX)[0],
            edu_title=edu_title,
            father_id=0,
            mother_id=0
        )
        Profession.objects.create(citizen=c, name=workplace.profession_type_provided, cur_level=1.00)

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
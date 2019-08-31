import random
import string
from random import choice, randrange

from citizen_engine.models import Citizen, Profession, Family, Education
from city_engine.models import Residential
from cou.global_var import ELEMENTARY, COLLEGE, PHD


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
            health=0.5,
            month_of_birth=randrange(1, 12),
            resident_object=self.choose_residential(),
            workplace_object=workplace,
            sex=choice(Citizen.SEX)[0],
            edu_title=edu_title,
            father_id=0,
            mother_id=0,
        )
        if edu_title == ELEMENTARY:
            Education.objects.create(
                citizen=c, name=ELEMENTARY, effectiveness=1, if_current=False
            )
        elif edu_title == COLLEGE:
            Education.objects.create(
                citizen=c, name=ELEMENTARY, effectiveness=1, if_current=False
            )
            Education.objects.create(
                citizen=c, name=COLLEGE, effectiveness=1, if_current=False
            )
        elif edu_title == PHD:
            Education.objects.create(
                citizen=c, name=ELEMENTARY, effectiveness=1, if_current=False
            )
            Education.objects.create(
                citizen=c, name=COLLEGE, effectiveness=1, if_current=False
            )
            Education.objects.create(
                citizen=c, name=PHD, effectiveness=1, if_current=False
            )

        Profession.objects.create(
            citizen=c,
            name=workplace.profession_type_provided,
            proficiency=1.00,
            education=edu_title,
        )
        Family.objects.create(surname=c.surname, city=self.city)

    def create_without_workplace(self):
        c = Citizen.objects.create(
            city=self.city,
            age=randrange(18, 60),
            health=0.5,
            month_of_birth=randrange(1, 12),
            resident_object=self.choose_residential(),
            sex=choice(Citizen.SEX)[0],
            father_id=0,
            mother_id=0,
        )
        Family.objects.create(surname=c.surname, city=self.city)

    def choose_residential(self):
        return choice(
            [
                r
                for r in self.data.list_of_buildings
                if isinstance(r, Residential) and r.max_population >= r.population
            ]
        )

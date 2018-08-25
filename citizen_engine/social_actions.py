from citizen_engine.citizen_abstract import CitizenAbstract
from citizen_engine.models import Citizen
import random, string


class SocialAction:
    def __init__(self, city, profile):
        self.city = city
        self.profile = profile
        self.data = CitizenAbstract(self.city, self.profile)

    def run(self):
        self.match_marriages()
        self.born_child()
        self.save_all()

    def save_all(self):
        for c in self.data.citizens_in_city:
            c.save()

    def match_marriages(self):
        males = [m for m in self.data.mature_males if m.partner_id == 0]
        if males is not None:
            females = [m for m in self.data.mature_females if m.partner_id == 0]
            random.shuffle(males)
            random.shuffle(females)
            for m, f in zip(males, females):
                if random.random() < self.data.chance_to_marriage[m.age] \
                        and random.random() < self.data.chance_to_marriage[f.age]:
                        f.partner_id = m.id
                        m.partner_id = f.id
                        f.surname = m.surname
            self.data.create_and_return_pairs_in_city()

    def born_child(self):
        for family in self.data.pairs_in_city:
            ml = self.data.pairs_in_city[family]['Ml']
            fl = self.data.pairs_in_city[family]['Fl']
            if random.random() < self.data.chance_to_born[ml.age] \
                    and random.random() < self.data.chance_to_born[fl.age]:
                Citizen.objects.create(
                    city=self.city,
                    age=0,
                    month_of_birth=self.profile.current_turn,
                    cash=0,
                    health=5,
                    name="".join([random.choice(string.ascii_letters) for x in range(5)]),
                    surname=ml.surname,
                    sex=random.choice(Citizen.SEX)[0],
                    father_id=fl.id,
                    mother_id=ml.id,
                    resident_object_id=ml.resident_object_id
                )
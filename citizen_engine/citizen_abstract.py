from citizen_engine.models import Citizen


class CitizenAbstract:
    def __init__(self, city, profile):
        self.city = city
        self.profile = profile
        self.citizens_in_city = Citizen.objects.filter(city=self.city)
        self.mature_males = [p for p in self.citizens_in_city
                             if p.sex == Citizen.MALE and p.age > 17]
        self.mature_females = [p for p in self.citizens_in_city
                               if p.sex == Citizen.FEMALE and p.age > 17]
        self.chance_to_marriage = self.chance_to_marriage_calc()
        self.chance_to_born = self.chance_to_born_baby_calc()

    def get_partner(self, m):
        for f in self.mature_females:
            if m.id == f.partner_id:
                return f
        return None

    def create_and_return_pairs_in_city(self):
        self.pairs_in_city = {m.surname: {m.sex: self.get_partner(m), self.get_partner(m).sex: m} for m in self.mature_males
                              if self.get_partner(m) is not None}

    def create_and_return_families_in_city(self):
        self.families_in_city = {pair: {**self.pairs_in_city[pair],
                                        **{"ch-{}".format(ch.id): ch for ch in self.citizens_in_city
                                           if ch.father_id == self.pairs_in_city[pair]['Ml'].id
                                           and ch.mother_id == self.pairs_in_city[pair]['Fl'].id
                                           and ch.partner_id == 0}}
                                 for pair in self.pairs_in_city}


    def chance_to_born_baby_calc(self):
        chance_to_born = {}
        chance_copy = self.profile.chance_to_born_baby_percent
        for x in range(18, 61):
            if x > 17 and x < 22:
                chance_to_born[x] = chance_copy
            else:
                if chance_copy > 0:
                    chance_copy -= 0.03
                    chance_to_born[x] = chance_copy
                else:
                    chance_to_born[x] = 0
        return chance_to_born

    def chance_to_marriage_calc(self):
        chance_copy = self.profile.chance_to_marriage_percent
        chance_to_marriage = {}
        for x in range(18, 61):
            if x > 17 and x < 24:
                chance_to_marriage[x] = chance_copy
            else:
                if chance_copy > 0:
                    chance_copy -= 0.02
                    chance_to_marriage[x] = chance_copy
                else:
                    chance_to_marriage[x] = 0
        return chance_to_marriage
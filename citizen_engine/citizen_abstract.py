from cou.global_var import MALE, FEMALE


class CitizenAbstract:
    def __init__(self, city, profile, city_data):
        self.city = city
        self.profile = profile
        self.citizens_in_city = city_data.citizens_in_city
        self.families = city_data.families
        self.mature_males = [p for p in self.citizens_in_city
                             if p.sex == MALE and p.age > 17]
        self.mature_females = [p for p in self.citizens_in_city
                               if p.sex == FEMALE and p.age > 17]
        self.matures = [p for p in self.citizens_in_city if p.age > 17]
        self.chance_to_marriage = self.chance_to_marriage_calc()
        self.chance_to_born = self.chance_to_born_baby_calc()

    def get_partner(self, m):
        for f in self.mature_females:
            if m.id == f.partner_id:
                return f
        return None

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

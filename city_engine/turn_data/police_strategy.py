from cou.global_var import CRIMINAL
from city_engine.temp_models import TempPoliceStation, TempPrison
import random
import decimal


class PoliceStrategy:
    def __init__(self, data):
        self.data = data

    def calculate_criminals_vs_police_in_city(self):
        criminals = self._get_active_criminals()
        for criminal in criminals:
            target = random.choice([b for b in self.data.list_of_buildings.values() if not isinstance(b, TempPrison)])
            if criminal.current_profession.proficiency >= target.criminal_prevention:
                self._robbery_succeed(criminal)
            else:
                self._robbery_failed(criminal)

    def _robbery_succeed(self, criminal):
        loot = criminal.salary_expectation * 3
        criminal.instance.cash += decimal.Decimal(loot)
        self.data.city.cash -= decimal.Decimal(loot)
        criminal.current_profession.update_proficiency(criminal)

    def _robbery_failed(self, criminal):
        if random.random() > criminal.current_profession.proficiency * 0.10:
            prisons = self._get_prisons_with_free_places()
            if prisons:
                prisons[-1].put_criminal_to_jail(criminal)

    def apply_crime_prevention_in_city(self):
        police_stations = (pc for pc in self.data.list_of_buildings.values() if isinstance(pc, TempPoliceStation))
        for police_station in police_stations:
            police_station.ensure_crime_prevention(self.data.list_of_buildings)

    def calculate_probability_of_become_criminal(self):
        for c in self.data.citizens_in_city.values():
            if c.is_become_a_criminal():
                c.change_citizen_into_criminal()

    def _get_active_criminals(self):
        return (cr for cr in self.data.citizens_in_city.values()
                if cr.current_profession.name == CRIMINAL)

    def _get_prisons_with_free_places(self):
        return [pr for pr in self.data.list_of_buildings.values() if isinstance(pr, TempPrison) and pr.is_has_place()]

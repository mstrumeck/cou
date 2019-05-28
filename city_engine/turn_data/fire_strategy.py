import random

from city_engine.temp_models import TempFireStation


class FireStrategy:
    def __init__(self, data):
        self.data = data

    def _get_building_neighbourhood(self, build):
        return [b for b in self.data.list_of_buildings.values()
                if abs(build.row_col_cor[0] - b.row_col_cor[0]) <= 1
                and abs(build.row_col_cor[1] - b.row_col_cor[1]) <= 1]

    def _get_building_distance(self, building_a, building_b):
        return max([building_a.row_col_cor[0] - building_b.row_col_cor[0], building_a.row_col_cor[1] - building_b.row_col_cor[1]])

    def _fight_with_fire(self, fs, b, distance):
        chances = random.randrange(distance, 6)
        for ch in range(chances):
            if fs.is_handle_with_fire():
                b.is_in_fire = False
                return
            else:
                if self._is_fire_spread_too_much(ch):
                    target_b_from_n = random.choice(self._get_building_neighbourhood(b))
                    target_b_from_n.set_in_fire()

                    if b.all_people_in_building:
                        target_p = random.choice(b.all_people_in_building)
                        if random.random() > 0.25:
                            target_p.probability_of_being_sick()
                        else:
                            self.data.kill_person(target_p)
        self.data.destroy_building(b)

    def _is_fire_spread_too_much(self, chance):
        return True if random.random() < chance * 0.10 else False

    def _get_nearest_buildings_in_fire_for_fire_station(self, fs):
        return sorted([b for b in self.data.list_of_buildings.values() if b.is_in_fire], key=lambda x: (
                abs(x.row_col_cor[0] - fs.row_col_cor[0]),
                abs(x.row_col_cor[1] - fs.row_col_cor[1])))

    def simulate_fire_in_the_city(self):
        fire_stations = [b for b in self.data.list_of_buildings.values() if isinstance(b, TempFireStation)]
        for fs in fire_stations:
            pattern = self._get_nearest_buildings_in_fire_for_fire_station(fs)
            while fs.fire_prevention_capacity and pattern:
                target = pattern[-1]
                distance_to_target = self._get_building_distance(fs, target)
                self._fight_with_fire(fs, target, distance_to_target)
                pattern = self._get_nearest_buildings_in_fire_for_fire_station(fs)

    def calculate_probability_of_fire_among_the_all_buildings(self):
        for b in [b for b in self.data.list_of_buildings.values() if not isinstance(b, TempFireStation)]:
            b.probability_of_fire()

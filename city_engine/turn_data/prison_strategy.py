from city_engine.models import Prison
from city_engine.temp_models import TempPrison


class PrisonStrategy:
    def __init__(self, data):
        self.data = data

    def _get_prisons_with_free_places(self):
        return (pr for pr in self.data.list_of_buildings.values() if isinstance(pr, TempPrison) and pr.is_has_place())

    def _get_prisons_with_prisoners(self):
        return (pr for pr in self.data.list_of_buildings.values() if isinstance(pr, TempPrison) and pr.num_of_prisoners)


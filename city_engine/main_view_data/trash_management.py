from django.db.models import F

from city_engine.models import DumpingGround


class TrashManagement:
    def __init__(self, data):
        self.data = data

    def run(self):
        self.generate_trash()
        self.update_trash_time()

    def generate_trash(self):
        for building in (b for b in self.data.list_of_buildings if not isinstance(b, DumpingGround)):
            tc = building.trash_calculation(self.data.list_of_buildings[building].people_in_charge)
            if tc > 0:
                building.trash.create(size=tc)

    def update_trash_time(self):
        for building in self.data.list_of_buildings:
            building.trash.update(time=F("time") + 1)

    def list_of_all_trashes_in_city(self):
        result = []
        for building in self.data.list_of_buildings:
            for trash in self.data.list_of_buildings[building].trash:
                result.append(trash)
        return result


class CollectGarbage:
    def __init__(self, city, data):
        self.city = city
        self.data = data

    def existing_dumping_grounds_with_slots(self):
        return (self.data.list_of_buildings[dg] for dg in self.data.list_of_buildings if isinstance(dg, DumpingGround)
                and dg.max_space_for_trash > dg.current_space_for_trash)

    def run(self):
        buildings_with_trash = {
            self.data.list_of_buildings[b].row_col_cor: self.data.list_of_buildings[b] for b in self.data.list_of_buildings
            if not isinstance(b, DumpingGround)
        }
        for dg in self.existing_dumping_grounds_with_slots():
            pattern = sorted(buildings_with_trash,
                             key=lambda x: (abs(x[0] - dg.row_col_cor[0]), abs(x[1] - dg.row_col_cor[1])))
            guard = 0
            while dg.current_capacity < dg.instance.max_space_for_trash and guard < len(pattern):
                target = pattern[guard]
                dg.collect_trash(buildings_with_trash[target])
                guard += 1
            dg.instance.current_space_for_trash = dg.current_capacity

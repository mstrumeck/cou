from city_engine.temp_models import TempDumpingGround
import itertools


class TrashManagement:
    def __init__(self, data):
        self.data = data

    def run(self):
        self.generate_trash()
        self.update_trash_time()

    def generate_trash(self):
        for building in (b for b in list(itertools.chain(self.data.list_of_buildings.values(), self.data.list_of_trade_districts.values())) if not isinstance(b, TempDumpingGround)):
            building.create_trash()

    def update_trash_time(self):
        for building in self.data.list_of_buildings.values():
            for t in building.trash:
                t.time += 1

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

    def move_temp_trash_to_perm(self):
        for building in (b for b in list(self.data.list_of_buildings.values()) + list(self.data.list_of_trade_districts.values()) if not isinstance(b, TempDumpingGround)):
            building.convert_temp_trash_to_perm()

    def existing_dumping_grounds_with_slots(self):
        return (dg for dg in self.data.list_of_buildings.values() if isinstance(dg, TempDumpingGround)
                and dg.instance.max_space_for_trash > dg.instance.current_space_for_trash)

    def run(self):
        buildings_with_trash = {
            b.row_col_cor: b for b in self.data.list_of_buildings.values()
            if not isinstance(b, TempDumpingGround)
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
        self.move_temp_trash_to_perm()

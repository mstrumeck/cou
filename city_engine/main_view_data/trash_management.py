from django.db.models import F

from city_engine.models import DumpingGround, DustCart


class TrashManagement:
    def __init__(self, data):
        self.data = data

    def run(self):
        self.generate_trash()
        self.update_trash_time()

    def generate_trash(self):
        for building in (
            b for b in self.data.list_of_buildings if not isinstance(b, DumpingGround)
        ):
            tc = building.trash_calculation(
                self.data.list_of_buildings[building].people_in_charge
            )
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
        return (
            dg
            for dg in self.data.list_of_buildings
            if isinstance(dg, DumpingGround)
            and dg.max_space_for_trash > dg.current_space_for_trash
        )

    def existing_dust_carts(self, dg):
        return (
            dc
            for dc in self.data.vehicles
            if isinstance(dc, DustCart) and dc.dumping_ground == dg
        )

    def max_capacity_of_cart(self, dc):
        return dc.max_capacity * dc.employee_productivity(
            self.data.vehicles, self.data.citizens_in_city
        )

    def unload_trashes_from_cart(self, dc, dg):
        while (
            dg.max_space_for_trash >= dg.current_space_for_trash
            and dc.curr_capacity > 0
        ):
            dg.current_space_for_trash += 1
            dc.curr_capacity -= 1

    def collect_trash_by_dust_cart(self, dc, dc_max_capacity, building):
        for trash in self.data.list_of_buildings[building].trash:
            while dc_max_capacity >= dc.curr_capacity and trash.size > 0:
                dc.curr_capacity += 1
                trash.size -= 1
            trash.delete()

    def run(self):
        buildings_with_trash = {
            self.data.list_of_buildings[b].row_col_cor: b
            for b in self.data.list_of_buildings
            if not isinstance(b, DumpingGround)
        }
        for dg in self.existing_dumping_grounds_with_slots():
            for dc in self.existing_dust_carts(dg):
                pattern = sorted(
                    buildings_with_trash,
                    key=lambda x: (
                        abs(x[0] - self.data.list_of_buildings[dg].row_col_cor[0]),
                        abs(x[1] - self.data.list_of_buildings[dg].row_col_cor[1]),
                    ),
                )
                guard = 0
                max_capcity = self.max_capacity_of_cart(dc)
                while dc.curr_capacity < max_capcity and guard < len(pattern):
                    target = pattern[guard]
                    self.collect_trash_by_dust_cart(
                        dc, max_capcity, buildings_with_trash[target]
                    )
                    guard += 1
                self.unload_trashes_from_cart(dc, dg)

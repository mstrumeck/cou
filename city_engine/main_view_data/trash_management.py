from city_engine.models import DumpingGround, DustCart, CityField, Building
from django.db.models import F
from city_engine.abstract import RootClass
from city_engine.main_view_data.allocation_pattern import AllocationPattern


class TrashManagement(object):

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def run(self):
        self.generate_trash()
        self.update_trash_time()

    def generate_trash(self):
        for building in self.data.list_of_building_in_city_excluding(DumpingGround):
            if building.trash_calculation() > 0:
                building.trash.create(size=building.trash_calculation())

    def update_trash_time(self):
        for building in self.data.list_of_buildings:
            building.trash.update(time=F('time')+1)

    def list_of_all_trashes_in_city(self):
        result = []
        for building in self.data.list_of_buildings:
            for trash in building.trash.all():
                result.append(trash)
        return result


class CollectGarbage(object):

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def existing_dumping_grounds_with_slots(self):
        if DumpingGround.objects.filter(city=self.city).exists():
            return [dg for dg in DumpingGround.objects.filter(city=self.city) if dg.max_space_for_trash > dg.current_space_for_trash]
        return []

    def existing_dust_carts(self, dg):
        if DustCart.objects.filter(dumping_ground=dg).exists():
            return [dc for dc in DustCart.objects.filter(dumping_ground=dg)]
        return []

    def city_field_from_corr(self, corr):
        if CityField.objects.filter(city=self.city, row=corr[0], col=corr[1]).exists():
            return CityField.objects.get(city=self.city, row=corr[0], col=corr[1])
        return None

    def search_building_with_corr(self, city_field):
        for building_model in self.data.subclasses_of_all_buildings:
            if building_model.objects.filter(city_field=city_field).exists():
                return building_model.objects.get(city_field=city_field)

    def list_of_trash_for_building(self, building):
        if building.trash.all().exists():
            return [trash for trash in building.trash.all()]
        return []

    def collect_trash_by_dust_cart(self, dc, next_corr):
        if self.city_field_from_corr(next_corr):
            city_field = self.city_field_from_corr(next_corr)
            if self.search_building_with_corr(city_field):
                building = self.search_building_with_corr(city_field)
                if self.list_of_trash_for_building(building):
                    for trash in self.list_of_trash_for_building(building):
                        if dc.curr_capacity < self.max_capacity_of_cart(dc):
                            dc.curr_capacity = F('curr_capacity') + trash.size
                            dc.save()
                            dc.refresh_from_db()
                            trash.delete()

    def max_capacity_of_cart(self, dc):
        return dc.max_capacity * dc.effectiveness()

    def unload_trashes_from_cart(self, dc, dg):
        dg.current_space_for_trash = F('current_space_for_trash') + dc.curr_capacity
        dc.curr_capacity = 0
        dg.save()
        dc.save()
        dg.refresh_from_db()

    def run(self):
        for dg in self.existing_dumping_grounds_with_slots():
            for dc in self.existing_dust_carts(dg):
                pattern = AllocationPattern().create_allocation_pattern(dg.city_field.row, dg.city_field.col)
                while dc.curr_capacity < self.max_capacity_of_cart(dc):
                    try:
                        root = next(pattern)
                    except(StopIteration):
                        break
                    for corr in root:
                        self.collect_trash_by_dust_cart(dc, corr)
                self.unload_trashes_from_cart(dc, dg)
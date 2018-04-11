from city_engine.models import list_of_models, DumpingGround, DustCart, CityField, Building
from django.db.models import F
from city_engine.abstract import RootClass
from city_engine.main_view_data.allocation_pattern import AllocationPattern


class TrashManagement(RootClass):

    def run(self):
        self.generate_trash()
        self.update_trash_time()

    def generate_trash(self):
        for building in self.list_of_building_in_city_excluding(DumpingGround):
            if building.trash_calculation() > 0:
                building.trash.create(size=building.trash_calculation())

    def update_trash_time(self):
        for building in self.list_of_buildings_in_city():
            building.trash.update(time=F('time')+1)

    def list_of_all_trashes_in_city(self):
        result = []
        for building in self.list_of_buildings_in_city():
            for trash in building.trash.all():
                result.append(trash)
        return result


class CollectGarbage(RootClass):

    def collect_garbage(self):
        if DumpingGround.objects.filter(city=self.city).exists():
            for dumping_ground in DumpingGround.objects.filter(city=self.city):
                if dumping_ground.max_space_for_trash > dumping_ground.current_space_for_trash:
                    for dust_cart in DustCart.objects.filter(dumping_ground=dumping_ground):
                        allocation_pattern = AllocationPattern()
                        pattern = allocation_pattern.create_allocation_pattern(dumping_ground.city_field.row, dumping_ground.city_field.col)
                        while dust_cart.curr_capacity < (dust_cart.max_capacity * dust_cart.effectiveness()):
                            try:
                                next_value = next(pattern)
                            except(StopIteration):
                                break
                            for field in next_value:
                                if CityField.objects.filter(city=self.city, row=field[0], col=field[1]).exists():
                                    city_field_of_target = CityField.objects.filter(city=self.city, row=field[0], col=field[1])
                                    for building_model in self.get_subclasses(abstract_class=Building, app_label='city_engine'):
                                        if building_model.objects.filter(city_field=city_field_of_target).exists():
                                            building_with_trash = building_model.objects.get(city_field=city_field_of_target)
                                            if building_with_trash.trash.all().exists():
                                                for trash in building_with_trash.trash.all():
                                                    if dust_cart.curr_capacity < (dust_cart.max_capacity * dust_cart.effectiveness()):
                                                        dust_cart.curr_capacity += trash.size
                                                        dust_cart.save()
                                                        trash.delete()
                        dumping_ground.current_space_for_trash += dust_cart.curr_capacity
                        dust_cart.curr_capacity = 0
                        dumping_ground.save()
                        dust_cart.save()
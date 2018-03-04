from city_engine.models import CityField, City, \
    Residential, \
    ProductionBuilding, \
    WindPlant, CoalPlant, RopePlant, WaterTower, \
    electricity_buildings, waterworks_buildings, \
    list_of_models, list_of_buildings_categories
from random import shuffle
import numpy as np


def assign_city_fields_to_board(city):
    fields = [x for x in range(1, int(Board.HEX_NUM)+1)]
    chunk_fields = np.array_split(fields, Board.HEX_NUM_IN_ROW)
    for num_of_row, row in enumerate(chunk_fields):
        row = list(row)
        for col in range(len(row)):
            CityField.objects.create(city=city, row=num_of_row, col=col).save()


class Board(object):
    ROW_NUM = 4
    HEX_NUM = 16
    HEX_NUM_IN_ROW = HEX_NUM / ROW_NUM

    def __init__(self, city):
        self.hex_table = ''
        self.city = city
        self.hex_with_builds = []
        self.hex_with_electricity = []
        self.hex_with_waterworks = []
        ResourceAllocation(self.city)
        self.map_board_info()
        self.generate_board()

    def generate_board(self):
        for row in range(self.ROW_NUM):
            if row % 2 == 0:
                self.hex_table += "<div class='hex-row even'>"
            elif row % 2 != 0:
                self.hex_table += "<div class='hex-row'>"
            for col in range(int(self.HEX_NUM_IN_ROW)):
                self.hex_table += Hex(row, col, self.hex_with_builds,
                                      self.hex_with_electricity,
                                      self.hex_with_waterworks).create()
            self.hex_table += "</div>"

    def map_board_info(self):
        for row in range(int(Board.ROW_NUM)):
            for col in range(int(Board.HEX_NUM_IN_ROW)):
                if CityField.objects.filter(col=col, row=row, city=self.city):
                    build_field = CityField.objects.get(col=col, row=row, city=self.city)
                    if build_field.if_residential is True:
                        self.hex_with_builds.append((row, col))
                    elif build_field.if_production is True:
                        self.hex_with_builds.append((row, col))
                    elif build_field.if_electricity is True:
                        self.hex_with_builds.append((row, col))
                        self.hex_with_electricity.append((row, col))
                    elif build_field.if_waterworks is True:
                        self.hex_with_builds.append((row, col))
                        self.hex_with_waterworks.append((row, col))


class Hex(object):
    def __init__(self, row, col, hex_with_builds, hex_with_electricity, hex_with_waterworks):
        self.col = col
        self.row = row
        self.hex_with_builds = hex_with_builds
        self.hex_with_electricity = hex_with_electricity
        self.hex_with_waterworks = hex_with_waterworks
        self.hexagon = ''

    def create(self):
        self.hexagon = "<div class='hexagon"
        if (self.row, self.col) in self.hex_with_builds:
            self.hexagon += " build'"
        else:
            self.hexagon += "'"
        self.hexagon += "id='{}{}'".format(self.row, self.col)
        self.hexagon += ">"
        self.hexagon += "<div class='hexagon-top'></div>"
        self.hexagon += "<div class='hexagon-middle'>"

        if (self.row, self.col) in self.hex_with_electricity:
            self.hexagon += "<p>Prąd</p>"
        elif (self.row, self.col) in self.hex_with_waterworks:
            self.hexagon += "<p>Wodociągi</p>"

        self.hexagon += "<p>{},{}</p>".format(self.row, self.col)
        self.hexagon += "</div>"
        self.hexagon += "<div class='hexagon-bottom'></div>"
        self.hexagon += "</div>"
        return self.hexagon


class HexDetail(object):
    def __init__(self, city):
        self.city = city
        self.hex_detail_info_table = ''
        self.generate_hex_detail()

    def generate_hex_detail(self):
        counter = 0
        for row in range(int(Board.ROW_NUM)):
            for col in range(int(Board.HEX_NUM_IN_ROW)):
                counter += 1
                self.hex_detail_info_table += self.add_hex_detail_box(counter, row, col)
        return self.hex_detail_info_table

    def add_hex_detail_box(self, hex_id, row, col):
        hex_detail_box = "<div class='hexInfoBoxDetail' "
        hex_detail_box += "id='hexBox{}{}'>".format(row, col)
        hex_detail_box += "<p>Podgląd hexa "+str(hex_id)+"</p>"

        if CityField.objects.filter(row=row, col=col, city=self.city):
            build_field = CityField.objects.get(row=row, col=col, city=self.city)
            hex_detail_box += "<p>Zanieczyszczenie: {}</p>".format(build_field.pollution)

            if build_field.if_residential is True:
                residential = Residential.objects.get(city_field=build_field.id, city=self.city)
                hex_detail_box += '<p>Budynek mieszkalny</p>' \
                                  '<p>Populacja: '+str(residential.current_population)+'</p>'

            elif build_field.if_production is True:
                production = ProductionBuilding.objects.get(city_field=build_field.id, city=self.city)
                hex_detail_box += '<p>Budynek produkcyjny</p>' \
                                  '<p>Pracownicy: '+str(production.current_employees)+'/'+str(production.max_employees)+'</p>'

            elif build_field.if_electricity is True:
                hex_detail_box += self.add_build_details(build_field, electricity_buildings)

            elif build_field.if_waterworks is True:
                hex_detail_box += self.add_build_details(build_field, waterworks_buildings)

        hex_detail_box += "</div>"
        return hex_detail_box

    def add_build_details(self, build_field, list_of_buildings):
        hex_detail_box = ''
        for building in list_of_buildings:
            if building.objects.filter(city_field=build_field.id, city=self.city).count() == 1:
                build = building.objects.get(city_field=build_field.id, city=self.city)
                hex_detail_box = '<p name="detailName">'+str(build.name)+'</p>'
                hex_detail_box += '<p name="detailEmployees">Pracownicy: '+str(build.current_employees)+'/'+str(build.max_employees)+'</p>'
                if build_field.if_electricity is True:
                    hex_detail_box += self.add_electricity_details(build)
                elif build_field.if_waterworks is True:
                    hex_detail_box += self.add_waterworks_details(build)
        return hex_detail_box

    def add_electricity_details(self, build):
        hex_detail_box = ''
        hex_detail_box += '<p name="detailEnergy">Produkowana energia: ' + str(build.total_production()) + '</p>'
        hex_detail_box += '<p>Zalokowana energia: ' + str(build.energy_allocated)+'</p>'
        if build is WindPlant:
            hex_detail_box += '<p>Liczba turbin: '
        else:
            hex_detail_box += '<p>Liczba reaktorów: '
            hex_detail_box += str(build.power_nodes)+'/'+str(build.max_power_nodes)+'</p>'
        hex_detail_box += '<p>Woda: '+str(build.water)+'/'+str(build.water_required)+'</p>'
        hex_detail_box += '<p>if_ele_city_field = '+str(build.city_field.if_electricity)+'</p>'
        hex_detail_box += '<p>if_ele_build = '+str(build.if_electricity)+'</p>'
        return hex_detail_box

    def add_waterworks_details(self, build):
        hex_detail_box = ''
        hex_detail_box += '<p name="detailWater">Pompowana woda: '+str(build.total_production())+'</p>'
        hex_detail_box += '<p>Energia: '+str(build.energy)+'/'+str(build.energy_required)+'</p>'
        hex_detail_box += '<p>Woda allocated: '+str(build.water_allocated)+'</p>'
        return hex_detail_box


class ResourceAllocation(object):
    def __init__(self, city):
        self.city = city
        self.clean_city_field_data()
        self.clean_resource_data()
        self.all_resource_allocation()
        self.pollution_allocation()

    def create_allocation_pattern(self, row, col):
        first_alloc = []
        for hex_in_row in range(1, int(Board.HEX_NUM_IN_ROW+1)):
            allocation_pattern = [
                (row - hex_in_row, col),
                (row - hex_in_row, col + hex_in_row),
                (row + hex_in_row, col),
                (row + hex_in_row, col + hex_in_row),
                (row, col - hex_in_row),
                (row, col + hex_in_row)
            ]
            for calculations in allocation_pattern:
                if calculations[0] >= 0 or calculations[1] >= 0:
                    first_alloc.append(calculations)
            shuffle(first_alloc)
            yield first_alloc
            first_alloc = []
            yield self.return_next_alloc(hex_in_row, hex_in_row+1, row, col)

    def return_next_alloc(self, hex_in_row, wave, row, col):
        allocation = []
        allocation_pattern = [
            (row + hex_in_row, col - hex_in_row + wave),
            (row + hex_in_row, col + hex_in_row - wave),
            (row - hex_in_row, col + hex_in_row - wave),
            (row - hex_in_row, col - hex_in_row + wave)
        ]
        for calculation in allocation_pattern:
            if calculation[0] >= 0 or calculation[1] >= 0:
                allocation.append(calculation)
        shuffle(allocation)
        return allocation

    def return_first_allocation(self, row, col):
        alloc = []
        hex_in_row = 1
        allocation_pattern = [
            (row - hex_in_row, col),
            (row - hex_in_row, col + hex_in_row),
            (row + hex_in_row, col),
            (row + hex_in_row, col + hex_in_row),
            (row, col - hex_in_row),
            (row, col + hex_in_row)
        ]
        for calculations in allocation_pattern:
            if calculations[0] >= 0 or calculations[1] >= 0:
                alloc.append(calculations)
        shuffle(alloc)
        return alloc

    def clean_city_field_data(self):
        for field in CityField.objects.filter(city=self.city):
            field.pollution = 0
            field.save()

    def clean_resource_data(self):
        for models in list_of_models:
            list_of_buildings = models.objects.filter(city=self.city)
            for building in list_of_buildings:
                building.energy = 0
                building.water = 0
                building.save()

    def all_resource_allocation(self):
        for building_category in list_of_buildings_categories:
            for models in building_category:
                list_of_buildings = models.objects.filter(city=self.city)
                for building in list_of_buildings:
                    building.resources_allocation_reset()
                    building.save()
                    pattern = self.create_allocation_pattern(building.city_field.row, building.city_field.col)
                    while building.producted_resources_allocation() < building.total_production():
                        try:
                            next_value = next(pattern)
                        except(StopIteration):
                            break
                        for field in next_value:
                            if CityField.objects.filter(city=self.city, row=field[0], col=field[1]):
                                city_field_for_building = CityField.objects.get(city=self.city, row=field[0], col=field[1])
                                if city_field_for_building.if_electricity is False and building.if_electricity is True:
                                    self.energy_allocation(building, city_field_for_building)
                                elif city_field_for_building.if_waterworks is False and building.if_waterworks is True:
                                    self.water_allocation(building, city_field_for_building)

    def energy_allocation(self, building, city_field_of_building):
        energy_left = building.total_production() - building.energy_allocated
        if city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
            for building_type in city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
                if building_type.objects.filter(city_field=city_field_of_building, city=self.city,
                                                if_electricity=False):
                    target_build = building_type.objects.get(city_field=city_field_of_building, city=self.city,
                                                             if_electricity=False)
                    energy_to_fill = target_build.energy_required - target_build.energy
                    if energy_left > energy_to_fill:
                        building.energy_allocated += energy_to_fill
                        target_build.energy += energy_to_fill
                    elif energy_left < energy_to_fill:
                        building.energy_allocated += energy_left
                        target_build.energy += energy_left
                    target_build.save()
                    building.save()

    def water_allocation(self, building, city_field_of_building):
        water_left = building.total_production() - building.water_allocated
        if city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
            for building_type in city_field_of_building.return_list_of_possible_buildings_related_with_type_of_field():
                if building_type.objects.filter(city_field=city_field_of_building, city=self.city, if_waterworks=False):
                    target_build = building_type.objects.get(city_field=city_field_of_building, city=self.city,
                                                             if_waterworks=False)
                    water_to_fill = target_build.water_required - target_build.water
                    if water_left > water_to_fill:
                        building.water_allocated += water_to_fill
                        target_build.water += water_to_fill
                    elif water_left < water_to_fill:
                        building.water_allocated += water_left
                        target_build.water += water_left
                    target_build.save()
                    building.save()

    def pollution_allocation(self):
        for field in CityField.objects.filter(city=self.city):
            if field.return_list_of_possible_buildings_related_with_type_of_field():
                for building in field.return_list_of_possible_buildings_related_with_type_of_field():
                    if building.objects.filter(city_field=field, city=self.city):
                        target_build = building.objects.get(city_field=field, city=self.city)
                        allocation_pattern = self.return_first_allocation(field.row, field.col)
                        for corr in allocation_pattern:
                            if CityField.objects.filter(city=self.city, row=corr[0], col=corr[1]):
                                target_city_field = CityField.objects.get(city=self.city, row=corr[0], col=corr[1])
                                target_city_field.pollution += (target_build.pollution_calculation() / len(allocation_pattern))
                                field.pollution += (target_build.pollution_calculation() / len(allocation_pattern))
                                target_city_field.save()
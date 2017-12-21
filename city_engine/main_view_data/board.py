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
        # self.allocate_resources()
        # ResourceAllocation(self.city)
        self.map_board_info()
        self.generate_board()

    def generate_board(self):
        counter = 0
        for row in range(self.ROW_NUM):
            if row % 2 == 0:
                self.hex_table += "<div class='hex-row even'>"
            elif row % 2 != 0:
                self.hex_table += "<div class='hex-row'>"
            for col in range(int(self.HEX_NUM_IN_ROW)):
                counter += 1
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
        if build is WindPlant:
            hex_detail_box += '<p>Liczba turbin: '
        else:
            hex_detail_box += '<p>Liczba reaktorów: '
            hex_detail_box += str(build.power_nodes)+'/'+str(build.max_power_nodes)+'</p>'
        hex_detail_box += '<p>Woda: '+str(build.water)+'/'+str(build.water_required)+'</p>'
        hex_detail_box += '<p>total_energy_allocation' +str(build.energy_allocated)+'</p>'
        hex_detail_box += '<p>if_ele '+str(build.city_field.if_electricity)+'</p>'
        return hex_detail_box

    def add_waterworks_details(self, build):
        hex_detail_box = ''
        hex_detail_box += '<p name="detailWater">Pompowana woda: '+str(build.total_production())+'</p>'
        hex_detail_box += '<p name="detailWater">Energia: '+str(build.energy)+'/'+str(build.energy_required)+'</p>'
        hex_detail_box += '<p>Woda allocated: '+str(build.water_allocated)+'</p>'
        return hex_detail_box


# class ResourceAllocation(object):
#     def __init__(self, city):
#         self.city = city
#         self.clean_resource_data()
#         self.water_allocation()
#         self.energy_allocation()
#         # self.allocate_resources()
#
#     def create_allocation_pattern(self, hex_id):
#         first_circle, second_circle, third_circle, fourth_circle = [], [], [], []
#         for x in range(1, int(Board.HEX_NUM_IN_ROW+1)):
#             first_calculations = [
#             hex_id + x,
#             hex_id + Board.HEX_NUM_IN_ROW + x,
#             hex_id + Board.HEX_NUM_IN_ROW,
#             hex_id + Board.HEX_NUM_IN_ROW - x,
#             hex_id - x,
#             hex_id - Board.HEX_NUM_IN_ROW - x,
#             hex_id - Board.HEX_NUM_IN_ROW,
#             hex_id - Board.HEX_NUM_IN_ROW + x,
#             ]
#             shuffle(first_calculations)
#             for result in first_calculations:
#                 if result > 0:
#                     first_circle.append(result)
#             yield first_circle
#             first_circle = []
#
#             if x >= 2:
#                 second_calculations = [
#                     hex_id + (x - x * Board.HEX_NUM_IN_ROW) - 1 - x,
#                     hex_id + (x - x * Board.HEX_NUM_IN_ROW) - x,
#                     hex_id + (x - x * Board.HEX_NUM_IN_ROW) + 1 - x,
#                     hex_id + (x + x * Board.HEX_NUM_IN_ROW) - 1 - x,
#                     hex_id + (x + x * Board.HEX_NUM_IN_ROW) - x,
#                     hex_id + (x + x * Board.HEX_NUM_IN_ROW) + 1 - x,
#                     hex_id + (x * Board.HEX_NUM_IN_ROW) - (2 - x) - x,
#                     hex_id - (x * Board.HEX_NUM_IN_ROW) - (2 - x) - x,
#                     hex_id + (x * Board.HEX_NUM_IN_ROW) + (2 + x) - x,
#                     hex_id - (x * Board.HEX_NUM_IN_ROW) + (2 + x) - x
#                 ]
#                 shuffle(second_calculations)
#                 for result in second_calculations:
#                     if result > 0:
#                         second_circle.append(result)
#                 yield second_circle
#                 second_circle = []
#
#                 if x % 2 == 0:
#                     third_calculations = [
#                         hex_id + (x * Board.HEX_NUM_IN_ROW) - 3,
#                        hex_id - (x * Board.HEX_NUM_IN_ROW) - 3,
#                         hex_id + (x * Board.HEX_NUM_IN_ROW) + 3,
#                         hex_id - (x * Board.HEX_NUM_IN_ROW) + 3,
#                     ]
#                     shuffle(third_calculations)
#                     for result in third_calculations:
#                         if result > 0:
#                             third_circle.append(result)
#                     yield third_circle
#                     third_circle = []
#
#                 elif x % 3 == 0:
#                     fourth_calculations = [
#                         hex_id + (x * Board.HEX_NUM_IN_ROW) - 3,
#                         hex_id - (x * Board.HEX_NUM_IN_ROW) - 3,
#                         hex_id + (x * Board.HEX_NUM_IN_ROW) + 3,
#                         hex_id - (x * Board.HEX_NUM_IN_ROW) + 3,
#                         hex_id + (x * Board.HEX_NUM_IN_ROW) - 4,
#                         hex_id - (x * Board.HEX_NUM_IN_ROW) - 4,
#                         hex_id + (x * Board.HEX_NUM_IN_ROW) + 4,
#                         hex_id - (x * Board.HEX_NUM_IN_ROW) + 4
#                     ]
#                     shuffle(fourth_calculations)
#                     for result in fourth_calculations:
#                         if result > 0:
#                             fourth_circle.append(result)
#                     yield fourth_circle
#                     fourth_circle = []
#
#     def clean_resource_data(self):
#         for models in list_of_models:
#             list = models.objects.filter(city=self.city)
#             for building in list:
#                 building.energy = 0
#                 building.water = 0
#                 building.save()
#
#     def energy_allocation(self):
#         for models in electricity_buildings:
#             list_of_buildings = models.objects.filter(city=self.city)
#             for building in list_of_buildings:
#                 building.energy_allocated = 0
#                 building.save()
#                 pattern = self.create_allocation_pattern(building.city_field.id)
#                 while building.energy_allocated < building.total_production():
#                     try:
#                         next_value = next(pattern)
#                     except(StopIteration):
#                         break
#                     for field in next_value:
#                         if CityField.objects.filter(city=self.city, field_id=field):
#                             if CityField.objects.get(city=self.city, field_id=field).if_waterworks is True:
#                                 energy_deficit = building.total_production() - building.energy_allocated
#                                 waterworks = WaterTower.objects.get(city=self.city, city_field=field)
#                                 if waterworks.energy == 0:
#                                     if waterworks.energy_required <= energy_deficit:
#                                         waterworks.energy += waterworks.energy_required
#                                         building.energy_allocated += waterworks.energy_required
#                                     else:
#                                         waterworks.energy += energy_deficit
#                                         building.energy_allocated += energy_deficit
#                                 waterworks.save()
#                                 building.save()
#
#     def water_allocation(self):
#         for models in waterworks_buildings:
#             list_of_buildings = models.objects.filter(city=self.city)
#             for building in list_of_buildings:
#                 building.water_allocated = 0
#                 building.save()
#                 pattern = self.create_allocation_pattern(building.city_field.id)
#                 while building.water_allocated < building.total_production():
#                     try:
#                         next_value = next(pattern)
#                     except(StopIteration):
#                         break
#                     for field in next_value:
#                         if CityField.objects.filter(city=self.city, field_id=field):
#                             if CityField.objects.get(city=self.city, field_id=field).if_electricity is True:
#                                 water_deficit = building.total_production() - building.water_allocated
#                                 for electric_building in electricity_buildings:
#                                     if electric_building.objects.filter(city=self.city, city_field=field):
#                                         power_plant = electric_building.objects.get(city=self.city, city_field=field)
#                                         if power_plant.water == 0:
#                                             if power_plant.water_required <= water_deficit:
#                                                 power_plant.water += power_plant.water_required
#                                                 building.water_allocated += power_plant.water_required
#                                             else:
#                                                 power_plant.water += water_deficit
#                                                 building.water_allocated += water_deficit
#                                         power_plant.save()
#                                         building.save()
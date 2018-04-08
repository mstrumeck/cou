from city_engine.models import CityField, waterworks_buildings
from .resources_allocation import ResourceAllocation
from .employee_allocation import EmployeeAllocation
import numpy as np
from .global_variables import HEX_NUM_IN_ROW, HEX_NUM, ROW_NUM
from city_engine.models import WindPlant, electricity_buildings, Residential, ProductionBuilding


def assign_city_fields_to_board(city):
    fields = [x for x in range(1, int(HEX_NUM)+1)]
    chunk_fields = np.array_split(fields, HEX_NUM_IN_ROW)
    for num_of_row, row in enumerate(chunk_fields):
        row = list(row)
        for col in range(len(row)):
            CityField.objects.create(city=city, row=num_of_row, col=col)


class Board(object):

    def __init__(self, city):
        self.hex_table = ''
        self.city = city
        self.hex_with_builds = []
        self.hex_with_electricity = []
        self.hex_with_waterworks = []
        self.hex_with_trashcollector = []
        self.map_board_info()
        self.generate_board()

    def generate_board(self):
        for row in range(ROW_NUM):
            if row % 2 == 0:
                self.hex_table += "<div class='hex-row even'>"
            elif row % 2 != 0:
                self.hex_table += "<div class='hex-row'>"
            for col in range(int(HEX_NUM_IN_ROW)):
                self.hex_table += Hex(row, col, self.hex_with_builds,
                                      self.hex_with_electricity,
                                      self.hex_with_waterworks,
                                      self.hex_with_trashcollector).create()
            self.hex_table += "</div>"

    def map_board_info(self):
        for row in range(int(ROW_NUM)):
            for col in range(int(HEX_NUM_IN_ROW)):
                if CityField.objects.filter(col=col, row=row, city=self.city).exists():
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
                    elif build_field.if_trashcollector is True:
                        self.hex_with_builds.append((row, col))
                        self.hex_with_trashcollector.append((row, col))


class Hex(object):
    def __init__(self, row, col, hex_with_builds, hex_with_electricity, hex_with_waterworks, hex_with_trashcollector):
        self.col = col
        self.row = row
        self.hex_with_builds = hex_with_builds
        self.hex_with_electricity = hex_with_electricity
        self.hex_with_waterworks = hex_with_waterworks
        self.hex_with_trashcollector = hex_with_trashcollector
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
        elif (self.row, self.col) in self.hex_with_trashcollector:
            self.hexagon += "<p>Wysypisko</p>"
        elif (self.row, self.col) in self.hex_with_builds:
            self.hexagon += "<p>Mieszkanie</p>"

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
        for row in range(int(ROW_NUM)):
            for col in range(int(HEX_NUM_IN_ROW)):
                counter += 1
                self.hex_detail_info_table += self.add_hex_detail_box(counter, row, col)
        return self.hex_detail_info_table

    def add_hex_detail_box(self, hex_id, row, col):
        hex_detail_box = "<div class='hexInfoBoxDetail' "
        hex_detail_box += "id='hexBox{}{}'>".format(row, col)
        hex_detail_box += "<p>Podgląd hexa "+str(hex_id)+"</p>"

        if CityField.objects.filter(row=row, col=col, city=self.city).exists():
            build_field = CityField.objects.get(row=row, col=col, city=self.city)
            hex_detail_box += "<p>Zanieczyszczenie: {}</p>".format(build_field.pollution)

            if build_field.if_residential is True:
                residential = Residential.objects.get(city_field=build_field.id, city=self.city)
                hex_detail_box += '<p>Budynek mieszkalny</p>' \
                                  '<p>Populacja: '+str(residential.population)+'</p>'

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
                elif build_field.if_trashcollector is True:
                    hex_detail_box += self.add_trashcollector_details(build)
                # elif build_field.if_residential is True:
                #     hex_detail_box += self.add_residential_details(build)
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

    def add_trashcollector_details(self, build):
        hex_detail_box = ''
        hex_detail_box += '<p>Energia: '+str(build.energy)+'/'+str(build.energy_required)+'</p>'
        return  hex_detail_box

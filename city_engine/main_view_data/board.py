from city_engine.models import CityField, DustCart
import numpy as np
from django.db.models import Sum
from .global_variables import HEX_NUM_IN_ROW, HEX_NUM, ROW_NUM
from city_engine.models import WindPlant, BuldingsWithWorkes, PowerPlant, Waterworks, DumpingGround, Residential, SewageWorks


def assign_city_fields_to_board(city):
    fields = [x for x in range(1, int(HEX_NUM)+1)]
    chunk_fields = np.array_split(fields, HEX_NUM_IN_ROW)
    for num_of_col, col in enumerate(chunk_fields):
        col = list(col)
        for row in range(len(col)):
            CityField.objects.create(city=city, row=row, col=num_of_col)


class Board:

    def __init__(self, city, data):
        self.city = city
        self.data = data
        self.hex_table = ''
        self.generate_board()

    def generate_board(self):
        builds = {(b.city_field.row, b.city_field.col): b for b in self.data.list_of_buildings}
        for row in range(ROW_NUM):
            if row % 2 == 0:
                self.hex_table += "<div class='hex-row even'>"
            elif row % 2 != 0:
                self.hex_table += "<div class='hex-row'>"
            for col in range(int(HEX_NUM_IN_ROW)):
                if (row, col) in builds:
                    self.hex_table += Hex(row, col, builds[(row, col)]).create()
                else:
                    self.hex_table += Hex(row, col).create()
            self.hex_table += "</div>"


class Hex:
    def __init__(self, row, col, instance=None):
        self.col = col
        self.row = row
        self.instance = instance
        self.hexagon = ''

    def create(self):
        self.hexagon = "<div class='hexagon'"
        if self.instance:
            self.hexagon += "v-bind:class='{disabled: isActive }'"
        else:
            self.hexagon += "v-bind:class='{isHexTaken: isActive }'"
        self.hexagon += "v-on:click='getRowCol({}{})' id={}{}".format(self.row, self.col, self.row, self.col)
        self.hexagon += ">"
        self.hexagon += "<div class='hexagon-top'></div>"
        self.hexagon += "<div class='hexagon-middle'>"
        if self.instance:
            self.hexagon += self.instance.name
        self.hexagon += "<p>{},{}</p>".format(self.row, self.col)
        self.hexagon += "</div>"
        self.hexagon += "<div class='hexagon-bottom'></div>"
        self.hexagon += "</div>"
        return self.hexagon


class HexDetail:

    def __init__(self, city,  data):
        self.city = city
        self.data = data
        self.hex_detail_info_table = ''
        self.building_by_corr = {self.data.list_of_buildings[b].row_col_cor: b for b in self.data.list_of_buildings}
        self.city_field_pollution = {self.data.city_fields_in_city[f].row_col: self.data.city_fields_in_city[f].pollution
                                     for f in self.data.city_fields_in_city}
        self.generate_hex_detail()

    def run(self):
        self.generate_hex_detail()

    def generate_hex_detail(self):
        for row in range(int(ROW_NUM)):
            for col in range(int(HEX_NUM_IN_ROW)):
                self.hex_detail_info_table += self.add_hex_detail_box(row, col)
        return self.hex_detail_info_table

    def add_hex_detail_box(self, row, col):
        hex_detail_box = "<div class='hexInfoBoxDetail' "
        hex_detail_box += "id='hexBox{}{}'>".format(row, col)

        if (row, col) in self.building_by_corr:
            build = self.building_by_corr[(row, col)]
            hex_detail_box += "<p>{}</p>".format(build.name)
            hex_detail_box += "<p>Zanieczyszczenie: {}</p>".format(self.city_field_pollution[(row, col)])
            hex_detail_box += '<p>Woda: {}/{}</p>'.format(build.water, build.water_required)
            hex_detail_box += "<p>Energia : {}/{}</p>".format(build.energy, build.energy_required)
            hex_detail_box += "<p>W trakcie budowy: {}</p>".format(build.if_under_construction)
            if isinstance(build, BuldingsWithWorkes):
                build_set = self.data.list_of_buildings[build]
                hex_detail_box += '<p name="detailEmployees">Pracownicy: {}/{}</p>'.format(
                    build_set.people_in_charge, build_set.max_employees
                )
                if isinstance(build, Waterworks):
                    hex_detail_box += self.add_waterworks_details(build)
                elif isinstance(build, PowerPlant):
                    hex_detail_box += self.add_electricity_details(build)
                elif isinstance(build, DumpingGround):
                    hex_detail_box += self.add_trashcollector_details(build)
                elif isinstance(build, Residential):
                    hex_detail_box += '<p>Populacja: {}/{}</p>'.format(build.population, build.max_population)
                elif isinstance(build, SewageWorks):
                    hex_detail_box += self.add_sewage_works_details(build)

        hex_detail_box += "</div>"
        return hex_detail_box

    def add_sewage_works_details(self, build):
        hex_detail_box = ''
        hex_detail_box += '<p>Pompowana czysta woda: {}/{}</p>'.format(build.clean_water_allocated, build.total_production(
            self.data.list_of_buildings,
            self.data.citizens_in_city
        ))
        hex_detail_box += '<p>Przepustowość : {}</p>'.format(build.raw_water_required)
        return hex_detail_box

    def add_electricity_details(self, build):
        hex_detail_box = ''
        hex_detail_box += '<p name="detailEnergy">Produkowana energia: ' + str(build.total_production(
            self.data.list_of_buildings,
            self.data.citizens_in_city
        )) + '</p>'
        hex_detail_box += '<p>Zalokowana energia: ' + str(build.energy_allocated)+'</p>'
        if build is WindPlant:
            hex_detail_box += '<p>Liczba turbin: '
        else:
            hex_detail_box += '<p>Liczba reaktorów: '
            hex_detail_box += str(build.power_nodes)+'/'+str(build.max_power_nodes)+'</p>'
        hex_detail_box += '<p>Śmieci: {}</p>'.format(build.trash.aggregate(Sum('size'))['size__sum'])
        return hex_detail_box

    def add_waterworks_details(self, build):
        hex_detail_box = ''
        hex_detail_box += '<p name="detailWater">Pompowana surowa woda: '+str(build.total_production(
            self.data.list_of_buildings,
            self.data.citizens_in_city
        ))+'</p>'
        hex_detail_box += '<p>Surowa woda zalokowana: '+str(build.raw_water_allocated)+'</p>'
        hex_detail_box += '<p>Śmieci: {}</p>'.format(build.trash.aggregate(Sum('size'))['size__sum'])
        return hex_detail_box

    def add_trashcollector_details(self, build):
        hex_detail_box = ''
        hex_detail_box += '<p>Energia: {}/{}</p>'.format(build.energy, build.energy_required)
        hex_detail_box += '<p>Wysypisko: {}/{}</p>'.format(build.current_space_for_trash, build.max_space_for_trash)
        hex_detail_box += '<p>Lista śmieciarek:</p>'
        for carts in self.data.vehicles:
            if hasattr(carts, 'dumping_ground_id'):
                if carts.dumping_ground == build:
                    cart_set = self.data.vehicles[carts]
                    hex_detail_box += '<p>{}: załoga {}/{}</p>'.format(carts,
                                                                       sum([len(cart_set.elementary_employees),
                                                                            len(cart_set.college_employees),
                                                                            len(cart_set.phd_employees)]),
                                                                       sum([cart_set.elementary_vacancies,
                                                                            cart_set.college_vacancies,
                                                                            cart_set.phd_vacancies])
                                                                       )
        return hex_detail_box
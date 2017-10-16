from city_engine.models import CityField, \
    Residential, \
    ProductionBuilding, \
    WindPlant, \
    City, \
    electricity_buildings, \
    CoalPlant, \
    RopePlant


def assign_city_fields_to_board(city):
    for field_id in range(1, int(Board.HEX_NUM) + 1):
        CityField.objects.create(city=city, field_id=field_id).save()


class Board(object):
    ROW_NUM = 4
    HEX_NUM = 16
    HEX_NUM_IN_ROW = HEX_NUM / ROW_NUM
    hex_with_builds = []
    hex_with_electricity = []
    hex_with_waterworks = []

    def __init__(self, request):
        self.request = request
        self.hex_table = ''
        self.map_board_info()
        self.generate_board()

    def generate_board(self):
        counter = 0
        for row in range(self.ROW_NUM):
            if row % 2 == 0:
                self.hex_table += "<div class='hex-row even'>"
            elif row % 2 != 0:
                self.hex_table += "<div class='hex-row'>"
            for id_number in range(1, int(self.HEX_NUM_IN_ROW) + 1):
                counter += 1
                self.hex_table += Hex(counter).create()
            self.hex_table += "</div>"

    def map_board_info(self):
        counter = 0
        city = City.objects.get(user=self.request.user)
        for row in range(Board.ROW_NUM):
            for id_number in range(1, int(Board.HEX_NUM_IN_ROW) + 1):
                counter += 1
                if CityField.objects.filter(field_id=counter, city=city):
                    build_field = CityField.objects.get(field_id=counter, city=city)
                    if build_field.if_residential is True:
                        Board.hex_with_builds.append(counter)
                    elif build_field.if_production is True:
                        Board.hex_with_builds.append(counter)
                    elif build_field.if_electricity is True:
                        Board.hex_with_builds.append(counter)
                        Board.hex_with_electricity.append(counter)
                    elif build_field.if_waterworks is True:
                        Board.hex_with_builds.append(counter)
                        Board.hex_with_waterworks.append(counter)


class Hex(object):
    def __init__(self, hex_id):
        self.hex_id = hex_id
        self.hexagon = ''

    def create(self):
        self.hexagon = "<div class='hexagon"
        if self.hex_id in Board.hex_with_builds:
            self.hexagon += " build'"
        else:
            self.hexagon += "'"
        self.hexagon += "id=" + str(self.hex_id) + ""
        self.hexagon += ">"
        self.hexagon += "<div class='hexagon-top'></div>"
        self.hexagon += "<div class='hexagon-middle'>"
        if self.hex_id in Board.hex_with_electricity:
            self.hexagon += "<p>Prąd</p>"
        self.hexagon += "</div>"
        self.hexagon += "<div class='hexagon-bottom'></div>"
        self.hexagon += "</div>"
        return self.hexagon


class HexDetail(object):
    def __init__(self, request):
        self.request = request
        self.hex_detail_info_table = ''

    def generate_hex_detail(self):
        counter = 0
        for row in range(Board.ROW_NUM):
            for id_number in range(1, int(Board.HEX_NUM_IN_ROW) + 1):
                counter += 1
                self.hex_detail_info_table += self.add_hex_detail_box(counter)
        return self.hex_detail_info_table

    def add_hex_detail_box(self, hex_id):
        hex_detail_box = "<div class='hexInfoBoxDetail' id='hexBox"+str(hex_id)+"'>" \
                        "<p>Podgląd hexa "+str(hex_id)+"</p>"

        city = City.objects.get(user=self.request.user)
        if CityField.objects.filter(field_id=hex_id, city=city):
            build_field = CityField.objects.get(field_id=hex_id, city=city)

            if build_field.if_residential is True:
                residential = Residential.objects.get(city_field=build_field.id, city=city)
                hex_detail_box += '<p>Budynek mieszkalny</p>' \
                                  '<p>Populacja: '+str(residential.current_population)+'</p>'

            elif build_field.if_production is True:
                production = ProductionBuilding.objects.get(city_field=build_field.id, city=city)
                hex_detail_box += '<p>Budynek produkcyjny</p>' \
                                    '<p>Pracownicy: '+str(production.current_employees)+'/'+str(production.max_employees)+'</p>'

            elif build_field.if_electricity is True:
                hex_detail_box += self.add_electricity_details(build_field, city)

        hex_detail_box += "</div>"
        return hex_detail_box

    def add_electricity_details(self, build_field, city):
        hex_detail_box = ''
        for buildings in electricity_buildings:
            if buildings.objects.filter(city_field=build_field.id, city=city).count() == 1:
                build = buildings.objects.get(city_field=build_field.id, city=city)
                hex_detail_box = '<p>' + str(build.name) + '</p>' \
                    '<p>Pracownicy: ' + str(build.current_employees) + '/' + str(build.max_employees) + '</p>' \
                    '<p>Produkowana energia: ' + str(build.total_energy_production()) + '</p>'
                if buildings is WindPlant:
                    hex_detail_box += '<p>Liczba turbin: '
                else:
                    hex_detail_box += '<p>Liczba reaktorów: '
                hex_detail_box += str(build.power_nodes) + '/' + str(build.max_power_nodes) + '</p>'
        return hex_detail_box



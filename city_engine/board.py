from .models import CityField, Residential, ProductionBuilding, PowerPlant
from django.contrib.auth.models import User

ROW_NUM = 4
HEX_NUM = 16
HEX_NUM_IN_ROW = HEX_NUM/ROW_NUM
hex_with_builds = []


def add_hex_detail_box(hex_id, request):
    hex_detail_box = "<div class='hexInfoBoxDetail' id='hexBox"+str(hex_id)+"'>" \
                    "<p>Podgląd hexa "+str(hex_id)+"</p>"

    if CityField.objects.filter(field_id=hex_id):
        build_field = CityField.objects.get(id=hex_id)
        build_field.refresh_from_db()

        if build_field.if_residential is True:
            hex_with_builds.append(hex_id)
            residential = Residential.objects.get(city_field=build_field.id, user=request.user)
            residential.refresh_from_db()
            hex_detail_box += '<p>Budynek mieszkalny</p>' \
                              '<p>Populacja: '+str(residential.current_population)+'</p>'

        if build_field.if_production is True:
            hex_with_builds.append(hex_id)
            production = ProductionBuilding.objects.get(city_field=build_field.id, user=request.user)
            production.refresh_from_db()
            hex_detail_box += '<p>Budynek produkcyjny</p>' \
                                '<p>Pracownicy: '+str(production.current_employees)+'/'+str(production.max_employees)+'</p>'

        if build_field.if_electricity is True:
            hex_with_builds.append(hex_id)
            electricity = PowerPlant.objects.get(city_field=build_field.id, user=request.user)
            electricity.refresh_from_db()
            hex_detail_box += '<p>'+str(electricity.name)+'</p>' \
                            '<p>Pracownicy: '+str(electricity.current_employees)+'/'+str(electricity.max_employees)+'</p>' \
                            '<p>Produkowana energia: '+str(electricity.total_energy_production())+'</p>'

    hex_detail_box += "</div>"
    return hex_detail_box


def create_hex(hex_id):
    if hex_id in hex_with_builds:
        hexagon = "<div class='hexagon build' id="+str(hex_id)+">"
    else:
        hexagon = "<div class='hexagon' id="+str(hex_id)+">"
    hexagon += "<div class='hexagon-top'></div>"
    hexagon += "<div class='hexagon-middle'></div>"
    hexagon += "<div class='hexagon-bottom'></div>"
    hexagon += "</div>"
    return hexagon

# def add_hex_detail_box(counter):
#     return "<div class='hexInfoBoxDetail' id='hexBox"+str(counter)+"'>" \
#            "<p>Podgląd hexa "+str(counter)+"</p>" \
#                                            "</div>"


def generate_board():
    hex_table = ''
    counter = 0
    for row in range(ROW_NUM):
        if row % 2 == 0:
            hex_table += "<div class='hex-row even'>"
        elif row % 2 != 0:
            hex_table += "<div class='hex-row'>"
        for id_number in range(1, int(HEX_NUM_IN_ROW)+1):
            counter += 1
            hex_table += create_hex(counter)
        hex_table += "</div>"
    return hex_table


def generate_hex_detail(request):
    counter = 0
    hex_detail_info_table = ''
    for row in range(ROW_NUM):
        for id_number in range(1, int(HEX_NUM_IN_ROW) + 1):
            counter += 1
            hex_detail_info_table += add_hex_detail_box(counter, request)
    return hex_detail_info_table

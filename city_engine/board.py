from .models import CityField, Residential, ProductionBuilding

hex_table = ''
hex_detail_info_table = ''
counter = 0
ROW_NUM = 4
HEX_NUM = 16
HEX_NUM_IN_ROW = HEX_NUM/ROW_NUM


def add_counter_to_hex(hex_id):
    return "<div class='hexagon' id="+str(hex_id) + ">" \
    "<div class='hexagon-top'></div>" \
    "<div class='hexagon-middle'></div>" \
    "<div class='hexagon-bottom'></div>" \
    "</div>"


def add_hex_detail_box(hex_id):
    hex_detail_box = "<div class='hexInfoBoxDetail' id='hexBox"+str(hex_id) + "'>" \
                        "<p>Podgląd hexa "+str(hex_id) + "</p>"
    if CityField.objects.all():
        if CityField.objects.filter(field_id=hex_id):
            build_field = CityField.objects.get(id=hex_id)
            if build_field.if_residental is True:
                residential = Residential.objects.get(city_field=build_field.id)
                hex_detail_box += '<p>Jest budynek dla '+str(hex_id)+'</p>' \
                                '<p>Budynek mieszkalny</p>' \
                                '<p>Populacja: '+str(residential.current_population)+'</p>'
            elif build_field.if_production is True:
                production = ProductionBuilding.objects.get(city_field=build_field.id)
                hex_detail_box += '<p>Jest budynek dla ' + str(hex_id) + '</p>' \
                                '<p>Budynek produkcyjny</p>' \
                                '<p>Pracownicy: ' + str(production.current_employees) + '</p>'

    hex_detail_box += "</div>"
    return hex_detail_box


for row in range(ROW_NUM):
    if row % 2 == 0:
        hex_table += "<div class='hex-row even'>"
    elif row % 2 != 0:
        hex_table += "<div class='hex-row'>"
    for id_number in range(1, int(HEX_NUM_IN_ROW)+1):
        counter += 1
        hex_table += add_counter_to_hex(counter)
        hex_detail_info_table += add_hex_detail_box(counter)
    hex_table += "</div>"


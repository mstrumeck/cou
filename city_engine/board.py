hex_table = ''
hex_detail_info_table = ''
counter = 0
ROW_NUM = 4
HEX_NUM = 16
HEX_NUM_IN_ROW = HEX_NUM/ROW_NUM


def add_counter_to_hex(counter):
    return "<div class='hexagon' id="+str(counter)+">" \
    "<div class='hexagon-top'></div>" \
    "<div class='hexagon-middle'></div>" \
    "<div class='hexagon-bottom'></div>" \
    "<div class='detail-hex-info'>" \
        "<h1>Plansza dla hexa nr "+str(counter)+"</h1>" \
        "<button>Zbuduj elektrownie</button>" \
    "</div>" \
    "</div>"


def add_hex_detail_box(counter):
    return "<div class='hexInfoDetail' id='hexBox"+str(counter)+"'>" \
           "<p>Podgląd hexa "+str(counter)+"</p>" \
                                           "</div>"


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


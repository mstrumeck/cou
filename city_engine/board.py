hex_table = ''
counter = 0
ROW_NUM = 4
HEX_NUM = 16
HEX_NUM_IN_ROW = HEX_NUM/ROW_NUM

for row in range(ROW_NUM):
    if row % 2 == 0:
        hex_table += "<div class='hex-row even'>"
    elif row % 2 != 0:
        hex_table += "<div class='hex-row'>"
    for id_number in range(1, int(HEX_NUM_IN_ROW)+1):
        counter += 1
        hex_table += "<div class='hexagon' id=" + str(counter) + ">" \
                                                                     "<div class='hexagon-top'></div>" \
                                                                     "<div class='hexagon-middle'></div>" \
                                                                     "<div class='hexagon-bottom'></div>" \
                                                                     "</div>"
    hex_table += "</div>"

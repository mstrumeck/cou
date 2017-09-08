hex_table = ''
counter = 0

for row in range(4):
    if row % 2 == 0:
        hex_table += "<div class='hex-row even'>"
    elif row % 2 != 0:
        hex_table += "<div class='hex-row'>"
    for id_number in range(1, 5):
        counter += 1
        hex_table += "<div class='hexagon' id=" + str(counter) + ">" \
                                                                     "<div class='hexagon-top'></div>" \
                                                                     "<div class='hexagon-middle'></div>" \
                                                                     "<div class='hexagon-bottom'></div>" \
                                                                     "</div>"
    hex_table += "</div>"

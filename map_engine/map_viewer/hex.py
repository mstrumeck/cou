

class Hex:

    def create(self, field, instance=None):
        if field.terrain:
            hexagon = "<div class='hexagon'>"
            hexagon += "<div class='hexagon-top ht-{}'></div>".format(field.terrain)
            hexagon += "<div class='hexagon-middle hm-{}'>".format(field.terrain)
            if field.resource:
                hexagon += field.resource
            hexagon += "{},{}".format(field.row, field.col)
            hexagon += "</div>"
            hexagon += "<div class='hexagon-bottom hb-{}'></div>".format(field.terrain)
        else:
            hexagon = "<div class='hexagon'"
            if instance:
                hexagon += "v-bind:class='{disabled: isActive }'"
            else:
                hexagon += "v-bind:class='{isHexTaken: isActive }'"
            hexagon += "v-on:click='getRowCol([{},{}])'".format(field.row, field.col)
            hexagon += ">"
            hexagon += "<div class='hexagon-top'></div>"
            hexagon += "<div class='hexagon-middle'>"
            if field.resource:
                hexagon += field.resource
            elif instance:
                hexagon += instance.name
            hexagon += "{},{}".format(field.row, field.col)
            hexagon += "</div>"
            hexagon += "<div class='hexagon-bottom'></div>"

        hexagon += "</div>"
        return hexagon

    def create_blank(self):
        hexagon = "<div class='hexagon'>"
        hexagon += "<div class='hexagon-top empty'></div>"
        hexagon += "<div class='hexagon-middle empty'></div>"
        hexagon += "<div class='hexagon-bottom empty'></div>"
        hexagon += "</div>"
        return hexagon

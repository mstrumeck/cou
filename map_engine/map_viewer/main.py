from .hex import Hex


class HexTable:
    def __init__(self, fields, data=None):
        self.fields = fields
        self.data = data
        self.hex_table = self.create()

    def create(self):
        hex_table = ''
        coordinates = {(f.row, f.col): f for f in self.fields}
        rows = sorted({f.row for f in self.fields if coordinates.get((f.row, f.col))})
        rows_with_col = {row: set([f.col for f in self.fields if coordinates.get((row, f.col))]) for row in rows}
        smallest_col = min([min(rows_with_col[row]) for row in rows_with_col])

        if self.data:
            builds = {
                (b.city_field.row, b.city_field.col): b for b in self.data.list_of_buildings
            }

        for row in rows:
            if row % 2 == 0:
                hex_table += "<div class='hex-row even'>"
            elif row % 2 != 0:
                hex_table += "<div class='hex-row'>"
            sorted_num_of_col = sorted(list(rows_with_col[row]))
            if smallest_col % 2 != 0:
                if sorted_num_of_col[0] > smallest_col or row % 2 != 0:
                    hex_table += Hex().create_blank()
            elif smallest_col % 2 == 0 and sorted_num_of_col[0] > smallest_col:
                if row % 2 != 0:
                    hex_table += Hex().create_blank()
            for col in sorted_num_of_col:
                if self.data and builds.get((row, col)):
                    hex_table += Hex().create(coordinates[(row, col)], builds[(row, col)])
                else:
                    hex_table += Hex().create(coordinates[(row, col)])
            hex_table += "</div>"
        return hex_table

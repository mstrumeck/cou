from .terrain_mapper import TerrainMarker
from cou.global_var import COAL, IRON, URAN, TITAN, MOUNTAIN, FERTILE, SEA
from map_engine.models import Map, Field


class FieldsGenerator:
    def __init__(self, rows, columns):
        self.total_rows = rows
        self.total_columns = columns
        self.fields_coordinates = []
        self.fields_chunks = []

    def generate(self):
        self.generate_all_fields_coordinates()
        self.create_lists_with_quaters()

    def generate_all_fields_coordinates(self):
        for row in range(self.total_rows):
            for col in range(self.total_columns):
                self.fields_coordinates.append((row, col))

    def create_lists_with_quaters(self):
        for quater_map in self.chunks(self.fields_coordinates, int(len(self.fields_coordinates) / 4)):
            for part_of_quater in self.chunks(quater_map, int(len(quater_map) / 6)):
                self.fields_chunks.append(part_of_quater)

    def chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


class MapCreator:
    def __init__(self, rows=106, cols=66):
        self.rows = rows
        self.cols = cols
        fg = FieldsGenerator(self.rows, self.cols)
        fg.generate()
        self.tm = TerrainMarker(self.rows, self.cols, fg.fields_coordinates, fg.fields_chunks)

    def get_resource(self, x, y):
        resources = {
            TITAN: self.tm.titanium_fields,
            COAL: self.tm.coal_fields,
            URAN: self.tm.uranium_fields,
            IRON: self.tm.iron_fields
        }
        for r in resources:
            if (x, y) in resources[r]:
                return r

    def get_terrain(self, x, y):
        terrain = {
            MOUNTAIN: self.tm.mountain_fields,
            FERTILE: self.tm.fertile_fields,
            SEA: self.tm.sea_fields
        }
        for t in terrain:
            if (x, y) in terrain[t]:
                return t

    def create_map(self):
        map = Map.objects.create(rows=self.rows, cols=self.cols)
        self.tm.mark_fields()
        fields = []
        for row in range(1, self.rows):
            for col in range(1, self.cols):
                fields.append(Field.objects.create(
                    map=map,
                    row=row,
                    col=col,
                    terrain=self.get_terrain(row, col),
                    resource=self.get_resource(row, col),
                ))

        starts_places = StartPositionMarker(fields).analyze_player_start_place()
        for f in fields:
            if (f.row, f.col) in starts_places:
                f.if_start = True
                f.save()


class StartPositionMarker:
    def __init__(self, fields):
        self.fields = fields
        self.max_row = max([f.row for f in self.fields])
        self.max_col = max([f.col for f in self.fields])

    def analyze_player_start_place(self):
        coordinates = {(f.row, f.col): f for f in self.fields}
        field_to_iterate = {(f.row, f.col): f for f in self.fields if not f.terrain and not f.resource}
        adequate = []
        taken = []
        for f in field_to_iterate:
            sur = self.field_surrounding(f)
            seas = len([c for c in sur if coordinates[c].terrain == SEA])
            mountains = len([c for c in sur if coordinates[c].terrain == MOUNTAIN])
            sur_taken = len([c for c in sur if c in taken])
            if sur_taken or not 1 <= seas <= 3 or not mountains <= 1 or len(sur) != 18:
                continue
            else:
                for s in sur:
                    taken.append(s)
                adequate.append(f)
                taken.append(f)
        return adequate

    def field_surrounding(self, cor):
        x = cor[0]
        y = cor[1]
        pattern = [
            (x + 1, y),
            (x + 1, y - 1),
            (x, y - 1),
            (x - 1, y),
            (x - 1, y + 1),
            (x, y + 1),
            (x, y - 2),
            (x + 1, y - 2),
            (x + 2, y + 2),
            (x + 2, y - 1),
            (x + 2, y),
            (x + 1, y + 1),
            (x, y + 2),
            (x - 1, y + 2),
            (x - 2, y + 2),
            (x - 2, y + 1),
            (x - 2, y),
            (x - 1, y - 1),
                ]
        return [
            sur
            for sur in pattern
            if (sur[0] >= 1 and sur[0] <= self.max_row)
               and (sur[1] >= 1 and sur[1] <= self.max_col)
        ]


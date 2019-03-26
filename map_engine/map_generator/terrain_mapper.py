import random
from .terrain_markers import Fertile, BasicTerrainMarker, SinglePointMarker, Sea


class TerrainMarker:
    def __init__(self, rows_in_maps, cols_in_maps, all_fields, fields_chunks):
        self.rows = rows_in_maps
        self.cols = cols_in_maps
        self.all_fields = all_fields
        self.fields_chunks = fields_chunks

        self.sea_fields = []
        self.mountain_fields = []
        self.fertile_fields = []
        self.rope_fields = []
        self.uranium_fields = []
        self.coal_fields = []
        self.iron_fields = []
        self.titanium_fields = []
        self.geothermal_fields = []

        self.taken_fields = []
        self.taken_by_resource = []

        self.terrain_marker_roadmap = {
            'sea': {'list_of_fields': self.sea_fields, 'num_of_marks': int(rows_in_maps / 8) or 1, 'marker': Sea},
            'mountain': {'list_of_fields': self.mountain_fields, 'num_of_marks': int(rows_in_maps / 20) or 1, 'marker': BasicTerrainMarker},
            'fertile': {'list_of_fields': self.fertile_fields, 'num_of_marks': int(rows_in_maps / 5) or 1, 'marker': Fertile}}

        self.resource_marker_roadmap = {
            'coal': {'list_of_fields': self.coal_fields, 'num_of_marks': 4, 'marker': SinglePointMarker},
            'iron': {'list_of_fields': self.iron_fields, 'num_of_marks': 4, 'marker': SinglePointMarker},
            'titanium': {'list_of_fields': self.titanium_fields, 'num_of_marks': 3, 'marker': SinglePointMarker},
            'uranium': {'list_of_fields': self.uranium_fields, 'num_of_marks': 1, 'marker': SinglePointMarker},
        }

    def mark_fields(self):
        for terrain_type in self.terrain_marker_roadmap:
            tt = self.terrain_marker_roadmap[terrain_type]
            self.mark_type_of_terrain(tt['num_of_marks'], tt['marker'], tt['list_of_fields'])

        for resource_type in self.resource_marker_roadmap:
            tt = self.resource_marker_roadmap[resource_type]
            self.mark_type_of_resource(tt['num_of_marks'], tt['marker'], tt['list_of_fields'])

    def mark_type_of_terrain(self, num_of_marks, marker, list_of_fields):
        for _ in range(num_of_marks):
            for q in self.fields_chunks:
                field = random.choice(q)
                while field in self.taken_fields and len(q) > 10:
                    field = random.choice(q)

                for mark_field in marker(field[0], field[1], self.rows, self.cols, self.taken_fields).run():
                    list_of_fields.append(mark_field)
                    self.taken_fields.append(mark_field)

    def mark_type_of_resource(self, num_of_marks, marker, list_of_fields):
        for _ in range(num_of_marks):
            for q in self.fields_chunks:
                field = random.choice(q)
                m = marker(field[0], field[1], self.rows, self.cols, self.taken_by_resource)
                while field in self.taken_by_resource and len(q) > 10 or len(set(m.total_surrounding) & set(self.taken_by_resource)) > 0:
                    field = random.choice(q)
                    m = marker(field[0], field[1], self.rows, self.cols, self.taken_by_resource)

                for mark_field in m.run():
                    list_of_fields.append(mark_field)
                    self.taken_by_resource.append(mark_field)
                self.taken_fields.append(field)

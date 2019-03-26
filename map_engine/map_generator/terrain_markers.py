import random


class BasicTerrainMarker:
    def __init__(self, x, y, rows, cols, taken_fields):
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.taken_fields = taken_fields
        self.builder_strategies = ['self.single_point()', 'self.big_hexagon()', 'self.irregular()']

    def run(self):
        return eval(random.choice(self.builder_strategies))

    def field_surrounding(self):
        pattern = [
            (self.x + 1, self.y - 1),
            (self.x + 1, self.y),
            (self.x + 1, self.y + 1),
            (self.x, self.y - 1),
            (self.x, self.y + 1),
            (self.x - 1, self.y - 1),
            (self.x - 1, self.y),
            (self.x - 1, self.y + 1),
        ]
        return [
            sur for sur in pattern if (sur[0] >= 0 and sur[0] <= self.rows) and (sur[1] >= 0 and sur[1] <= self.cols)
        ]

    def single_point(self):
        return [(self.x, self.y)]

    def big_hexagon(self):
        return [*self.single_point(), *self.field_surrounding()]

    def irregular(self):
        fields = []
        l = random.randrange(5)
        for _ in range(l):
            try:
                fields.append(random.choice([s for s in self.field_surrounding() if s not in self.taken_fields]))
            except IndexError:
                continue
        return fields


class SinglePointMarker(BasicTerrainMarker):
    def __init__(self, x, y, rows, cols, taken_fields):
        super().__init__(x, y, rows, cols, taken_fields)
        self.builder_strategies = ['self.single_point()']
        self.surrounding = self.field_surrounding()
        self.far_surrounding = self.field_for_landing()
        self.total_surrounding = self.surrounding + self.far_surrounding

    def field_for_landing(self):
        container = []
        for line in self.field_surrounding_for_landing():
            for field in line:
                container.append(field)
        return container

    def field_surrounding(self):
        return [
            (self.x + 1, self.y),
            (self.x + 1, self.y - 1),
            (self.x, self.y - 1),
            (self.x - 1, self.y),
            (self.x - 1, self.y + 1),
            (self.x, self.y + 1)
        ]

    def field_surrounding_for_landing(self):
        return [[
            (self.x + inc, self.y),
            (self.x + inc, self.y - inc),
            (self.x, self.y - inc),
            (self.x - inc, self.y),
            (self.x - inc, self.y + inc),
            (self.x, self.y + inc)] for inc in range(1, 3)]


class Sea(BasicTerrainMarker):
    def __init__(self, x, y, rows, cols, taken_fields):
        super().__init__(x, y, rows, cols, taken_fields)
        self.builder_strategies = ['self.big_hexagon()', 'self.irregular()']


class Fertile(BasicTerrainMarker):
    def __init__(self, x, y, rows, cols, taken_fields):
        super().__init__(x, y, rows, cols, taken_fields)
        self.builder_strategies = ['self.single_point()']

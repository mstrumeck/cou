

class TempField:
    def __init__(self, instance):
        self.instance = instance
        self.row_col = (instance.row, instance.col)
        self.pollution = 0.0

from city_engine.main_view_data.global_variables import HEX_NUM_IN_ROW
from random import shuffle


class AllocationPattern(object):

    def create_allocation_pattern(self, row, col):
        first_alloc = []
        for hex_in_row in range(1, int(HEX_NUM_IN_ROW+1)):
            allocation_pattern = [
                (row - hex_in_row, col),
                (row - hex_in_row, col + hex_in_row),
                (row + hex_in_row, col),
                (row + hex_in_row, col + hex_in_row),
                (row, col - hex_in_row),
                (row, col + hex_in_row)
            ]
            for calculations in allocation_pattern:
                if calculations[0] >= 0 or calculations[1] >= 0:
                    first_alloc.append(calculations)
            shuffle(first_alloc)
            yield first_alloc
            first_alloc = []
            yield self.return_next_alloc(hex_in_row, hex_in_row+1, row, col)

    def return_next_alloc(self, hex_in_row, wave, row, col):
        allocation = []
        allocation_pattern = [
            (row + hex_in_row, col - hex_in_row + wave),
            (row + hex_in_row, col + hex_in_row - wave),
            (row - hex_in_row, col + hex_in_row - wave),
            (row - hex_in_row, col - hex_in_row + wave)
        ]
        for calculation in allocation_pattern:
            if calculation[0] >= 0 or calculation[1] >= 0:
                allocation.append(calculation)
        shuffle(allocation)
        return allocation

    def return_first_allocation(self, row, col):
        alloc = []
        hex_in_row = 1
        allocation_pattern = [
            (row - hex_in_row, col),
            (row - hex_in_row, col + hex_in_row),
            (row + hex_in_row, col),
            (row + hex_in_row, col + hex_in_row),
            (row, col - hex_in_row),
            (row, col + hex_in_row)
        ]
        for calculations in allocation_pattern:
            if calculations[0] >= 0 or calculations[1] >= 0:
                alloc.append(calculations)
        shuffle(alloc)
        return alloc
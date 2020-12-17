
class Cell():
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.exhausted = False  # Flag to check if we have tried all numbers
        self.number = 0  # Initial number
        self.possible_numbers = set()

    def try_new_number(self):
        self.set_number(self.possible_numbers.pop())
        self.exhausted = not self.possible_numbers

    def set_possible_numbers(self, numbers):
        self.possible_numbers = numbers
        self.exhausted = not numbers

    def reset_number(self):
        self.set_number(0)

    def set_number(self, number):
        self.number = number

    def reset(self):
        # Reset this cell completely
        self.exhausted = False
        self.possible_numbers = set()
        self.set_number(0)


class Board():
    def __init__(self):
        # Initialize a 9x9 matrix of Cell objects
        self.board = [[Cell(r, c) for c in range(9)] for r in range(9)]

    @staticmethod
    def __difference(numbers):
        # Get the remaining usable Sudoku numbers given a list of numbers
        return set(range(1, 10)) - set(numbers)

    @staticmethod
    def __validate(numbers):
        numbers = list(filter(lambda n: n != 0, numbers))  # remove all 0s
        correct_numbers = set(numbers).issubset(set(range(1, 10)))
        no_duplicates = len(numbers) == len(set(numbers))
        return correct_numbers and no_duplicates

    def __get_row(self, row):
        return [cell.number for cell in self.board[row]]

    def __get_column(self, column):
        return [self.board[row][column].number for row in range(9)]

    def __get_square(self, row, column):
        return [
            self.board[r][c].number
            for r in range(row - (row % 3), row + (3 - (row % 3)))
            for c in range(column - (column % 3), column + (3 - (column % 3)))
        ]

    def is_valid(self):
        columns = [self.__validate(self.__get_column(column))
                   for column in range(9)]
        rows = [self.__validate(self.__get_row(r))
                for r in range(9)]
        squares = [
            self.__validate(self.__get_square(row, column))
            for row in range(0, 9, 3)
            for column in range(0, 9, 3)
        ]
        return all(columns + rows + squares)

    def possible_numbers(self, r, c):
        row = self.__get_row(r)
        column = self.__get_column(c)
        square = self.__get_square(r, c)
        return self.__difference(row + column + square)

    def clear(self):
        [self.board[r][c].reset() for c in range(9) for r in range(9)]
